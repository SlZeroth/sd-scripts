import math

# 사용자 입력 받기
target_steps = int(input("목표 스텝 수 (target_steps)를 입력하세요: "))
special_repeat = int(input("특수 이미지 반복 횟수 (special_repeat)를 입력하세요: "))
regular_repeat = int(input("일반 이미지 반복 횟수 (regular_repeat)를 입력하세요 (보통 1): "))

# 이미지 개수 입력 받기
total_images = int(input("전체 이미지 수를 입력하세요: "))
special_count = int(input("특수 이미지 수를 입력하세요: "))
regular_count = total_images - special_count

# 에포크 당 스텝 수 계산
# 각 에포크에서는 일반 이미지는 regular_repeat번, 특수 이미지는 special_repeat번 사용됨.
steps_per_epoch = (regular_count * regular_repeat) + (special_count * special_repeat)

# target_steps에 맞춰 전체 학습 에포크 수 계산
ideal_epochs = target_steps / steps_per_epoch
floor_epochs = max(1, math.floor(ideal_epochs))
ceil_epochs = math.ceil(ideal_epochs)

# 각 경우의 총 스텝 수
floor_total = floor_epochs * steps_per_epoch
ceil_total = ceil_epochs * steps_per_epoch

# 목표 스텝에 더 가까운 쪽을 선택
if abs(floor_total - target_steps) <= abs(ceil_total - target_steps):
    chosen_epochs = floor_epochs
    actual_total_steps = floor_total
else:
    chosen_epochs = ceil_epochs
    actual_total_steps = ceil_total

# 결과 출력
print("------------------------------------------------")
print(f"에포크 당 스텝 수: {steps_per_epoch}")
print(f"최종 학습 스텝 (max_steps): {actual_total_steps}")
print(f"학습 에포크 수: {chosen_epochs}")
print(f"특수 이미지 반복 횟수 (special_repeat): {special_repeat}")
print("------------------------------------------------")
