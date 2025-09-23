import lgpio
import time
import math

# ---------- 핀 설정(BCM 번호) ----------
PRIMARY_DIR_PIN = 17   # 첫 번째 드라이버 DIR+
PRIMARY_PUL_PIN = 18   # 첫 번째 드라이버 PUL+
SECONDARY_DIR_PIN = 27  # 두 번째 드라이버 DIR+
SECONDARY_PUL_PIN = 22  # 두 번째 드라이버 PUL+
DIR_PIN = 23
PUL_PIN = 24
DRIVERS = (
    ("FIRST", PRIMARY_DIR_PIN, PRIMARY_PUL_PIN),
    ("SECOND", SECONDARY_DIR_PIN, SECONDARY_PUL_PIN),
)

# ---------- 기구/드라이버 파라미터 ----------
GEAR = 54
MOTOR_STEPS = 200       # 스텝모터 1.8° → 200스텝
MICROSTEP = 1
PULSES_PER_REV = MOTOR_STEPS * MICROSTEP * GEAR  # 출력축 1회전 펄스 수

# ---------- 속도 파라미터 ----------
PULSE_DELAY_MIN = 0.0005   # 최고속도
PULSE_DELAY_MAX = 0.0030   # 출발/정지 속도
ACCEL_RATIO = 0.2          # 전체 스텝 중 앞뒤 20%를 가속/감속에 사용


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


def rotate_driver_angle(h, dir_pin, pul_pin, angle: float, cw=True):
    """
    원하는 각도만큼 회전 (출력축 기준)
    """
    steps_needed = int(PULSES_PER_REV * (angle / 360.0))
    if steps_needed <= 0:
        return

    lgpio.gpio_write(h, dir_pin, 1 if cw else 0)

    accel_steps = int(steps_needed * ACCEL_RATIO)
    decel_steps = accel_steps
    const_steps = steps_needed - accel_steps - decel_steps
    if const_steps < 0:  # 작은 각도에서는 정속 구간 없음
        accel_steps = steps_needed // 2
        decel_steps = steps_needed - accel_steps
        const_steps = 0

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
            f"[INFO] gear={GEAR}:1, microstep={MICROSTEP}, pulses/rev={PULSES_PER_REV}, drivers={len(DRIVERS)}"
        )

        # 사용자 입력
        angle_first = float(input("FIRST 모터 회전 각도 (deg): ").strip())
        dir_first = input("FIRST 방향 (CW/CCW): ").strip().upper()
        angle_second = float(input("SECOND 모터 회전 각도 (deg): ").strip())
        dir_second = input("SECOND 방향 (CW/CCW): ").strip().upper()
        loop_count = int(input("몇 번 반복할까요?: ").strip())

        # 루프 실행
        for n in range(loop_count):
            print(f"\n[LOOP {n+1}/{loop_count}]")

            print(f"[RUN] FIRST 모터 {angle_first}° {dir_first}")
            rotate_driver_angle(
                h, PRIMARY_DIR_PIN, PRIMARY_PUL_PIN, angle_first, cw=(dir_first == "CW")
            )
            time.sleep(0.5)

            print(f"[RUN] SECOND 모터 {angle_second}° {dir_second}")
            rotate_driver_angle(
                h, SECONDARY_DIR_PIN, SECONDARY_PUL_PIN, angle_second, cw=(dir_second == "CW")
            )
            time.sleep(0.5)

        print("\n[FINISH] 모든 루프 완료")

    except KeyboardInterrupt:
        print("\n[STOP] 사용자 인터럽트")
    finally:
        lgpio.gpiochip_close(h)
