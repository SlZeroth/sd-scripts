import requests
import json

url = "https://www.krea.ai/api/jobs/v2/new/lora"

headers = {
    "accept": "*/*",
    "accept-language": "ko-KR,ko;q=0.9,zh-MO;q=0.8,zh;q=0.7,vi-VN;q=0.6,vi;q=0.5,ja-JP;q=0.4,ja;q=0.3,en-US;q=0.2,en;q=0.1",
    "baggage": "sentry-environment=production,sentry-release=f3522e0181974cc3a516527eecec4804,sentry-public_key=10ac8a6039a5c139d921588be6336824,sentry-trace_id=8067293bd8cd415396fd17e75c0e6785",
    # requests를 사용할 경우 Content-Type은 files 파라미터에 의해 자동 설정됩니다.
    "priority": "u=1, i",
    "sec-ch-ua": "\"Not A(Brand\";v=\"8\", \"Chromium\";v=\"132\", \"Google Chrome\";v=\"132\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "sentry-trace": "8067293bd8cd415396fd17e75c0e6785-8e58841703f07c43",
    "cookie": "session_affinity=1738667656.149.109495.92533|937665b7b38e2dca082499f855c6f8cf; sb-superb-auth-token.0=%7B%22access_token%22%3A%22eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlZDhkZTNiMC00MzU1LTQ3NzYtODNjOC02MDMzZmZkYzY1MDAiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzM5MjA2MjQ3LCJpYXQiOjE3MzkyMDI2NDcsImVtYWlsIjoicWtyd25ja3M1OTNAZ21haWwuY29tIiwicGhvbmUiOiIiLCJhcHBfbWV0YWRhdGEiOnsicHJvdmlkZXIiOiJnb29nbGUiLCJwcm92aWRlcnMiOlsiZ29vZ2xlIl19LCJ1c2VyX21ldGFkYXRhIjp7ImF2YXRhcl91cmwiOiJodHRwczovL2xoMy5nb29nbGV1c2VyY29udGVudC5jb20vYS9BQ2c4b2NKbmpwVGRkUmlLX2FJOVBKd1lBVWJfeGNScFoxa04xZDQ4bUpmMkU3Sm5yUk1ZUDVtej1zOTYtYyIsImVtYWlsIjoicWtyd25ja3M1OTNAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsImZ1bGxfbmFtZSI6InBhcmsga3J3IiwiaXNzIjoiaHR0cHM6Ly9hY2NvdW50cy5nb29nbGUuY29tIiwibmFtZSI6InBhcmsga3J3IiwicGhvbmVfdmVyaWZpZWQiOmZhbHNlLCJwaWN0dXJlIjoiaHR0cHM6Ly9saDMuZ29vZ2xldXNlcmNvbnRlbnQuY29tL2EvQUNnOG9jSm5qcFRkZFJpS19hSTlQSndZQVViX3hjUnBaMWtOMWQ0OG1KZjJFN0puclJNWVA1bXo9czk2LWMiLCJwcm92aWRlcl9pZCI6IjEwMTc5MDM1NDA0Mzc0ODAyOTEwNiIsInN1YiI6IjEwMTc5MDM1NDA0Mzc0ODAyOTEwNiJ9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6Im9hdXRoIiwidGltZXN0YW1wIjoxNzM3Njg1NzA0fV0sInNlc3Npb25faWQiOiJkNTIzYWNlYS0wMzU1LTRmNDktYWFjYy1kMzUwNzM5ZTA3ODYiLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.YxU9OGVlGLH8Jnd_apogoWz50gz2GK0l-Hl4RyEAzyM%22%2C%22token_type%22%3A%22bearer%22%2C%22expires_in%22%3A3600%2C%22expires_at%22%3A1739206247%2C%22refresh_token%22%3A%22Dy7_Kkb8fjRokauJgSmDpA%22%2C%22user%22%3A%7B%22id%22%3A%22ed8de3b0-4355-4776-83c8-6033ffdc6500%22%2C%22aud%22%3A%22authenticated%22%2C%22role%22%3A%22authenticated%22%2C%22email%22%3A%22qkrwncks593%40gmail.com%22%2C%22email_confirmed_at%22%3A%222025-01-24T02%3A28%3A22.648784Z%22%2C%22phone%22%3A%22%22%2C%22confirmed_at%22%3A%222025-01-24T02%3A28%3A22.648784Z%22%2C%22last_sign_in_at%22%3A%222025-01-26T08%3A02%3A52.986849Z%22%2C%22app_metadata%22%3A%7B%22provider%22%3A%22google%22%2C%22providers%22%3A%5B%22google%22%5D%7D%2C%22user_metadata%22%3A%7B%22avatar_url%22%3A%22https%3A%2F%2Flh3.googleusercontent.com%2Fa%2FACg8ocJnjpTddRiK_aI9PJwYAUb_xcRpZ1kN1d48mJf2E7JnrRMYP5mz%3Ds96-c%22%2C%22email%22%3A%22qkrwncks593%40gmail.com%22%2C%22email_verified%22%3Atrue%2C%22full_name%22%3A%22park%20krw%22%2C%22iss%22%3A%22https%3A%2F%2Faccounts.google.com%22%2C%22name%22%3A%22park%20krw%22%2C%22phone_verified%22%3Afalse%2C%22picture%22%3A%22https%3A%2F%2Flh3.googleusercontent.com%2Fa%2FACg8ocJnjpTddRiK_aI9PJwYAUb_xcRpZ1kN1d48mJf2E7JnrRMYP5mz%3Ds96-c%22%2C%22provider_id%22%3A%22101790354043748029106%22%2C%22sub%22%3A%22101790354043748029106%22%7D%2C%22identities%22%3A%5B%7B%22identity_id%22%3A%22b2e42e94-d879-45fb-b3c3-13e6280da6bd%22%2C%22id%22%3A%22101790354043748029106%22%2C%22user_id%22%3A%22ed8de3b0-4355-4776-83c8-6033ffdc6500%22%2C%22identity_data%22%3A%7B%22avatar_url%22%3A%22https%3A%2F%2Flh3.googleusercontent.com%2Fa%2FACg8ocJnjpTddRiK_aI9PJwYAUb_xcRpZ1kN1d48mJf2E7JnrRMYP5mz%3Ds96-c%22%2C%22email%22%3A%22qkrwncks593%40gmail.com%22%2C%22email_verified%22%3Atrue%2C%22full_name%22%3A%22park%20krw%22%2C%22iss%22%3A%22https%3A%2F%2Faccounts.google.com%22%2C%22name%22%3A%22park%20krw%22%2C%22phone_verified%22%3Afalse%2C%22picture%22%3A%22https%3A%2F%2Flh3.googleusercontent.com%2Fa%2FACg8ocJnjpTddRiK_aI9PJwYAUb_xcRpZ1kN1d48mJf2E7JnrRMYP5mz%3Ds96-c%22%2C%22provider_id%22%3A%22101790354043748029106%22%2C%22sub%22%3A%22101790354043748029106%22%7D%2C%22provider%22%3A%22google%22%2C%22last_sign_in_at%22%3A%222025-01-24T02%3A28%3A22.632868Z%22%2C%22created_at%22%3A%222025-01-24T02%3A28%3A22.632913Z%22%2C%22updated_at%22%3A%222025-01-26T08%3A02%3A51.803931Z%22%2C%22email%22%3A%22qkrwncks593%40gmail.com%22%7D%5D%2C%22created_at%22%3A%222025-01-24T02%3A28%3A22.620304Z%22%2C%22updated_at%22%3A%222025-02-10T15%3A50%3A47.909025Z%22%2C%22is_anonymous%22%3Afalse%7D%7D; ph_phc_kyzaz2uOZkTGjBpixpJPev9B8cusob2snVtgYXoIn96_posthog=%7B%22distinct_id%22%3A%22ed8de3b0-4355-4776-83c8-6033ffdc6500%22%2C%22%24sesid%22%3A%5B1739203150395%2C%220194f08b-23b9-79ee-8825-f0a5069503c7%22%2C1739202438073%5D%2C%22%24epp%22%3Atrue%2C%22%24initial_person_info%22%3A%7B%22r%22%3A%22https%3A%2F%2Fwww.krea.ai%2Ftrain%22%2C%22u%22%3A%22https%3A%2F%2Fwww.krea.ai%2Fapps%2Fimage%2Fflux%3Fstyle%3Dkb06lqi4o%22%7D%7D",
    "Referer": "https://www.krea.ai/train",
    "Referrer-Policy": "strict-origin-when-cross-origin"
}

# 전송할 payload 데이터를 dict로 구성한 후 JSON 문자열로 변환합니다.
payload_data = {
    "model": "flux_dev",
    "name": "Casual Portraits",
    "images": [
        {
            "url": "https://app-uploads.krea.ai/ed8de3b0-4355-4776-83c8-6033ffdc6500/1739203115353-f2bccc89-522b-4aa0-b4c4-d4e324edaaf6.png",
            "safe": True,
            "width": 419,
            "height": 656
        },
        {
            "url": "https://app-uploads.krea.ai/ed8de3b0-4355-4776-83c8-6033ffdc6500/1739203117141-bc70840c-9285-43e6-bf46-02541d165368.jpeg",
            "safe": True,
            "width": 2556,
            "height": 3408
        },
        {
            "url": "https://app-uploads.krea.ai/ed8de3b0-4355-4776-83c8-6033ffdc6500/1739203117182-0e5e5c49-b17b-422e-836a-0514c64278fc.jpeg",
            "safe": True,
            "width": 2556,
            "height": 3408
        },
        {
            "url": "https://app-uploads.krea.ai/ed8de3b0-4355-4776-83c8-6033ffdc6500/1739203117474-9c5dac7e-de44-40e5-9f00-6596e89cd057.png",
            "safe": True,
            "width": 1284,
            "height": 3593
        },
        {
            "url": "https://app-uploads.krea.ai/ed8de3b0-4355-4776-83c8-6033ffdc6500/1739203117099-acb784d1-a62b-4a3f-8b3a-f7fbe4cb9f7f.jpeg",
            "safe": True,
            "width": 2556,
            "height": 3408
        }
    ],
    "max_train_steps": 250,
    "trigger_word": "krea",
    "learning_rate": 0.003,
    "gradient_accumulation_steps": 1,
    "training_resolutions": [[512, 512], [768, 768], [1024, 1024]],
    "timestep_sampling": "sigmoid",
    "dataset_repeats_per_resolution": {"512": 4, "768": 4, "1024": 1},
    "mask_config": {"use_masks": True, "mask_min_val": 0.1},
    "train_type": "Character",
    "lr_scheduler_max_iters": 1
}


# JSON 문자열로 변환합니다.
payload_json = json.dumps(payload_data)

# multipart/form-data 형식으로 "payload" 필드에 해당 JSON 문자열을 담아 전송합니다.
files = {
    "payload": (None, payload_json, "application/json")
}

response = requests.post(url, headers=headers, files=files)

print("Status Code:", response.status_code)
print("Response:", response.text)
