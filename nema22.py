# stepper_2motor_with_enable.py
import lgpio
import time
import math

# --- 모터 핀 설정 (BCM 번호) ---
# 예시 핀 번호: 실제 배선에 맞게 수정하세요
step_pin_1, dir_pin_1, en_pin_1 = 18, 17, 6
step_pin_2, dir_pin_2, en_pin_2 = 22, 27, 13

MOTORS = [
    {"step": step_pin_1, "dir": dir_pin_1, "en": en_pin_1, "name": "모터1"},
    {"step": step_pin_2, "dir": dir_pin_2, "en": en_pin_2, "name": "모터2"},
]

# --- 스텝모터 파라미터 ---
MICROSTEP = 1
STEPS_PER_REV = 200 * MICROSTEP
DEG_PER_STEP = 360.0 / STEPS_PER_REV

DIR_SETUP_S = 0.000010
STEP_PULSE_MIN_S = 0.000010


def gpio_init():
    h = lgpio.gpiochip_open(0)
    for m in MOTORS:
        lgpio.gpio_claim_output(h, 0, m["step"], 0)
        lgpio.gpio_claim_output(h, 0, m["dir"], 0)
        lgpio.gpio_claim_output(h, 0, m["en"], 1)  # 시작 시 Disable (전류 차단 상태)
    return h


def gpio_cleanup(h):
    for m in MOTORS:
        try:
            lgpio.gpio_free(h, m["step"])
            lgpio.gpio_free(h, m["dir"])
            lgpio.gpio_free(h, m["en"])
        except Exception:
            pass
    lgpio.gpiochip_close(h)


def enable_motor(h, motor):
    lgpio.gpio_write(h, motor["en"], 0)  # EN LOW → Enable (TB6600 기준)
    time.sleep(0.01)


def disable_motor(h, motor):
    lgpio.gpio_write(h, motor["en"], 1)  # EN HIGH → Disable (전류 차단)


def move_to_angle(h, motor, current_angle, target_angle, delay=0.002):
    step_pin, dir_pin = motor["step"], motor["dir"]

    delta_angle = target_angle - current_angle
    steps_needed = int(round(abs(delta_angle) / DEG_PER_STEP))
    if steps_needed == 0:
        return current_angle

    # 모터 전원 켜기
    enable_motor(h, motor)

    direction = 1 if delta_angle > 0 else 0
    lgpio.gpio_write(h, dir_pin, direction)
    time.sleep(DIR_SETUP_S)

    for _ in range(steps_needed):
        lgpio.gpio_write(h, step_pin, 1)
        time.sleep(delay/2)
        lgpio.gpio_write(h, step_pin, 0)
        time.sleep(delay/2)

    # 동작 완료 후 전류 차단
    disable_motor(h, motor)

    return target_angle


def main():
    h = gpio_init()
    current_angles = [0.0, 0.0]  # 모터1, 모터2의 현재 각도

    try:
        while True:
            raw = input("각도 입력 (예: 90 180) 또는 q 종료: ").strip()
            if raw.lower() in ("q", "quit", "exit"):
                break

            try:
                target_angles = list(map(float, raw.split()))
            except ValueError:
                print("⚠️ 숫자 2개를 입력하세요. 예: 90 180")
                continue

            if len(target_angles) != 2:
                print("⚠️ 모터1, 모터2 각도 2개를 입력해야 합니다.")
                continue

            for i, m in enumerate(MOTORS):
                print(f"👉 {m['name']} {current_angles[i]:.1f}° → {target_angles[i]:.1f}° 이동 중...")
                current_angles[i] = move_to_angle(h, m, current_angles[i], target_angles[i])
                print(f"✅ {m['name']} 완료 (전류 차단됨)")

    except KeyboardInterrupt:
        print("\n정지: GPIO 해제 중...")
    finally:
        gpio_cleanup(h)
        print("GPIO 해제 완료. 프로그램 종료.")


if __name__ == "__main__":
    main()
