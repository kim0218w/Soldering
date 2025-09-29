콘텐츠로 건너뛰기
채팅 기록

나의 말:
nema24 tb6600이 4개 연결 됐을 때 전류와 전압을 계산해봐
ChatGPT의 말:

23s 동안 생각함
좋아요. “NEMA24 스텝모터 × 4개를 TB6600 드라이버 4개에 각각 물렸을 때 전원(전압/전류)을 어떻게 잡느냐”를 간단 공식 + 예시로 정리해드릴게요.

1) 전압(PSU Voltage)
TB6600 권장 입력: 보통 24 V ~ 36 V(드라이버 스펙 상한 내에서).

선택 기준: 전압이 높을수록 고속 토크/속도 여유가 생깁니다. 일반적으로 24 V가 무난, 속도 여유가 더 필요하면 36 V.

모터 정격 전압은 ‘코일 저항 × 정격전류’로 낮게 나오지만, 초퍼 드라이버(TB6600)는 정격전류 기준으로 전압을 높게 써도 OK입니다(드라이버가 전류를 제한).

2) 전류(PSU Current) 계산 공식
초퍼 드라이버 사용 시 전원에서 끌어오는 평균 전류는 모터 정격전류 합보다 작습니다. 보수적으로 아래 경험 법칙을 많이 씁니다.

PSU 전류 추정식(경험칙):

I
PSU
≈
0.67
×
I
phase
×
N
motors
I 
PSU
​
 ≈0.67×I 
phase
​
 ×N 
motors
​
 
I
phase
I 
phase
​
 : 모터 정격(또는 드라이버 설정) 전류/상(A)

N
motors
=
4
N 
motors
​
 =4

마지막에 여유 20~50% 더하세요(전원·배선 여유/동시부하 대비).

왜 0.67?
미세스텝에서 두 상이 번갈아/동시에 부분적으로 도통되며, 드라이버의 전류 리사이클링 특성 때문에 전원에서 보는 평균 전류가 상전류의 약 2/3 수준인 경우가 많습니다. (보수적으로 잡고, 여유분 추가가 핵심!)

3) 예시 계산
예시 A) NEMA24 = 3.0 A/상
4개 모터, 
I
phase
=
3.0
I 
phase
​
 =3.0 A

기본 추정: 
0.67
×
3.0
×
4
=
8.04
0.67×3.0×4=8.04 A

여유 +30% → 약 10.5 A

권장 PSU: 24 V 12 A (또는 24 V 15 A)

전력 예산: 
P
≈
24
×
10.5
≈
252
P≈24×10.5≈252 W (12 A PSU면 288 W급)

예시 B) NEMA24 = 4.2 A/상
기본 추정: 
0.67
×
4.2
×
4
=
11.26
0.67×4.2×4=11.26 A

여유 +30% → 약 14.6 A

권장 PSU: 24 V 15 A (여유 넉넉히 24 V 20 A도 좋음)

전력 예산: 
P
≈
24
×
14.6
≈
350
P≈24×14.6≈350 W (15–20 A PSU 권장)

4) 드라이버 설정 및 주의
TB6600 전류 스위치를 모터 **정격전류(또는 그 이하)**로 설정하세요. (TB6600은 통상 최대 ~4.5 A 피크 / ~3.5 A RMS 수준이므로, 4 A급 모터는 살짝 낮춰 쓰는 게 안전합니다.)

PSU는 병렬 배선으로 TB6600 네 개에 공통 공급(굵은 배선/스타배선 권장).

방열/냉각 필수(드라이버 히트싱크, 팬).

EMI/노이즈 대비로 PSU-드라이버-모터 간 그라운드 정리, 실드 케이블(필요시), 모터-드라이버 간 배선 짧고 굵게.

원하는 정확한 수치를 뽑아드리려면 **모터 데이터시트의 정격전류(상당)**만 알려주시면 됩니다. 위 공식에 그대로 대입해서 PSU 전류와 권장 전원 용량을 바로 계산해 드릴게요.

나의 말:
raceback (most recent call last):
  File "/home/pi/Desktop/soldering/nema2.py", line 26, in <module>
    lgpio.gpio_claim_output(h, motor["step"])
  File "/usr/lib/python3/dist-packages/lgpio.py", line 781, in gpio_claim_output
    return _u2i(_lgpio._gpio_claim_output(handle&0xffff, lFlags, gpio, level))
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3/dist-packages/lgpio.py", line 458, in _u2i
    raise error(error_text(v))
lgpio.error: 'GPIO busy'
오류 원인찾아줘
ChatGPT의 말:
에러 메시지의 핵심은 다음 부분이에요:

lgpio.error: 'GPIO busy'
즉, lgpio.gpio_claim_output()로 지정하려는 GPIO 핀이 이미 사용 중이라는 뜻입니다. 원인을 정리해보면:

가능한 원인
다른 프로세스에서 해당 GPIO를 이미 사용 중

예: 같은 Python 코드가 백그라운드에서 여전히 실행 중이거나, 이전 실행이 완전히 종료되지 않은 경우.

pigpiod, gpio 같은 다른 드라이버/데몬이 점유하고 있는 경우도 있음.

같은 코드에서 중복으로 claim

예: 루프 안에서 gpio_claim_output()을 반복 호출하거나, 한 핀을 여러 번 잡으려는 경우.

올바른 핀 번호 방식 사용 안 함

Raspberry Pi는 BCM 번호와 보드 물리 번호가 다릅니다. lgpio는 기본적으로 BCM(GPIO) 번호를 사용하므로 혼동 시 에러가 날 수 있음.

종료 시 핀 해제가 안 됨

프로그램이 비정상 종료되면 커널이 여전히 해당 핀을 “사용 중”으로 남겨둘 수 있습니다.

해결 방법
프로세스 확인 & 정리

ps aux | grep python
남아 있는 Python 프로세스를 kill로 종료하세요.

핀 번호 확인

motor["step"]에 들어가는 값이 Raspberry Pi의 BCM 핀 번호인지 확인하세요.

예: GPIO17 → 숫자 17 사용.

중복 claim 방지

코드에서 같은 핀을 여러 번 gpio_claim_output() 하지 않았는지 확인하세요.

루프 바깥에서 한 번만 claim 하고, 루프 안에서는 gpio_write()만 하도록 고치세요.

lgpio.gpio_claim_output(h, motor["step"], 0)  # 초기 1회 claim
for i in range(100):
    lgpio.gpio_write(h, motor["step"], 1)
    lgpio.gpio_write(h, motor["step"], 0)
프로그램 종료 시 핀 해제

종료 전에 꼭 lgpio.gpio_free(h, pin) 또는 lgpio.gpiochip_close(h) 호출하세요.

👉 질문: 혹시 nema2.py 코드에서 같은 핀을 여러 번 claim하고 계신가요, 아니면 실행 중인 다른 모터 제어 코드가 남아 있을 수도 있는데 확인해드릴까요?

나의 말:
# stepper_4motor_scurve.py
import lgpio
import time
import math

# --- 모터 핀 설정 ---
step_pin_1, dir_pin_1 = 17, 27
step_pin_2, dir_pin_2 = 18, 23
step_pin_3, dir_pin_3 = 22, 24
step_pin_4, dir_pin_4 = 25, 5

MOTORS = [
    {"step": step_pin_1, "dir": dir_pin_1},
    {"step": step_pin_2, "dir": dir_pin_2},
    {"step": step_pin_3, "dir": dir_pin_3},
    {"step": step_pin_4, "dir": dir_pin_4},
]

# --- 스텝모터 파라미터 ---
STEPS_PER_REV = 200              # 1회전 = 200스텝 (마이크로스텝 설정에 맞게 수정)
DEG_PER_STEP = 360.0 / STEPS_PER_REV

# --- GPIO 초기화 ---
h = lgpio.gpiochip_open(0)
for motor in MOTORS:
    lgpio.gpio_claim_output(h, motor["step"])
    lgpio.gpio_claim_output(h, motor["dir"])

# --- S-curve 프로파일 ---
def s_curve_profile(steps: int):
    return [(1 - math.cos(math.pi * i / (steps - 1))) / 2 for i in range(steps)]

# --- 모터 제어 함수 ---
def move_stepper(motor, current_angle, target_angle, duration=1.0):
    step_pin, dir_pin = motor["step"], motor["dir"]

    delta_angle = target_angle - current_angle
    steps_needed = int(abs(delta_angle) / DEG_PER_STEP)

    if steps_needed == 0:
        return target_angle

    # 방향 설정
    direction = 1 if delta_angle > 0 else 0
    lgpio.gpio_write(h, dir_pin, direction)

    # S-curve 생성
    profile = s_curve_profile(steps_needed if steps_needed > 1 else 2)

    for _ in profile:
        lgpio.gpio_write(h, step_pin, 1)
        time.sleep(duration / steps_needed / 2)
        lgpio.gpio_write(h, step_pin, 0)
        time.sleep(duration / steps_needed / 2)

    return target_angle

# --- 메인 루프 ---
if __name__ == "__main__":
    current_angles = [0, 0, 0, 0]  # 1~4번 모터 현재 각도

    try:
        while True:
            raw = input("각도 입력 (예: 90 45 180 0): ")
            target_angles = list(map(int, raw.split()))

            if len(target_angles) != 4:
                print("⚠️ 1~4번 모터 각도 4개를 입력해야 합니다.")
                continue

            for i in range(4):
                print(f"👉 {i+1}번 모터 {current_angles[i]}° → {target_angles[i]}° 이동 중...")
                current_angles[i] = move_stepper(MOTORS[i], current_angles[i], target_angles[i], duration=2.0)

    except KeyboardInterrupt:
        print("\n정지: GPIO 해제")
        lgpio.gpiochip_close(h)
이거 오류 찾아줘
ChatGPT의 말:
좋습니다 👍 올려주신 stepper_4motor_scurve.py 코드에서 GPIO busy 오류가 나는 이유를 살펴볼게요.

🔎 문제 원인
lgpio.gpio_claim_output() 함수 시그니처는 다음과 같아요:

lgpio.gpio_claim_output(handle, flags, gpio, level)
즉, **4개의 인자(handle, flags, gpio 번호, 초기 출력 레벨)**를 줘야 하는데, 코드에서는:

lgpio.gpio_claim_output(h, motor["step"])
lgpio.gpio_claim_output(h, motor["dir"])
처럼 2개만 넣었죠.
이 경우 내부적으로 잘못된 인자가 들어가면서 드라이버가 핀을 제대로 claim 하지 못하고, 결과적으로 GPIO busy 같은 오류가 납니다.

✅ 수정 방법
각 핀 claim할 때 flags와 초기 출력 레벨을 함께 지정해 주세요. 보통 flags는 0, level은 0(LOW)으로 시작하면 됩니다.

수정된 부분
# --- GPIO 초기화 ---
h = lgpio.gpiochip_open(0)
for motor in MOTORS:
    lgpio.gpio_claim_output(h, 0, motor["step"], 0)  # step 핀 초기화
    lgpio.gpio_claim_output(h, 0, motor["dir"], 0)   # dir 핀 초기화
🔧 추가 권장 사항
코드 종료 시 핀 해제
현재는 gpiochip_close(h)만 호출하는데, 개별 핀을 해제하려면 lgpio.gpio_free(h, pin)을 호출하는 것이 더 안전합니다.

for motor in MOTORS:
    lgpio.gpio_free(h, motor["step"])
    lgpio.gpio_free(h, motor["dir"])
lgpio.gpiochip_close(h)
동시 구동 고려
지금 구조는 1번 → 2번 → 3번 → 4번 모터 순차 실행이에요. 4개를 동시에 구동하려면 threading이나 asyncio를 써야 합니다.

S-curve 프로파일 활용
현재는 프로파일 값을 계산하지만, 실제로 delay에 반영하지 않고 duration / steps_needed로만 쓰고 있어요.
원래 의도라면 profile 값(가속/감속 비율)을 delay 계산에 곱해주어야 합니다.

👉 정리하면, 오류의 직접적인 원인은 gpio_claim_output() 인자를 잘못 준 것이고, 아래처럼 고치면 해결될 겁니다:

lgpio.gpio_claim_output(h, 0, motor["step"], 0)
lgpio.gpio_claim_output(h, 0, motor["dir"], 0)
원하시면 제가 S-curve 프로파일까지 실제 가속/감속에 반영되도록 코드 리팩토링도 해드릴까요?

나의 말:
리펙토링
ChatGPT의 말:
좋습니다 👍 올려주신 코드를 리팩토링해서

gpio_claim_output 호출을 올바르게 수정

S-curve 프로파일을 실제 속도(딜레이)에 반영

종료 시 핀 해제 처리

까지 반영한 버전을 드릴게요.

✅ 리팩토링된 코드
# stepper_4motor_scurve_refactored.py
import lgpio
import time
import math

# --- 모터 핀 설정 (BCM 번호) ---
step_pin_1, dir_pin_1 = 17, 27
step_pin_2, dir_pin_2 = 18, 23
step_pin_3, dir_pin_3 = 22, 24
step_pin_4, dir_pin_4 = 25, 5

MOTORS = [
    {"step": step_pin_1, "dir": dir_pin_1},
    {"step": step_pin_2, "dir": dir_pin_2},
    {"step": step_pin_3, "dir": dir_pin_3},
    {"step": step_pin_4, "dir": dir_pin_4},
]

# --- 스텝모터 파라미터 ---
STEPS_PER_REV = 200              # 1회전 = 200스텝 (마이크로스텝에 맞게 수정)
DEG_PER_STEP = 360.0 / STEPS_PER_REV

# --- GPIO 초기화 ---
h = lgpio.gpiochip_open(0)
for motor in MOTORS:
    lgpio.gpio_claim_output(h, 0, motor["step"], 0)  # step 핀 LOW로 초기화
    lgpio.gpio_claim_output(h, 0, motor["dir"], 0)   # dir 핀 LOW로 초기화

# --- S-curve 프로파일 생성 ---
def s_curve_profile(steps: int):
    """
    steps 길이의 S-curve 가속/감속 비율 배열을 생성.
    (cosine 기반: 0 → 1 → 0 속도 변화)
    """
    return [(1 - math.cos(math.pi * i / (steps - 1))) / 2 for i in range(steps)]

# --- 모터 제어 함수 ---
def move_stepper(motor, current_angle, target_angle, duration=1.0):
    step_pin, dir_pin = motor["step"], motor["dir"]

    delta_angle = target_angle - current_angle
    steps_needed = int(abs(delta_angle) / DEG_PER_STEP)

    if steps_needed == 0:
        return target_angle

    # 방향 설정
    direction = 1 if delta_angle > 0 else 0
    lgpio.gpio_write(h, dir_pin, direction)

    # S-curve 프로파일 생성
    profile = s_curve_profile(steps_needed if steps_needed > 1 else 2)

    # 전체 이동 시간을 profile에 따라 분배
    for weight in profile:
        delay = (duration / steps_needed) * (1 + (1 - weight))  # 가속/감속 반영
        lgpio.gpio_write(h, step_pin, 1)
        time.sleep(delay / 2)
        lgpio.gpio_write(h, step_pin, 0)
        time.sleep(delay / 2)

    return target_angle

# --- 메인 루프 ---
if __name__ == "__main__":
    current_angles = [0, 0, 0, 0]  # 1~4번 모터 현재 각도

    try:
        while True:
            raw = input("각도 입력 (예: 90 45 180 0): ")
            target_angles = list(map(int, raw.split()))

            if len(target_angles) != 4:
                print("⚠️ 1~4번 모터 각도 4개를 입력해야 합니다.")
                continue

            for i in range(4):
                print(f"👉 {i+1}번 모터 {current_angles[i]}° → {target_angles[i]}° 이동 중...")
                current_angles[i] = move_stepper(MOTORS[i], current_angles[i], target_angles[i], duration=2.0)

    except KeyboardInterrupt:
        print("\n정지: GPIO 해제")
        for motor in MOTORS:
            lgpio.gpio_free(h, motor["step"])
            lgpio.gpio_free(h, motor["dir"])
        lgpio.gpiochip_close(h)
🔑 변경 사항 요약
gpio_claim_output(h, 0, pin, 0) → 올바른 호출로 수정.

s_curve_profile() 반환값을 딜레이 가중치로 반영.

시작은 길게(느리게), 중간은 짧게(빠르게), 끝은 다시 길게 → 부드러운 가감속.

종료 시 gpio_free() 추가하여 GPIO 핀 해제 확실히 처리.

👉 지금 구조는 여전히 4개 모터를 순차 제어합니다.
만약 4개 모터를 동시에 S-curve로 구동하고 싶으세요, 아니면 지금처럼 개별적으로만 움직여도 괜찮으세요?

나의 말:
Traceback (most recent call last): File "/home/pi/Desktop/soldering/nema.py", line 85, in lgpio.gpio_claim_output(h, dir_pin, 0) File "/usr/lib/python3/dist-packages/lgpio.py", line 781, in gpio_claim_output return _u2i(_lgpio._gpio_claim_output(handle&0xffff, lFlags, gpio, level)) ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ File "/usr/lib/python3/dist-packages/lgpio.py", line 458, in _u2i raise error(error_text(v)) lgpio.error: 'GPIO busy'
이렇게 오류뜨는데 원인 찾아봐
ChatGPT의 말:
네, 이번 에러 로그를 보면 핵심은 다시 lgpio.error: 'GPIO busy' 입니다.
그런데 이번에는 함수 호출이 이렇게 찍혔네요:

lgpio.gpio_claim_output(h, dir_pin, 0)
🔎 문제 포인트
gpio_claim_output()의 올바른 시그니처는:

lgpio.gpio_claim_output(handle, flags, gpio, level)
즉, 인자 4개가 필요합니다:

handle → gpiochip_open()으로 얻은 핸들

flags → 보통 0

gpio → BCM GPIO 번호

level → 초기 출력값 (0 or 1)

그런데 현재 호출은:

lgpio.gpio_claim_output(h, dir_pin, 0)
👉 여기서 dir_pin이 flags 자리에 들어가 버렸고,
그 뒤의 0이 gpio 번호 자리에 들어가 버린 것이에요.
즉, 완전히 잘못된 순서라서 드라이버가 말도 안 되는 핀을 claim하려고 하다가 "이미 사용 중" 에러를 던진 겁니다.

✅ 해결 방법
고쳐야 할 올바른 호출 예시는 다음과 같습니다:

lgpio.gpio_claim_output(h, 0, dir_pin, 0)
즉, 항상 0 (flags) → 핀 번호 → 초기 출력 레벨 순서로 넣어야 합니다.

🚑 추가 점검
혹시 코드 일부는 lgpio.gpio_claim_output(h, motor["step"]) 이런 식으로 잘못 써놓으셨을 수도 있습니다.
전부 4인자 방식으로 바꿔야 합니다.

프로그램을 강제 종료(Ctrl+C)한 후에도 GPIO가 "busy"로 남을 수 있습니다. 그럴 땐:

sudo reboot
하거나, 코드에서 lgpio.gpio_free(h, pin) → lgpio.gpiochip_close(h)를 꼭 실행해 주세요.

👉 질문: 지금은 모터 1개 제어 중인데도 GPIO busy가 뜨나요, 아니면 여러 모터 핀을 동시에 claim할 때 충돌이 생기는 건가요?

나의 말:
순차적으로 각도를 넣고 순차적으로 실행하고 싶다 코드 수정해라
ChatGPT의 말:

59s 동안 생각함
좋아요! “각도를 하나씩 입력하면 그 모터가 바로 움직이고, 다음 모터로 넘어가는” 순차 입력 → 순차 실행 형태로 리팩토링했어요.
gpio_claim_output 인자도 올바른 순서(핸들, 플래그, 핀, 초기레벨)로 수정했고, S-curve를 실제 속도 가중치로 적용해 전체 이동시간이 duration에 맞게 분배되도록 했습니다. 종료 시에는 핀도 확실히 해제합니다.

# stepper_4motor_scurve_sequential.py
import lgpio
import time
import math

# --- 설정 ---
# BCM 핀 번호 사용
step_pin_1, dir_pin_1 = 17, 27
step_pin_2, dir_pin_2 = 18, 23
step_pin_3, dir_pin_3 = 22, 24
step_pin_4, dir_pin_4 = 25, 5

MOTORS = [
    {"step": step_pin_1, "dir": dir_pin_1, "name": "모터1"},
    {"step": step_pin_2, "dir": dir_pin_2, "name": "모터2"},
    {"step": step_pin_3, "dir": dir_pin_3, "name": "모터3"},
    {"step": step_pin_4, "dir": dir_pin_4, "name": "모터4"},
]

# 마이크로스텝 설정에 맞게 변경 (예: TB6600에서 1/8 이면 200*8)
MICROSTEP = 1
STEPS_PER_REV = 200 * MICROSTEP
DEG_PER_STEP = 360.0 / STEPS_PER_REV

# 하드웨어 타이밍(보수적)
DIR_SETUP_S = 0.000010     # DIR 바꾼 뒤 STEP 주기전 최소 준비시간(10us)
STEP_PULSE_MIN_S = 0.000010  # STEP High/Low 최소 펄스(10us)

def gpio_init():
    h = lgpio.gpiochip_open(0)
    for m in MOTORS:
        lgpio.gpio_claim_output(h, 0, m["step"], 0)  # (handle, flags, gpio, level)
        lgpio.gpio_claim_output(h, 0, m["dir"], 0)
    return h

def gpio_cleanup(h):
    # 개별 핀 해제 후 칩 핸들 닫기
    for m in MOTORS:
        try:
            lgpio.gpio_free(h, m["step"])
            lgpio.gpio_free(h, m["dir"])
        except Exception:
            pass
    try:
        lgpio.gpiochip_close(h)
    except Exception:
        pass

# S-curve: 0→1로 올라가는 코사인 기반 프로파일
def s_curve_profile(steps: int):
    if steps <= 1:
        return [1.0]
    return [(1 - math.cos(math.pi * i / (steps - 1))) / 2 for i in range(steps)]

def move_stepper(h, motor, current_angle, target_angle, duration=1.0):
    step_pin, dir_pin = motor["step"], motor["dir"]

    delta_angle = target_angle - current_angle
    steps_needed = int(round(abs(delta_angle) / DEG_PER_STEP))

    if steps_needed == 0:
        return target_angle

    # 방향 설정 (DIR setup time 준수)
    direction = 1 if delta_angle > 0 else 0
    lgpio.gpio_write(h, dir_pin, direction)
    time.sleep(DIR_SETUP_S)

    # 속도 가중치 계산 (S-curve) — 최소 속도 바닥값 EPS로 무한대 주기 방지
    EPS = 0.15  # 0.0~1.0 사이, 클수록 시동/정지 구간이 빠름
    base_profile = s_curve_profile(steps_needed)
    speed_weights = [EPS + (1.0 - EPS) * v for v in base_profile]  # 모두 > 0

    # 총 duration을 각 스텝 주기로 정확히 분배:
    # period_i ∝ 1 / speed_i  ->  sum_i(period_i) = duration
    inv_sum = sum(1.0 / w for w in speed_weights)
    k = duration / inv_sum

    for w in speed_weights:
        period = max(k / w, STEP_PULSE_MIN_S * 2)   # 하프 펄스 2배 이상 확보
        high_t = max(STEP_PULSE_MIN_S, period / 2)  # 하이 펄스
        low_t  = max(STEP_PULSE_MIN_S, period - high_t)

        lgpio.gpio_write(h, step_pin, 1)
        time.sleep(high_t)
        lgpio.gpio_write(h, step_pin, 0)
        time.sleep(low_t)

    return target_angle

def main():
    h = gpio_init()
    current_angles = [0.0, 0.0, 0.0, 0.0]

    print("순차 입력 모드: 모터1 → 모터2 → 모터3 → 모터4 순서로 각도 입력 후 즉시 동작합니다.")
    print("입력 예) 90   (엔터만 치면 건너뜀, q 입력 시 종료)")
    try:
        while True:
            for i, m in enumerate(MOTORS):
                raw = input(f"{m['name']} 목표 각도? (현재 {current_angles[i]:.1f}°) : ").strip()
                if raw.lower() in ("q", "quit", "exit"):
                    raise KeyboardInterrupt
                if raw == "":
                    print(f" - {m['name']} 건너뜀")
                    continue
                try:
                    target = float(raw)
                except ValueError:
                    print("⚠️ 숫자를 입력하세요. (예: 90, -45)")
                    continue

                print(f"👉 {m['name']} {current_angles[i]:.1f}° → {target:.1f}° 이동 중...")
                # 필요 시 모터별 duration 다르게 주고 싶으면 인자로 전달
                current_angles[i] = move_stepper(h, m, current_angles[i], target, duration=2.0)
                print(f"✅ {m['name']} 완료: 현재 {current_angles[i]:.1f}°")

    except KeyboardInterrupt:
        print("\n정지: GPIO 해제 중...")
    finally:
        gpio_cleanup(h)
        print("GPIO 해제 완료. 프로그램 종료.")

if __name__ == "__main__":
    main()
포인트
순차 입력 → 즉시 실행: 모터1 각도 입력 → 실행 → 모터2 입력 → 실행 … 반복.

gpio_claim_output(h, 0, pin, 0)처럼 인자 순서를 반드시 지켰습니다.

S-curve 속도 가중치로 각 스텝 주기를 계산해 **총 시간(duration)**이 정확히 맞도록 분배합니다.

TB6600의 DIR setup/STEP 최소 펄스를 고려해 마이크로초 단위 안전 여유를 줬습니다.

종료/예외 시 모든 핀을 gpio_free 후 gpiochip_close로 정리.

필요하면 “4개 모터를 동시에” 같은 동작(스레드 기반 병렬 구동) 버전도 만들어 드릴게요.

나의 말:
step_pin_1, dir_pin_1 = 17, 18
step_pin_2, dir_pin_2 = 27, 22
step_pin_3, dir_pin_3 = 23, 24
step_pin_4, dir_pin_4 = 10, 9
핀번호 이걸로 변경
ChatGPT의 말:
알겠습니다 👍 요청하신 새로운 핀 번호로 코드를 수정해드릴게요.

✅ 수정된 핀 매핑
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
🔧 전체 코드에 적용한 버전
아래는 앞서 드린 순차 입력/순차 실행 코드에서 핀 번호만 교체한 것입니다.

# stepper_4motor_scurve_sequential.py
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

# 마이크로스텝 설정 (TB6600 DIP 스위치에 맞게 수정)
MICROSTEP = 1
STEPS_PER_REV = 200 * MICROSTEP
DEG_PER_STEP = 360.0 / STEPS_PER_REV

# 하드웨어 타이밍
DIR_SETUP_S = 0.000010       # 10us
STEP_PULSE_MIN_S = 0.000010  # 10us

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

def s_curve_profile(steps: int):
    if steps <= 1:
        return [1.0]
    return [(1 - math.cos(math.pi * i / (steps - 1))) / 2 for i in range(steps)]

def move_stepper(h, motor, current_angle, target_angle, duration=1.0):
    step_pin, dir_pin = motor["step"], motor["dir"]

    delta_angle = target_angle - current_angle
    steps_needed = int(round(abs(delta_angle) / DEG_PER_STEP))
    if steps_needed == 0:
        return target_angle

    direction = 1 if delta_angle > 0 else 0
    lgpio.gpio_write(h, dir_pin, direction)
    time.sleep(DIR_SETUP_S)

    EPS = 0.15
    base_profile = s_curve_profile(steps_needed)
    speed_weights = [EPS + (1.0 - EPS) * v for v in base_profile]

    inv_sum = sum(1.0 / w for w in speed_weights)
    k = duration / inv_sum

    for w in speed_weights:
        period = max(k / w, STEP_PULSE_MIN_S * 2)
        high_t = max(STEP_PULSE_MIN_S, period / 2)
        low_t = max(STEP_PULSE_MIN_S, period - high_t)

        lgpio.gpio_write(h, step_pin, 1)
        time.sleep(high_t)
        lgpio.gpio_write(h, step_pin, 0)
        time.sleep(low_t)

    return target_angle

def main():
    h = gpio_init()
    current_angles = [0.0, 0.0, 0.0, 0.0]

    print("순차 입력 모드: 모터1 → 모터2 → 모터3 → 모터4 순서로 각도 입력 후 즉시 동작합니다.")
    print("입력 예) 90   (엔터만 치면 건너뜀, q 입력 시 종료)")
    try:
        while True:
            for i, m in enumerate(MOTORS):
                raw = input(f"{m['name']} 목표 각도? (현재 {current_angles[i]:.1f}°) : ").strip()
                if raw.lower() in ("q", "quit", "exit"):
                    raise KeyboardInterrupt
                if raw == "":
                    print(f" - {m['name']} 건너뜀")
                    continue
                try:
                    target = float(raw)
                except ValueError:
                    print("⚠️ 숫자를 입력하세요. (예: 90, -45)")
                    continue

                print(f"👉 {m['name']} {current_angles[i]:.1f}° → {target:.1f}° 이동 중...")
                current_angles[i] = move_stepper(h, m, current_angles[i], target, duration=2.0)
                print(f"✅ {m['name']} 완료: 현재 {current_angles[i]:.1f}°")

    except KeyboardInterrupt:
        print("\n정지: GPIO 해제 중...")
    finally:
        gpio_cleanup(h)
        print("GPIO 해제 완료. 프로그램 종료.")

if __name__ == "__main__":
    main()
👉 이렇게 하면 새로운 핀 번호에 맞게 모터 4개를 순차 입력·순차 실행할 수 있습니다.

원하시면 제가 **“동시에 4개 모터를 병렬로 실행”**하는 코드 버전도 만들어드릴까요?

나의 말:
모터를 하나돌리고 끄고 하나돌리고 끄고 하자
ChatGPT의 말:
좋습니다 👍 말씀하신 건 모터를 한 번씩 돌리고 → 멈추고 → 다음 모터 돌리고 → 멈추고… 이런 “순차 구동 + 중간에 끄기(Idle)” 동작이네요.
기존 코드를 조금 단순화해서 각 모터를 순서대로 돌리고, 돌린 뒤에는 끄도록(step 신호 없음 + dir도 LOW 유지) 수정해드리겠습니다.

✅ 리팩토링 코드 (모터 순차 구동 + 끄기)
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
                print(f"👉 {m['name']} 시계 방향 회전 중...")
                move_steps(h, m, steps=200, direction=1, delay=0.002)  # 200스텝(=1회전)
                print(f"✅ {m['name']} 완료, 모터 OFF")
                time.sleep(1)  # 모터 끈 상태에서 잠시 대기

                print(f"👉 {m['name']} 반시계 방향 회전 중...")
                move_steps(h, m, steps=200, direction=0, delay=0.002)
                print(f"✅ {m['name']} 완료, 모터 OFF")
                time.sleep(1)

    except KeyboardInterrupt:
        print("\n정지: GPIO 해제 중...")
    finally:
        gpio_cleanup(h)
        print("GPIO 해제 완료. 프로그램 종료.")

if __name__ == "__main__":
    main()
🔑 동작 설명
모터1을 시계 방향 한 바퀴 → 멈춤,

잠시 대기 후 반시계 방향 한 바퀴 → 멈춤,

다음 모터(모터2, 3, 4) 순서대로 반복.

각 모터 돌린 뒤에는 STEP=0, DIR=0으로 내려주어 드라이버가 Idle 상태가 됩니다.

👉 혹시 “모터를 돌리고 완전히 전원(전류)까지 끄고 싶다”는 의미일까요? (즉, 드라이버 Enable 핀을 제어해서 전류 자체를 차단하는 방식)
아니면 지금처럼 STEP 신호를 멈추고 DIR을 0으로 두는 것으로 충분할까요?

나의 말:
ㅇㅇㅇ 잔류전원 자체를 차단하는 방식으로 하고싶어
ChatGPT의 말:
좋습니다 👍 말씀하신 건 모터 드라이버(TB6600)의 Enable 핀(보통 EN+, EN-)을 제어해서 코일 전류를 완전히 차단하는 방식이에요.

🔎 원리
TB6600은 EN 핀이 활성화(Enable) 상태일 때만 모터에 전류를 흘립니다.

일반적으로 EN 핀 LOW → 활성화(모터 구동됨), EN 핀 HIGH → 비활성화(모터 코일 전류 차단) 로 동작합니다.
(드라이버 모델/세팅에 따라 반대일 수도 있으니 데이터시트 확인 필요합니다.)

따라서 모터를 돌릴 때 → Enable ON, 끝나면 Enable OFF 로 제어하면 잔류전류가 사라집니다.

✅ 코드 수정 예시 (Enable 핀 제어 추가)
핀 번호에 Enable 핀을 하나씩 지정한다고 가정해볼게요 (예: BCM 6, 13, 19, 26).
👉 실제 라즈베리파이 배선에 맞춰 바꾸시면 됩니다.

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
🔑 정리
Enable 핀 추가: 모터가 필요할 때만 켜고, 끝나면 꺼서 잔류전류 완전 차단.

gpio_init()에서 EN 핀을 **기본 HIGH(Disable)**로 잡아둡니다.

move_steps()에서 돌리기 전 Enable → 돌리고 나서 Disable.

👉 질문: 지금 쓰시는 TB6600 보드에서 Enable 핀(EN+/EN-)을 라즈베리파이에 연결하실 수 있나요?
그 핀 연결 여부에 따라 실제로 “잔류전원 차단”이 가능해집니다.

나의 말:
핀두개만 사용하는 코드로 수정
ChatGPT의 말:
좋습니다 👍 말씀하신 대로라면 STEP, DIR 두 개 핀만 쓰고 Enable 핀은 연결하지 않는다는 의미네요.
즉, 모터는 항상 전원이 인가된 상태에서, STEP 신호만 줄 때만 움직이고, 멈추면 그대로 홀딩 토크(잔류전류)가 유지됩니다.

하지만 질문에서 “핀 두개만”이라고 하셨으니, STEP + DIR만 사용하는 가장 단순한 코드로 리팩토링 해드리겠습니다.

✅ STEP, DIR 두 개만 쓰는 코드
# stepper_4motor_step_dir_only.py
import lgpio
import time

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
    """STEP/DIR 두 핀만 사용해서 단순 구동"""
    step_pin, dir_pin = motor["step"], motor["dir"]

    # 방향 설정
    lgpio.gpio_write(h, dir_pin, direction)
    time.sleep(DIR_SETUP_S)

    # 지정된 스텝 수 만큼 펄스 발생
    for _ in range(steps):
        lgpio.gpio_write(h, step_pin, 1)
        time.sleep(delay/2)
        lgpio.gpio_write(h, step_pin, 0)
        time.sleep(delay/2)

def main():
    h = gpio_init()
    try:
        while True:
            for m in MOTORS:
                print(f"👉 {m['name']} 시계 방향 회전 중...")
                move_steps(h, m, steps=200, direction=1, delay=0.002)  # 200스텝
                print(f"✅ {m['name']} 완료")
                time.sleep(1)

                print(f"👉 {m['name']} 반시계 방향 회전 중...")
                move_steps(h, m, steps=200, direction=0, delay=0.002)
                print(f"✅ {m['name']} 완료")
                time.sleep(1)

    except KeyboardInterrupt:
        print("\n정지: GPIO 해제 중...")
    finally:
        gpio_cleanup(h)
        print("GPIO 해제 완료. 프로그램 종료.")

if __name__ == "__main__":
    main()
🔑 설명
필요한 핀 = STEP, DIR 두 개만 사용.

Enable 핀은 쓰지 않으므로 모터가 멈춘 뒤에도 잔류전류가 계속 흐릅니다 → 항상 홀딩토크 유지.

move_steps() 함수에서 원하는 스텝 수만큼 단순히 펄스를 발생시킵니다.

👉 만약 진짜로 “돌리고 나서 전류까지 꺼서 모터 완전히 해제”하고 싶으시면, Enable 핀을 꼭 연결해야 합니다. 지금 구조(핀 2개만 사용)에서는 전류를 차단할 수 없는데, 그래도 이 방식이면 괜찮으실까요?

나의 말:
핀은 3개 쓰고 모터를 2개만 각도 입력받고 사용하요 전원을 차단하도록 설정
ChatGPT의 말:
네 👍 이번에는 요구사항을 정리해보면:

핀은 STEP, DIR, EN → 3개 사용

모터는 2개만 제어 (각도 입력받아서 동작)

동작이 끝나면 EN 핀을 HIGH(Disable)로 해서 전류 차단

즉, 최소 구성(모터 2개 × 3핀씩)으로 제어하고, 동작 후 잔류 전류까지 꺼주는 코드입니다.

✅ 코드 예시 (모터 2개, STEP+DIR+EN)
# stepper_2motor_with_enable.py
import lgpio
import time
import math

# --- 모터 핀 설정 (BCM 번호) ---
# 예시 핀 번호: 실제 배선에 맞게 수정하세요
step_pin_1, dir_pin_1, en_pin_1 = 17, 18, 6
step_pin_2, dir_pin_2, en_pin_2 = 27, 22, 13

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
                print(" 숫자 2개를 입력하세요. 예: 90 180")
                continue

            if len(target_angles) != 2:
                print(" 모터1, 모터2 각도 2개를 입력해야 합니다.")
                continue

            for i, m in enumerate(MOTORS):
                print(f" {m['name']} {current_angles[i]:.1f}° → {target_angles[i]:.1f}° 이동 중...")
                current_angles[i] = move_to_angle(h, m, current_angles[i], target_angles[i])
                print(f" {m['name']} 완료 (전류 차단됨)")

    except KeyboardInterrupt:
        print("\n정지: GPIO 해제 중...")
    finally:
        gpio_cleanup(h)
        print("GPIO 해제 완료. 프로그램 종료.")


if __name__ == "__main__":
    main()
 동작 방식
각도 입력 → 예: 90 180 → 모터1은 90°, 모터2는 180°로 이동

모터 동작 시 EN 핀 LOW → 모터에 전류 공급

이동 완료 후 EN 핀 HIGH → 전류 차단, 잔류 토크 해제

순차 실행: 모터1 완료 → 모터2 실행

 실제 배선에서 TB6600의 EN+ / EN- 핀을 라즈베리파이 GPIO와 GND에 연결하셔야 전류 차단이 제대로 동작합니다.

원하시면 제가 TB6600 핀 배치(EN+/EN-, DIR+/DIR-, PUL+/PUL-) 기준으로 라즈베리파이 연결 예시 그림도 그려드릴까요?


개발자 모드


선택된 파일 없음선택된 파일 없음
ChatGPT는 실수를 할 수 있습니다. 중요한 정보는 재차 확인하세요.
