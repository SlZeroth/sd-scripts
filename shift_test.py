import torch
import matplotlib.pyplot as plt

# 더미 인자 객체 생성
class DummyArgs:
    pass

# args 설정
args = DummyArgs()
args.timestep_sampling = "sigmoid"   # 또는 "sigmoid", "shift" 등 원하는 방식으로 선택
args.discrete_flow_shift = 3.0         # 초기 shift 값
args.timestep_e_shift = 0.7            # 최종 shift 값로 이동
args.timestep_se_steps = None           # 동적 shift가 진행될 스텝 수 (없으면 None으로 설정)
args.sigmoid_scale = 1.0               # sigmoid 스케일

# noise_scheduler는 사용되지 않으므로 None으로 둡니다.
noise_scheduler = None

# 실행 환경 및 데이터 설정
device = torch.device("cpu")
dtype = torch.float32

# 더미 latents와 noise 생성 (예시로 1 x 3 x 64 x 64 텐서)
bsz = 1
channels = 3
height = 64
width = 64
latents = torch.randn(bsz, channels, height, width, device=device, dtype=dtype)
noise = torch.randn_like(latents)

def get_noisy_model_input_and_timesteps(args, noise_scheduler, latents, noise, device, dtype, global_step):
    """
    global_step에 따라 current_shift 값을 동적 또는 고정으로 결정한 후,
    timestep_sampling 방식에 따라 t 값을 샘플링하고 shift를 적용하여 noisy_model_input과 timesteps를 반환합니다.
    추가로 current_shift도 반환하여 시뮬레이션 결과 확인에 사용합니다.
    """
    bsz, _, h, w = latents.shape
    sigmas = None

    # 동적 shift 적용: timestep_se_steps가 지정되어 있으면 선형 보간, 아니면 고정 shift 사용.
    if hasattr(args, "timestep_se_steps") and args.timestep_se_steps is not None:
        if global_step < args.timestep_se_steps:
            ratio = global_step / args.timestep_se_steps
            current_shift = (1 - ratio) * args.discrete_flow_shift + ratio * args.timestep_e_shift
        else:
            current_shift = args.timestep_e_shift
    else:
        current_shift = args.discrete_flow_shift

    noise_scheduler.config.shift = current_shift

    if args.timestep_sampling == "uniform" or args.timestep_sampling == "sigmoid":
        # 간단한 t 기반 노이즈 샘플링
        if args.timestep_sampling == "sigmoid":
            # 예시: https://github.com/XLabs-AI/x-flux/tree/main
            t = torch.sigmoid(args.sigmoid_scale * torch.randn((bsz,), device=device))
        else:
            t = torch.rand((bsz,), device=device)

        # shift 변환 적용: t 값에 current_shift를 반영
        t = (t * current_shift) / (1 + (current_shift - 1) * t)
        timesteps = t * 1000.0  # 예를 들어, 0~1 범위의 t를 0~1000 범위로 스케일링
        t = t.view(-1, 1, 1, 1)
        noisy_model_input = (1 - t) * latents + t * noise

    elif args.timestep_sampling == "shift":
        # Gaussian 노이즈 후 sigmoid 적용
        logits_norm = torch.randn(bsz, device=device)
        logits_norm = logits_norm * args.sigmoid_scale  # 더 균등하게 샘플링하기 위해 scale 조정
        timesteps = logits_norm.sigmoid()

        # shift 변환 적용
        timesteps = (timesteps * current_shift) / (1 + (current_shift - 1) * timesteps)
        t = timesteps.view(-1, 1, 1, 1)
        timesteps = timesteps * 1000.0
        noisy_model_input = (1 - t) * latents + t * noise

    return noisy_model_input, timesteps, sigmas, current_shift

if __name__ == '__main__':
    # global_step에 따른 current_shift 변화를 시뮬레이션합니다.
    global_steps = list(range(0, 350, 10))  # 0, 10, 20, ... 340
    shifts = []

    print("Global step 별 current_shift 값:")
    for gs in global_steps:
        _, ts, _, current_shift = get_noisy_model_input_and_timesteps(
            args, noise_scheduler, latents, noise, device, dtype, gs
        )
        shifts.append(current_shift)
        print(f"Global step: {gs:3d}, Current shift: {current_shift:.4f}")

    # current_shift 변화 플롯
    plt.figure(figsize=(8, 4))
    plt.plot(global_steps, shifts, marker='o')
    plt.xlabel('Global Step')
    plt.ylabel('Current Shift')
    plt.title('Dynamic Shift over Global Steps')
    plt.grid(True)
    plt.show()
