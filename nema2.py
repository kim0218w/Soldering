# stepper_4motor_scurve_refactored.py
import lgpio
import time
import math

# --- 모터 핀 설정 (BCM 번호) ---
step_pin_1, dir_pin_1 = 17, 18
step_pin_2, dir_pin_2 = 27, 22
step_pin_3, dir_pin_3 = 23, 24
step_pin_4, dir_pin_4 = 10, 9

MOTORS = [
    {"step": step_pin_1, "dir": dir_pin_1},
    {"step": step_pin_2, "dir": dir_pin_2},
    {"step": step_pin_3, "dir": dir_pin_3},
    {"step": step_pin_4, "dir": dir_pin_4},
]

# --- 스텝모터 파라미터 ---
STEPS_PER_REV = 200              # 1회전 = 200스텝 (마이크로스텝에 맞게 수정)
DEG_PER_STEP = 360.0 / STEPS_PER_REV

# --- GPIO 초기화 ---
h = lgpio.gpiochip_open(0)
for motor in MOTORS:
    lgpio.gpio_claim_output(h, 0, motor["step"], 0)  # step 핀 LOW로 초기화
    lgpio.gpio_claim_output(h, 0, motor["dir"], 0)   # dir 핀 LOW로 초기화

# --- S-curve 프로파일 생성 ---
def s_curve_profile(steps: int):
    """
    steps 길이의 S-curve 가속/감속 비율 배열을 생성.
    (cosine 기반: 0 → 1 → 0 속도 변화)
    """
    return [(1 - math.cos(math.pi * i / (steps - 1))) / 2 for i in range(steps)]

# --- 모터 제어 함수 ---
def move_stepper(motor, current_angle, target_angle, duration=1.0):
    step_pin, dir_pin = motor["step"], motor["dir"]

    delta_angle = target_angle - current_angle
    steps_needed = int(abs(delta_angle) / DEG_PER_STEP)

    if steps_needed == 0:
        return target_angle

    # 방향 설정
    direction = 1 if delta_angle > 0 else 0
    lgpio.gpio_write(h, dir_pin, direction)

    # S-curve 프로파일 생성
    profile = s_curve_profile(steps_needed if steps_needed > 1 else 2)

    # 전체 이동 시간을 profile에 따라 분배
    for weight in profile:
        delay = (duration / steps_needed) * (1 + (1 - weight))  # 가속/감속 반영
        lgpio.gpio_write(h, step_pin, 1)
        time.sleep(delay / 2)
        lgpio.gpio_write(h, step_pin, 0)
        time.sleep(delay / 2)

    return target_angle

# --- 메인 루프 ---
if __name__ == "__main__":
    current_angles = [0, 0, 0, 0]  # 1~4번 모터 현재 각도

    try:
        while True:
            raw = input("각도 입력 (예: 90 45 180 0): ")
            target_angles = list(map(int, raw.split()))

            if len(target_angles) != 4:
                print("⚠️ 1~4번 모터 각도 4개를 입력해야 합니다.")
                continue

            for i in range(4):
                print(f"👉 {i+1}번 모터 {current_angles[i]}° → {target_angles[i]}° 이동 중...")
                current_angles[i] = move_stepper(MOTORS[i], current_angles[i], target_angles[i], duration=2.0)

    except KeyboardInterrupt:
        print("\n정지: GPIO 해제")
        for motor in MOTORS:
            lgpio.gpio_free(h, motor["step"])
            lgpio.gpio_free(h, motor["dir"])
        lgpio.gpiochip_close(h)
