# stepper_4motor_with_enable.py
import lgpio
import time

# --- 모터 핀 설정 (BCM 번호) ---
step_pin_1, dir_pin_1, en_pin_1 = 17, 18, 6
step_pin_2, dir_pin_2, en_pin_2 = 27, 22, 13
step_pin_3, dir_pin_3, en_pin_3 = 23, 24, 19
step_pin_4, dir_pin_4, en_pin_4 = 10, 9, 26

MOTORS = [
    {"step": step_pin_1, "dir": dir_pin_1, "en": en_pin_1, "name": "모터1"},
    {"step": step_pin_2, "dir": dir_pin_2, "en": en_pin_2, "name": "모터2"},
    {"step": step_pin_3, "dir": dir_pin_3, "en": en_pin_3, "name": "모터3"},
    {"step": step_pin_4, "dir": dir_pin_4, "en": en_pin_4, "name": "모터4"},
]

DIR_SETUP_S = 0.000010
STEP_PULSE_MIN_S = 0.000010

def gpio_init():
    h = lgpio.gpiochip_open(0)
    for m in MOTORS:
        lgpio.gpio_claim_output(h, 0, m["step"], 0)
        lgpio.gpio_claim_output(h, 0, m["dir"], 0)
        lgpio.gpio_claim_output(h, 0, m["en"], 1)  # 시작 시 Disable 상태
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
    # EN 핀 LOW → Enable (TB6600 기준)
    lgpio.gpio_write(h, motor["en"], 0)

def disable_motor(h, motor):
    # EN 핀 HIGH → Disable (TB6600 기준)
    lgpio.gpio_write(h, motor["en"], 1)

def move_steps(h, motor, steps, direction=1, delay=0.002):
    step_pin, dir_pin = motor["step"], motor["dir"]

    # 모터 켜기
    enable_motor(h, motor)
    time.sleep(0.01)  # 안정화 시간

    lgpio.gpio_write(h, dir_pin, direction)
    time.sleep(DIR_SETUP_S)

    for _ in range(steps):
        lgpio.gpio_write(h, step_pin, 1)
        time.sleep(delay/2)
        lgpio.gpio_write(h, step_pin, 0)
        time.sleep(delay/2)

    # 모터 끄기 (전류 차단)
    disable_motor(h, motor)

def main():
    h = gpio_init()
    try:
        while True:
            for m in MOTORS:
                print(f"👉 {m['name']} 시계 방향 회전 중...")
                move_steps(h, m, steps=200, direction=1, delay=0.002)
                print(f"✅ {m['name']} 완료 → 전류 차단")
                time.sleep(1)

                print(f"👉 {m['name']} 반시계 방향 회전 중...")
                move_steps(h, m, steps=200, direction=0, delay=0.002)
                print(f"✅ {m['name']} 완료 → 전류 차단")
                time.sleep(1)

    except KeyboardInterrupt:
        print("\n정지: GPIO 해제 중...")
    finally:
        gpio_cleanup(h)
        print("GPIO 해제 완료. 프로그램 종료.")

if __name__ == "__main__":
    main()
