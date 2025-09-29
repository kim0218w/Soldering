# stepper_4motor_scurve_sequential.py
import lgpio
import time
import math

# --- 모터 핀 설정 (BCM 번호) ---
step_pin_1, dir_pin_1 = 17, 18
step_pin_2, dir_pin_2 = 27, 22
step_pin_3, dir_pin_3 = 23, 24
step_pin_4, dir_pin_4 = 10, 9

MOTORS = [
    {"step": step_pin_1, "dir": dir_pin_1, "name": "모터1"},
    {"step": step_pin_2, "dir": dir_pin_2, "name": "모터2"},
    {"step": step_pin_3, "dir": dir_pin_3, "name": "모터3"},
    {"step": step_pin_4, "dir": dir_pin_4, "name": "모터4"},
]

# 마이크로스텝 설정 (TB6600 DIP 스위치에 맞게 수정)
MICROSTEP = 1
STEPS_PER_REV = 200 * MICROSTEP
DEG_PER_STEP = 360.0 / STEPS_PER_REV

# 하드웨어 타이밍
DIR_SETUP_S = 0.000010       # 10us
STEP_PULSE_MIN_S = 0.000010  # 10us

def gpio_init():
    h = lgpio.gpiochip_open(0)
    for m in MOTORS:
        lgpio.gpio_claim_output(h, 0, m["step"], 0)
        lgpio.gpio_claim_output(h, 0, m["dir"], 0)
    return h

def gpio_cleanup(h):
    for m in MOTORS:
        try:
            lgpio.gpio_free(h, m["step"])
            lgpio.gpio_free(h, m["dir"])
        except Exception:
            pass
    lgpio.gpiochip_close(h)

def s_curve_profile(steps: int):
    if steps <= 1:
        return [1.0]
    return [(1 - math.cos(math.pi * i / (steps - 1))) / 2 for i in range(steps)]

def move_stepper(h, motor, current_angle, target_angle, duration=1.0):
    step_pin, dir_pin = motor["step"], motor["dir"]

    delta_angle = target_angle - current_angle
    steps_needed = int(round(abs(delta_angle) / DEG_PER_STEP))
    if steps_needed == 0:
        return target_angle

    direction = 1 if delta_angle > 0 else 0
    lgpio.gpio_write(h, dir_pin, direction)
    time.sleep(DIR_SETUP_S)

    EPS = 0.15
    base_profile = s_curve_profile(steps_needed)
    speed_weights = [EPS + (1.0 - EPS) * v for v in base_profile]

    inv_sum = sum(1.0 / w for w in speed_weights)
    k = duration / inv_sum

    for w in speed_weights:
        period = max(k / w, STEP_PULSE_MIN_S * 2)
        high_t = max(STEP_PULSE_MIN_S, period / 2)
        low_t = max(STEP_PULSE_MIN_S, period - high_t)

        lgpio.gpio_write(h, step_pin, 1)
        time.sleep(high_t)
        lgpio.gpio_write(h, step_pin, 0)
        time.sleep(low_t)

    return target_angle

def main():
    h = gpio_init()
    current_angles = [0.0, 0.0, 0.0, 0.0]

    print("순차 입력 모드: 모터1 → 모터2 → 모터3 → 모터4 순서로 각도 입력 후 즉시 동작합니다.")
    print("입력 예) 90   (엔터만 치면 건너뜀, q 입력 시 종료)")
    try:
        while True:
            for i, m in enumerate(MOTORS):
                raw = input(f"{m['name']} 목표 각도? (현재 {current_angles[i]:.1f}°) : ").strip()
                if raw.lower() in ("q", "quit", "exit"):
                    raise KeyboardInterrupt
                if raw == "":
                    print(f" - {m['name']} 건너뜀")
                    continue
                try:
                    target = float(raw)
                except ValueError:
                    print("⚠️ 숫자를 입력하세요. (예: 90, -45)")
                    continue

                print(f"👉 {m['name']} {current_angles[i]:.1f}° → {target:.1f}° 이동 중...")
                current_angles[i] = move_stepper(h, m, current_angles[i], target, duration=2.0)
                print(f"✅ {m['name']} 완료: 현재 {current_angles[i]:.1f}°")

    except KeyboardInterrupt:
        print("\n정지: GPIO 해제 중...")
    finally:
        gpio_cleanup(h)
        print("GPIO 해제 완료. 프로그램 종료.")

if __name__ == "__main__":
    main()
