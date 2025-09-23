import lgpio
import time

# ---------- 핀 설정(BCM 번호) ----------
PRIMARY_DIR_PIN = 17   # 첫 번째 드라이버 DIR+
PRIMARY_PUL_PIN = 18   # 첫 번째 드라이버 PUL+
SECONDARY_DIR_PIN = 27  # 두 번째 드라이버 DIR+ (배선에 맞게 수정)
SECONDARY_PUL_PIN = 22  # 두 번째 드라이버 PUL+ (배선에 맞게 수정)
DRIVERS = (
    ("FIRST", PRIMARY_DIR_PIN, PRIMARY_PUL_PIN),
    ("SECOND", SECONDARY_DIR_PIN, SECONDARY_PUL_PIN),
)
# PUL-, DIR- 는 라즈베리파이 GND(물리핀 6/9/14/20/25/30/34/39 등)로 연결

# ---------- 기구/드라이버 파라미터 ----------
GEAR = 54            # 54:1 감속기
MOTOR_STEPS = 3600    # NEMA23 기본(1.8°)
MICROSTEP = 1        # 드라이버 DIP와 동일하게! (1,2,4,8,16,...)

# 출력축 1바퀴에 필요한 펄스 수 = 200 * MICROSTEP * GEAR
PULSES_OUTPUT_REV = MOTOR_STEPS * MICROSTEP * GEAR

# 속도(지연). 너무 낮추면 탈조 가능. 하이/로 각각 delay → 주기=2*delay
PULSE_DELAY = 0.0008


def pulse_once(h, pin, delay):
    lgpio.gpio_write(h, pin, 1)
    time.sleep(delay)
    lgpio.gpio_write(h, pin, 0)
    time.sleep(delay)


def rotate_driver_one_rev(h, dir_pin, pul_pin, cw=True):
    direction_level = 1 if cw else 0
    lgpio.gpio_write(h, dir_pin, direction_level)
    for _ in range(PULSES_OUTPUT_REV):
        pulse_once(h, pul_pin, PULSE_DELAY)


if __name__ == "__main__":
    h = lgpio.gpiochip_open(0)
    try:
        # 모든 드라이버의 DIR/PUL 핀을 순서대로 출력으로 설정
        for _, dir_pin, pul_pin in DRIVERS:
            lgpio.gpio_claim_output(h, dir_pin, 0)
            lgpio.gpio_claim_output(h, pul_pin, 0)

        print(
            f"[INFO] gear={GEAR}:1, microstep={MICROSTEP}, pulses/rev={PULSES_OUTPUT_REV}, drivers={len(DRIVERS)}"
        )

        # 첫 번째 드라이버 시퀀스
        print("[RUN] FIRST 드라이버 1바퀴 CW")
        rotate_driver_one_rev(h, PRIMARY_DIR_PIN, PRIMARY_PUL_PIN, cw=True)
        time.sleep(1.0)
        print("[RUN] FIRST 드라이버 1바퀴 CCW")
        rotate_driver_one_rev(h, PRIMARY_DIR_PIN, PRIMARY_PUL_PIN, cw=False)

        time.sleep(1.0)

        # 두 번째 드라이버 시퀀스
        print("[RUN] SECOND 드라이버 1바퀴 CW")
        rotate_driver_one_rev(h, SECONDARY_DIR_PIN, SECONDARY_PUL_PIN, cw=True)
        time.sleep(1.0)
        print("[RUN] SECOND 드라이버 1바퀴 CCW")
        rotate_driver_one_rev(h, SECONDARY_DIR_PIN, SECONDARY_PUL_PIN, cw=False)

        print("[DONE]")
    except KeyboardInterrupt:
        print("\n[STOP] 사용자 인터럽트")
    finally:
        lgpio.gpiochip_close(h)
