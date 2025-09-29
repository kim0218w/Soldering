import lgpio
import time
import math

# =========================
# 1~4번 모터 핀 설정(BCM)
# =========================
PRIMARY_DIR_PIN   = 17   # FIRST  DIR+
PRIMARY_PUL_PIN   = 18   # FIRST  PUL+
SECONDARY_DIR_PIN = 27   # SECOND DIR+
SECONDARY_PUL_PIN = 22   # SECOND PUL+
THIRD_DIR_PIN     = 23   # THIRD  DIR+
THIRD_PUL_PIN     = 24   # THIRD  PUL+
FOURTH_DIR_PIN    = 9    # FOURTH DIR+  (주의: 09가 아니라 9)
FOURTH_PUL_PIN    = 10   # FOURTH PUL+

DRIVERS = (
    ("FIRST",  PRIMARY_DIR_PIN,   PRIMARY_PUL_PIN),
    ("SECOND", SECONDARY_DIR_PIN, SECONDARY_PUL_PIN),
    ("THIRD",  THIRD_DIR_PIN,     THIRD_PUL_PIN),
    ("FOURTH", FOURTH_DIR_PIN,    FOURTH_PUL_PIN),
)

# =========================
# 5번 모터 핀 (스텝수/방향 전용)
# =========================
FIFTH_DIR_PIN = 12   # DIR+
FIFTH_PUL_PIN = 13   # PUL+
# PUL-, DIR- 는 라즈베리파이 GND(물리핀 6/9/14/20/25/30/34/39 등)로 연결

# =========================
# 1~4번 기구/드라이버 파라미터(각도 제어)
# =========================
GEAR = 54
GEAR_5=9
MOTOR_STEPS = 200        # 1.8° → 200 스텝
MICROSTEP = 1
PULSES_PER_REV = MOTOR_STEPS * MICROSTEP * GEAR  # 출력축 1회전 펄스 수

# =========================
# 속도 파라미터
# =========================
# 1~4번: S-curve 가감속
PULSE_DELAY_MIN = 0.0005   # 최고 속도(하이/로 각각 지연)
PULSE_DELAY_MAX = 0.0030   # 출발/정지 속도
ACCEL_RATIO     = 0.2      # 앞/뒤 20% 구간 가감속

# 5번: 단순 고정 지연
PULSE_DELAY_5   = 0.0001   # 너무 낮추면 탈조 가능 → 필요시 0.0002~0.0005로 키우기

# =========================
# 공용 펄스 함수
# =========================
def pulse_once(h, pin, delay):
    lgpio.gpio_write(h, pin, 1)
    time.sleep(delay)
    lgpio.gpio_write(h, pin, 0)
    time.sleep(delay)

# =========================
# 1~4번: S-curve 보간 지연
# =========================
def s_curve_delay(progress: float) -> float:
    # progress: 0~1 (가속 0→1, 감속 1→0)
    return PULSE_DELAY_MAX - (PULSE_DELAY_MAX - PULSE_DELAY_MIN) * (
        0.5 - 0.5 * math.cos(math.pi * progress)
    )

# =========================
# 1~4번: 각도 기반 회전
# =========================
def rotate_driver_angle(h, dir_pin, pul_pin, angle: float, cw=True):
    steps_needed = int(PULSES_PER_REV * (angle / 360.0))
    if steps_needed <= 0:
        return

    lgpio.gpio_write(h, dir_pin, 1 if cw else 0)

    accel_steps = int(steps_needed * ACCEL_RATIO)
    decel_steps = accel_steps
    const_steps = steps_needed - accel_steps - decel_steps
    if const_steps < 0:  # 작은 각도면 정속 없음
        accel_steps = steps_needed // 2
        decel_steps = steps_needed - accel_steps
        const_steps = 0

    # 가속
    for i in range(accel_steps):
        delay = s_curve_delay((i + 1) / max(1, accel_steps))
        pulse_once(h, pul_pin, delay)

    # 정속
    for _ in range(const_steps):
        pulse_once(h, pul_pin, PULSE_DELAY_MIN)

    # 감속
    for i in range(decel_steps):
        delay = s_curve_delay(1 - (i + 1) / max(1, decel_steps))
        pulse_once(h, pul_pin, delay)

# =========================
# 5번: 스텝수 기반 회전
# =========================
def rotate_steps(h, dir_pin, pul_pin, steps: int, cw=True, delay=PULSE_DELAY_5):
    if steps <= 0:
        return
    lgpio.gpio_write(h, dir_pin, 1 if cw else 0)
    for _ in range(steps):
        pulse_once(h, pul_pin, delay)

# =========================
# 메인
# =========================
if __name__ == "__main__":
    h = lgpio.gpiochip_open(0)
    try:
        # 1~4번 출력 설정
        for _, dir_pin, pul_pin in DRIVERS:
            lgpio.gpio_claim_output(h, dir_pin, 0)
            lgpio.gpio_claim_output(h, pul_pin, 0)
        # 5번 출력 설정
        lgpio.gpio_claim_output(h, FIFTH_DIR_PIN, 0)
        lgpio.gpio_claim_output(h, FIFTH_PUL_PIN, 0)

        print(f"[INFO] gear={GEAR}:1, microstep={MICROSTEP}, pulses/rev={PULSES_PER_REV}, angle-drivers={len(DRIVERS)}, 5th=steps-mode")

        # ===== 사용자 입력 =====
        angle_first  = float(input("FIRST  모터 회전 각도 (deg): ").strip())
        dir_first    = input("FIRST  방향 (CW/CCW): ").strip().upper()

        angle_second = float(input("SECOND 모터 회전 각도 (deg): ").strip())
        dir_second   = input("SECOND 방향 (CW/CCW): ").strip().upper()

        angle_third  = float(input("THIRD  모터 회전 각도 (deg): ").strip())
        dir_third    = input("THIRD  방향 (CW/CCW): ").strip().upper()

        angle_fourth = float(input("FOURTH 모터 회전 각도 (deg): ").strip())
        dir_fourth   = input("FOURTH 방향 (CW/CCW): ").strip().upper()

        # 5번째: 각도 무시, 스텝수/방향만
        steps_fifth  = int(input("FIFTH 모터 스텝 수 (정수): ").strip())
        dir_fifth    = input("FIFTH 방향 (CW/CCW): ").strip().upper()

        loop_count   = int(input("몇 번 반복할까요?: ").strip())

        # ===== 실행(순차 구동) =====
        for n in range(loop_count):
            print(f"\n[LOOP {n+1}/{loop_count}]")

            print(f"[RUN] FIRST  {angle_first}° {dir_first}")
            rotate_driver_angle(h, PRIMARY_DIR_PIN,  PRIMARY_PUL_PIN,  angle_first,  cw=(dir_first  == "CW"))
            time.sleep(0.5)

            print(f"[RUN] SECOND {angle_second}° {dir_second}")
            rotate_driver_angle(h, SECONDARY_DIR_PIN, SECONDARY_PUL_PIN, angle_second, cw=(dir_second == "CW"))
            time.sleep(0.5)

            print(f"[RUN] THIRD  {angle_third}° {dir_third}")
            rotate_driver_angle(h, THIRD_DIR_PIN,    THIRD_PUL_PIN,    angle_third,  cw=(dir_third  == "CW"))
            time.sleep(0.5)

            print(f"[RUN] FOURTH {angle_fourth}° {dir_fourth}")
            rotate_driver_angle(h, FOURTH_DIR_PIN,   FOURTH_PUL_PIN,   angle_fourth, cw=(dir_fourth == "CW"))
            time.sleep(0.5)

            print(f"[RUN] FIFTH  {steps_fifth} steps {dir_fifth}")
            rotate_steps(h, FIFTH_DIR_PIN, FIFTH_PUL_PIN, steps_fifth, cw=(dir_fifth == "CW"), delay=PULSE_DELAY_5)

        print("\n[FINISH] 모든 루프 완료")

    except KeyboardInterrupt:
        print("\n[STOP] 사용자 인터럽트")
    finally:
        lgpio.gpiochip_close(h)