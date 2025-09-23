import lgpio, time, math

# ---------- 핀 설정(BCM 번호) ----------
DIR_PIN = 17
PUL_PIN = 18

# ---------- 기구/드라이버 파라미터 ----------
GEAR = 54
MOTOR_STEPS = 200    # 스텝모터 1.8° → 200스텝
MICROSTEP = 1
PULSES_OUTPUT_REV = MOTOR_STEPS * MICROSTEP * GEAR

# ---------- 속도 파라미터 ----------
PULSE_DELAY_MIN = 0.0005   # 최고속도일 때 딜레이 (주기 = 2*delay)
PULSE_DELAY_MAX = 0.0030   # 시작/종료 시 딜레이
ACCEL_RATIO = 0.2          # 전체 펄스 중 앞뒤 가속/감속 구간 비율 (20%씩)

def pulse_once(h, pin, delay):
    lgpio.gpio_write(h, pin, 1)
    time.sleep(delay)
    lgpio.gpio_write(h, pin, 0)
    time.sleep(delay)

def s_curve_delay(progress):
    """
    progress: 0~1 (가속 0→1, 감속 1→0)
    코사인 기반 S-curve 보간
    """
    return PULSE_DELAY_MAX - (PULSE_DELAY_MAX - PULSE_DELAY_MIN) * (0.5 - 0.5 * math.cos(math.pi * progress))

def rotate_output_one_rev(h, cw=True):
    lgpio.gpio_write(h, DIR_PIN, 1 if cw else 0)

    accel_steps = int(PULSES_OUTPUT_REV * ACCEL_RATIO)
    decel_steps = accel_steps
    const_steps = PULSES_OUTPUT_REV - accel_steps - decel_steps

    # 가속 구간
    for i in range(accel_steps):
        delay = s_curve_delay(i / accel_steps)
        pulse_once(h, PUL_PIN, delay)

    # 정속 구간
    for _ in range(const_steps):
        pulse_once(h, PUL_PIN, PULSE_DELAY_MIN)

    # 감속 구간
    for i in range(decel_steps):
        delay = s_curve_delay(1 - i / decel_steps)
        pulse_once(h, PUL_PIN, delay)

if __name__ == "__main__":
    h = lgpio.gpiochip_open(0)
    try:
        lgpio.gpio_claim_output(h, DIR_PIN, 0)
        lgpio.gpio_claim_output(h, PUL_PIN, 0)

        print(f"[INFO] gear={GEAR}:1, microstep={MICROSTEP}, pulses/rev={PULSES_OUTPUT_REV}")
        print("[RUN] 출력축 1바퀴 CW (S-curve)")
        rotate_output_one_rev(h, cw=True)

        time.sleep(1.0)

        print("[RUN] 출력축 1바퀴 CCW (S-curve)")
        rotate_output_one_rev(h, cw=False)

        print("[DONE]")
    except KeyboardInterrupt:
        print("\n[STOP] 사용자 인터럽트")
    finally:
        lgpio.gpiochip_close(h)
