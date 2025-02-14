import torch
import numpy as np
import matplotlib.pyplot as plt
from types import SimpleNamespace
import logging

# ----------------------------
# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ----------------------------
# 더미 헬퍼 함수들

def get_lin_function(y1, y2):
    """x에 대해 y를 선형으로 매핑하는 함수 반환 (예: 0~1000 범위)."""
    def f(x):
        return y1 + (y2 - y1) * (x / 1000.0)
    return f

def time_shift(mu, sigma, timesteps):
    """flux_shift 방식의 시간 변환 (여기서는 간단하게 mu를 곱하는 방식)."""
    return timesteps * mu

def compute_density_for_timestep_sampling(weighting_scheme, batch_size, logit_mean, logit_std, mode_scale):
    """fallback 분기에서 균일한 분포의 값을 반환."""
    return torch.rand(batch_size)

def get_sigmas(noise_scheduler, timesteps, device, n_dim, dtype):
    """
    fallback 분기에서 timesteps 값을 0~1 범위로 스케일하여 sigma 값을 계산.
    timesteps는 0~1000 사이의 값이라고 가정.
    """
    sigma = (timesteps / noise_scheduler.config.num_train_timesteps)
    sigma = sigma.view(-1, *([1] * (n_dim - 1)))
    return sigma.to(dtype)

# ----------------------------
# Dummy Noise Scheduler

class DummyConfig:
    def __init__(self, shift=1.0, num_train_timesteps=1000):
        self.shift = shift
        self.num_train_timesteps = num_train_timesteps

class DummyNoiseScheduler:
    def __init__(self, device, num_train_timesteps=1000):
        self.config = DummyConfig(shift=1.0, num_train_timesteps=num_train_timesteps)
        self.device = device
        # 0부터 num_train_timesteps-1까지 균일하게 분포한 타임스텝 생성
        self.timesteps = torch.linspace(0, num_train_timesteps - 1, steps=num_train_timesteps, device=device)
    
    def set_timesteps(self, num_inference_steps, device):
        # 추론 시 사용할 타임스텝 배열 재생성
        self.timesteps = torch.linspace(0, self.config.num_train_timesteps - 1, steps=num_inference_steps, device=device)

# ----------------------------
# 제공해주신 get_noisy_model_input_and_timesteps 함수

def get_noisy_model_input_and_timesteps(
    args, noise_scheduler, latents, noise, device, dtype, global_step
):
    bsz, _, h, w = latents.shape
    sigmas = None

    if hasattr(args, "timestep_se_steps") and args.timestep_se_steps is not None:
        if global_step < args.timestep_se_steps:
            ratio = global_step / args.timestep_se_steps
            current_shift = (1 - ratio) * args.discrete_flow_shift + ratio * args.timestep_e_shift
        else:
            current_shift = args.timestep_e_shift
    else:
        # 고정 shift 사용.
        current_shift = args.discrete_flow_shift
    logger.info(f"step: {global_step}, current_shift: {current_shift}")

    noise_scheduler.config.shift = current_shift
    noise_scheduler.set_timesteps(num_inference_steps=1000, device=device)

    if args.timestep_sampling == "uniform" or args.timestep_sampling == "sigmoid":
        # 간단한 t 기반 노이즈 샘플링
        if args.timestep_sampling == "sigmoid":
            t = torch.sigmoid(args.sigmoid_scale * torch.randn((bsz,), device=device))
        else:
            t = torch.rand((bsz,), device=device)

        # shift 변환 적용
        t = (t * current_shift) / (1 + (current_shift - 1) * t)

        timesteps = t * 1000.0
        t = t.view(-1, 1, 1, 1)
        noisy_model_input = (1 - t) * latents + t * noise

    elif args.timestep_sampling == "shift":
        shift = args.discrete_flow_shift
        logits_norm = torch.randn(bsz, device=device)
        logits_norm = logits_norm * args.sigmoid_scale
        timesteps = logits_norm.sigmoid()
        timesteps = (timesteps * shift) / (1 + (shift - 1) * timesteps)

        t = timesteps.view(-1, 1, 1, 1)
        timesteps = timesteps * 1000.0
        noisy_model_input = (1 - t) * latents + t * noise

    elif args.timestep_sampling == "flux_shift":
        logits_norm = torch.randn(bsz, device=device)
        logits_norm = logits_norm * args.sigmoid_scale
        timesteps = logits_norm.sigmoid()

        # shift 변환 적용
        timesteps = (timesteps * current_shift) / (1 + (current_shift - 1) * timesteps)

        mu = get_lin_function(y1=0.5, y2=1.15)((h // 2) * (w // 2))
        timesteps = time_shift(mu, 1.0, timesteps)

        t = timesteps.view(-1, 1, 1, 1)
        timesteps = timesteps * 1000.0
        noisy_model_input = (1 - t) * latents + t * noise

    else:
        # weighting_scheme에 따른 비균일 샘플링
        u = compute_density_for_timestep_sampling(
            weighting_scheme=args.weighting_scheme,
            batch_size=bsz,
            logit_mean=args.logit_mean,
            logit_std=args.logit_std,
            mode_scale=args.mode_scale,
        )
        indices = (u * noise_scheduler.config.num_train_timesteps).long()
        timesteps = noise_scheduler.timesteps[indices].to(device=device)

        # flow matching에 따른 노이즈 추가
        sigmas = get_sigmas(noise_scheduler, timesteps, device, n_dim=latents.ndim, dtype=dtype)
        noisy_model_input = sigmas * noise + (1.0 - sigmas) * latents

    return noisy_model_input.to(dtype), timesteps.to(dtype), sigmas

# ----------------------------
# global_step=100일 때 timestep 분포를 수집하고 시각화하는 함수

def simulate_timestep_distribution_at_global_step(global_step=100, n_batches=1000):
    """
    동일한 입력(latents, noise)으로 여러 번 get_noisy_model_input_and_timesteps()를 호출하여,
    global_step=100일 때 선택되는 timestep 값의 분포를 확인합니다.
    """
    device = "cpu"
    dtype = torch.float32
    bsz = 128  # 배치 사이즈 (각 배치마다 bsz개의 timestep이 선택됨)
    h, w = 32, 32  # 이미지 크기

    # 더미 latent와 noise 텐서를 생성
    latents = torch.randn(bsz, 3, h, w, device=device)
    noise = torch.randn(bsz, 3, h, w, device=device)

    # 필요한 인자들을 담은 args 생성
    args = SimpleNamespace(
        timestep_se_steps=100,         # 예: 100 스텝까지 동적 shift 적용
        discrete_flow_shift=3.5,       # 초기 shift 값
        timestep_e_shift=1.0,          # 100 스텝 이상부터 적용될 shift 값
        timestep_sampling="sigmoid",   # "uniform", "sigmoid", "shift", "flux_shift" 등 선택 가능
        sigmoid_scale=1.0,
        weighting_scheme="default",
        logit_mean=0.0,
        logit_std=1.0,
        mode_scale=1.0,
    )

    # Dummy noise scheduler 생성
    noise_scheduler = DummyNoiseScheduler(device=device, num_train_timesteps=1000)
    
    # 여러 번 호출하여 timestep 값을 수집 (전체 배치의 timestep 값 분포)
    all_timesteps = []
    for _ in range(n_batches):
        _, timesteps, _ = get_noisy_model_input_and_timesteps(
            args, noise_scheduler, latents, noise, device, dtype, global_step
        )
        # timesteps가 (bsz,) 혹은 (bsz, 1, 1, 1)일 수 있으므로 flatten
        all_timesteps.append(timesteps.detach().cpu().numpy().flatten())
    
    all_timesteps = np.concatenate(all_timesteps)
    
    # 히스토그램으로 분포 시각화 (0~1000 범위)
    plt.figure(figsize=(8, 6))
    plt.hist(all_timesteps, bins=50, range=(0, 1000), color='skyblue', edgecolor='black')
    plt.xlabel("Timestep")
    plt.ylabel("Frequency")
    plt.title(f"Timestep Distribution at Global Step {global_step}")
    plt.show()

if __name__ == "__main__":
    simulate_timestep_distribution_at_global_step(global_step=100, n_batches=1000)
