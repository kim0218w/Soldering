# stepper_4motor_turn_off_after_each.py
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
    return h

def gpio_cleanup(h):
    for m in MOTORS:
        try:
            lgpio.gpio_free(h, m["step"])
            lgpio.gpio_free(h, m["dir"])
        except Exception:
            pass
    lgpio.gpiochip_close(h)

def move_steps(h, motor, steps, direction=1, delay=0.002):
    """단순 스텝 구동"""
    step_pin, dir_pin = motor["step"], motor["dir"]

    lgpio.gpio_write(h, dir_pin, direction)
    time.sleep(DIR_SETUP_S)

    for _ in range(steps):
        lgpio.gpio_write(h, step_pin, 1)
        time.sleep(delay/2)
        lgpio.gpio_write(h, step_pin, 0)
        time.sleep(delay/2)

    # 모터 끄기 (DIR, STEP 모두 LOW)
    lgpio.gpio_write(h, step_pin, 0)
    lgpio.gpio_write(h, dir_pin, 0)

def main():
    h = gpio_init()
    try:
        while True:
            for m in MOTORS:
                print(f" {m['name']} 시계 방향 회전 중...")
                move_steps(h, m, steps=200, direction=1, delay=0.002)  # 200스텝(=1회전)
                print(f" {m['name']} 완료, 모터 OFF")
                time.sleep(1)  # 모터 끈 상태에서 잠시 대기

                print(f" {m['name']} 반시계 방향 회전 중...")
                move_steps(h, m, steps=200, direction=0, delay=0.002)
                print(f" {m['name']} 완료, 모터 OFF")
                time.sleep(1)

    except KeyboardInterrupt:
        print("\n정지: GPIO 해제 중...")
    finally:
        gpio_cleanup(h)
        print("GPIO 해제 완료. 프로그램 종료.")

if __name__ == "__main__":
    main()
