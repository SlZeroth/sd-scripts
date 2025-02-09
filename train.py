def run_kohya_train(train_args, dataset_args):
    import subprocess
    def create_dataset_config(input_dataset_args):
        import toml
        config = {
            "general": {
                "flip_aug": False,
                "color_aug": False,
                "keep_tokens_separator": "|||",
                "shuffle_caption": False,
                "caption_tag_dropout_rate": 0,
                "caption_extension": ".txt",
                "min_bucket_reso": 128,
                "max_bucket_reso": 2048
            },
            "datasets": [
                {
                    "batch_size": 1,
                    "enable_bucket": True,
                    "resolution": [1024, 1024],
                    "subsets": [
                        {
                            "image_dir": "face_image",
                            "num_repeats": 10,
                            "is_reg": False
                        }

                        # {
                        #     "image_dir": "J:/train/Aric/img/3_Aric tattoo", 
                        #     "num_repeats": 3,
                        #     "is_reg": False
                        # },
                        # {
                        #     "image_dir": "J:/train/reg/1_regshirt",
                        #     "num_repeats": 1,
                        #     "is_reg": True
                        # }
                    ]
                }
            ]
        }
        with open("config.toml", "w") as f:
            toml.dump(config, f)

    create_dataset_config(dataset_args)
    
    cmd = [
        "accelerate", "launch",
        "--num_processes", "1",
        "--main_process_port", "23333",
        "flux_train_network.py",
        "--pretrained_model_name_or_path", "D:\\diffusion-models\\FLUX.1-dev\\flux1-dev.safetensors",
        "--clip_l", "D:\\diffusion-models\\FLUX.1-dev\\clip_l.safetensors",
        "--t5xxl", "D:\\diffusion-models\\FLUX.1-dev\\t5xxl_fp16.safetensors",
        "--ae", "D:\\diffusion-models\\FLUX.1-dev\\ae.safetensors",
        "--cache_latents_to_disk",
        "--save_model_as", "safetensors",
        "--sdpa",
        "--persistent_data_loader_workers",
        "--max_data_loader_n_workers", "2", 
        "--seed", "42",
        "--gradient_checkpointing",
        "--mixed_precision", "bf16",
        "--save_precision", "bf16",
        "--network_module", "networks.lora_flux",
        "--network_dim", "32",
        "--network_train_unet_only",
        "--optimizer_type", "adamw",
        "--learning_rate", "3e-3",
        "--lr_scheduler", "cosine",
        "--full_bf16",
        "--cache_text_encoder_outputs",
        "--cache_text_encoder_outputs_to_disk",
        "--sigmoid_scale", "1.0",
        "--model_prediction_type", "raw",
        "--highvram",
        "--max_train_epochs", "8",
        "--save_every_n_epochs", "1",
        "--output_dir", "flux-lora-models",
        "--output_name", "flux-lora",
        "--timestep_sampling", "sigmoid",
        "--discrete_flow_shift", "3.0",
        "--model_prediction_type", "raw",
        "--guidance_scale", "1.0",
        "--dataset_config", "config.toml",
        "--timestep_se_steps", "300",
        "--timestep_e_shift", "1.15",
    ]


    import shlex
    import re

    command = " ".join(cmd)
    print(command)

    import os
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE, 
        stderr=subprocess.STDOUT,
        universal_newlines=True, 
        bufsize=1, 
        encoding='utf-8',
        env=env
    )

    progress_pattern = re.compile(r'steps:\s*(\d+)%')

    for line in iter(process.stdout.readline, ''):
        print(line)
        # match = progress_pattern.search(line)
        # if match:
        #     percentage = match.group(1)
        #     # print(f"현재 진행률: {percentage}%")
        # else:
        #     print(line, end='')

    process.stdout.close()
    return_code = process.wait()

    return return_code

run_kohya_train({}, {
    'num_repeats': 10,
    'train_image_path': 'train_images/sks'
})