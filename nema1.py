import lgpio, time

# ---------- 핀 설정(BCM 번호) ----------
DIR_PIN = 17   # DIR+
PUL_PIN = 18   # PUL+
ENA_PIN = 27   # ENA+
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

def rotate_output_one_rev(h, cw=True):
    # 방향 설정 (배선 극성에 따라 0/1 바뀔 수 있음)
    lgpio.gpio_write(h, DIR_PIN, 1 if cw else 0)
    lgpio.gpio_write(h, ENA_PIN, 1)
    # 펄스 출력
    for _ in range(PULSES_OUTPUT_REV):
        pulse_once(h, PUL_PIN, PULSE_DELAY)
    lgpio.gpio_write(h, ENA_PIN, 0)             

def rotate_output_one_rev_with_speed(h, cw=True, speed=100):
    lgpio.gpio_write(h, ENA_PIN, speed)
    rotate_output_one_rev(h, cw)
    lgpio.gpio_write(h, ENA_PIN, 0)

if __name__ == "__main__":
    h = lgpio.gpiochip_open(0)
    try:
        # 출력으로 클레임(초기값 0)
        lgpio.gpio_claim_output(h, DIR_PIN, 0)
        lgpio.gpio_claim_output(h, PUL_PIN, 0)
        lgpio.gpio_claim_output(h, ENA_PIN, 0)

        print(f"[INFO] gear={GEAR}:1, microstep={MICROSTEP}, pulses/rev={PULSES_OUTPUT_REV}")
        print("[RUN] 출력축 1바퀴 CW")
        rotate_output_one_rev_with_speed(h, cw=True, speed=100)

        time.sleep(1.0)

        print("[RUN] 출력축 1바퀴 CCW")
        rotate_output_one_rev_with_speed(h, cw=False, speed=100)

        print("[DONE]")
    except KeyboardInterrupt:
        print("\n[STOP] 사용자 인터럽트")
    finally:
        lgpio.gpiochip_close(h)