import lgpio
import time

# ---------- 핀 설정(BCM 번호) ----------
PRIMARY_DIR_PIN = 17   # DIR+ of first driver
PRIMARY_PUL_PIN = 18   # PUL+ of first driver
SECONDARY_DIR_PIN = 27  # DIR+ of second driver (update to your wiring)
SECONDARY_PUL_PIN = 22  # PUL+ of second driver (update to your wiring)
DIR_PINS = (PRIMARY_DIR_PIN, SECONDARY_DIR_PIN)
PUL_PINS = (PRIMARY_PUL_PIN, SECONDARY_PUL_PIN)
# PUL-, DIR- 는 라즈베리파이 GND(물리핀 6/9/14/20/25/30/34/39 등)로 연결

# ---------- 기구/드라이버 파라미터 ----------
GEAR = 54            # 54:1 감속기
MOTOR_STEPS = 3600    # NEMA23 기본(1.8°)
MICROSTEP = 1        # 드라이버 DIP와 동일하게! (1,2,4,8,16,...)

# 출력축 1바퀴에 필요한 펄스 수 = 200 * MICROSTEP * GEAR
PULSES_OUTPUT_REV = MOTOR_STEPS * MICROSTEP * GEAR

# 속도(지연). 너무 낮추면 탈조 가능. 하이/로 각각 delay → 주기=2*delay
PULSE_DELAY = 0.0008


def pulse_once(h, pins, delay):
    if isinstance(pins, int):
        pins = (pins,)
    for pin in pins:
        lgpio.gpio_write(h, pin, 1)
    time.sleep(delay)
    for pin in pins:
        lgpio.gpio_write(h, pin, 0)
    time.sleep(delay)


def rotate_output_one_rev(h, cw=True):
    # 방향 설정 (배선 극성에 따라 0/1 바뀔 수 있음)
    direction_level = 1 if cw else 0
    for dir_pin in DIR_PINS:
        lgpio.gpio_write(h, dir_pin, direction_level)
    # 펄스를 모든 출력축 드라이버에 동시에 보냄
    for _ in range(PULSES_OUTPUT_REV):
        pulse_once(h, PUL_PINS, PULSE_DELAY)


if __name__ == "__main__":
    h = lgpio.gpiochip_open(0)
    try:
        # 출력으로 클레임(초기값 0)
        for dir_pin in DIR_PINS:
            lgpio.gpio_claim_output(h, dir_pin, 0)
        for pul_pin in PUL_PINS:
            lgpio.gpio_claim_output(h, pul_pin, 0)

        print(
            f"[INFO] gear={GEAR}:1, microstep={MICROSTEP}, pulses/rev={PULSES_OUTPUT_REV}, drivers={len(PUL_PINS)}"
        )
        print("[RUN] 출력축 1바퀴 CW")
        rotate_output_one_rev(h, cw=True)

        time.sleep(1.0)

        print("[RUN] 출력축 1바퀴 CCW")
        rotate_output_one_rev(h, cw=False)

        print("[DONE]")
    except KeyboardInterrupt:
        print("\n[STOP] 사용자 인터럽트")
    finally:
        lgpio.gpiochip_close(h)
