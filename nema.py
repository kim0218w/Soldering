import lgpio
import time
import math

# ---------- 핀 설정(BCM 번호) ----------
PRIMARY_DIR_PIN = 17   # 첫 번째 드라이버 DIR+
PRIMARY_PUL_PIN = 18   # 첫 번째 드라이버 PUL+
SECONDARY_DIR_PIN = 27  # 두 번째 드라이버 DIR+
SECONDARY_PUL_PIN = 22  # 두 번째 드라이버 PUL+
DRIVERS = (
    ("FIRST", PRIMARY_DIR_PIN, PRIMARY_PUL_PIN),
    ("SECOND", SECONDARY_DIR_PIN, SECONDARY_PUL_PIN),
)
# PUL-, DIR- 는 라즈베리파이 GND로 연결

# ---------- 기구/드라이버 파라미터 ----------
GEAR = 54
MOTOR_STEPS = 200       # 스텝모터 1.8° → 200스텝
MICROSTEP = 1           # 드라이버 DIP 스위치와 동일
PULSES_OUTPUT_REV = MOTOR_STEPS * MICROSTEP * GEAR

# ---------- 속도 파라미터 ----------
PULSE_DELAY_MIN = 0.0005   # 최고속도 (짧을수록 빠름)
PULSE_DELAY_MAX = 0.0030   # 출발/정지 속도 (길수록 느림)
ACCEL_RATIO = 0.2          # 전체 스텝 중 앞뒤 20%를 가속/감속에 할당


def pulse_once(h, pin, delay):
    lgpio.gpio_write(h, pin, 1)
    time.sleep(delay)
    lgpio.gpio_write(h, pin, 0)
    time.sleep(delay)


def s_curve_delay(progress: float) -> float:
    """
    progress: 0~1 (가속 0→1, 감속 1→0)
    코사인 기반 S-curve 보간
    """
    return PULSE_DELAY_MAX - (PULSE_DELAY_MAX - PULSE_DELAY_MIN) * (
        0.5 - 0.5 * math.cos(math.pi * progress)
    )


def rotate_driver_one_rev(h, dir_pin, pul_pin, cw=True):
    lgpio.gpio_write(h, dir_pin, 1 if cw else 0)

    accel_steps = int(PULSES_OUTPUT_REV * ACCEL_RATIO)
    decel_steps = accel_steps
    const_steps = PULSES_OUTPUT_REV - accel_steps - decel_steps

    # 가속 구간
    for i in range(accel_steps):
        delay = s_curve_delay(i / accel_steps)
        pulse_once(h, pul_pin, delay)

    # 정속 구간
    for _ in range(const_steps):
        pulse_once(h, pul_pin, PULSE_DELAY_MIN)

    # 감속 구간
    for i in range(decel_steps):
        delay = s_curve_delay(1 - i / decel_steps)
        pulse_once(h, pul_pin, delay)


if __name__ == "__main__":
    h = lgpio.gpiochip_open(0)
    try:
        # 모든 드라이버의 DIR/PUL 핀을 출력으로 설정
        for _, dir_pin, pul_pin in DRIVERS:
            lgpio.gpio_claim_output(h, dir_pin, 0)
            lgpio.gpio_claim_output(h, pul_pin, 0)

        print(
            f"[INFO] gear={GEAR}:1, microstep={MICROSTEP}, pulses/rev={PULSES_OUTPUT_REV}, drivers={len(DRIVERS)}"
        )

        # 첫 번째 드라이버 시퀀스
        print("[RUN] FIRST 드라이버 1바퀴 CW (S-curve)")
        rotate_driver_one_rev(h, PRIMARY_DIR_PIN, PRIMARY_PUL_PIN, cw=True)
        time.sleep(1.0)
        print("[RUN] FIRST 드라이버 1바퀴 CCW (S-curve)")
        rotate_driver_one_rev(h, PRIMARY_DIR_PIN, PRIMARY_PUL_PIN, cw=False)

        time.sleep(1.0)

        # 두 번째 드라이버 시퀀스
        print("[RUN] SECOND 드라이버 1바퀴 CW (S-curve)")
        rotate_driver_one_rev(h, SECONDARY_DIR_PIN, SECONDARY_PUL_PIN, cw=True)
        time.sleep(1.0)
        print("[RUN] SECOND 드라이버 1바퀴 CCW (S-curve)")
        rotate_driver_one_rev(h, SECONDARY_DIR_PIN, SECONDARY_PUL_PIN, cw=False)

        print("[DONE]")
    except KeyboardInterrupt:
        print("\n[STOP] 사용자 인터럽트")
    finally:
        lgpio.gpiochip_close(h)
