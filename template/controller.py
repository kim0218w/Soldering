# controller.py (라즈베리파이 A: 카메라)
import subprocess
import time
import paho.mqtt.client as mqtt
from webcam import run_webcam
from predict import run_predict

# === SSH 설정 ===
ROBOT_IP = "192.168.0.22"   # 2라파5 IP (수정 필요)
ROBOT_USER = "pi"           # 2라파5 사용자 계정
ROBOT_FILE = "/home/pi/projects/robot/robotarm.py"  # 2라파5에서 robotarm.py의 실제 경로로 수정하세요

# === MQTT 설정 ===
BROKER_IP = "192.168.0.21"   # 브로커가 되는 RPi IP (보통 카메라 RPi 자체)
COMMAND_TOPIC = "command/robotarm"
STATUS_TOPIC = "status/robotarm"

client = mqtt.Client()

def on_message(client, userdata, msg):
    data = msg.payload.decode()
    print(f"[로봇팔 상태 수신] {data}")

    if data == "납땜 완료":
        print("📷 카메라 촬영 및 AI 판독 시작...")
        saved = run_webcam()   # YOLO 웹캠으로 이미지 촬영
        if saved:
            run_predict(saved)  # 촬영 이미지 분류
        else:
            print("⚠️ 이미지 저장 실패")

def start_robotarm_remote():
    # SSH를 통해 2라파5에서 robotarm.py 실행
    cmd = f'ssh {ROBOT_USER}@{ROBOT_IP} "python3 {ROBOT_FILE}"'
    print(f"👉 로봇팔 실행 명령 전송: {cmd}")
    subprocess.Popen(cmd, shell=True)

if __name__ == "__main__":
    # 1. MQTT 초기화
    client.on_message = on_message
    client.connect(BROKER_IP, 1883)
    client.subscribe(STATUS_TOPIC)
    client.loop_start()

    # 2. 원격에서 robotarm.py 실행
    start_robotarm_remote()
    time.sleep(3)  # robotarm.py가 실행될 시간을 조금 줌

    # 3. 로봇팔 시작 신호 전송
    print("👉 로봇팔 시작 신호 전송: OK")
    client.publish(COMMAND_TOPIC, "OK")

    try:
        while True:
            time.sleep(1)  # MQTT 수신 대기
    except KeyboardInterrupt:
        print("\n종료 (Ctrl+C)")
    finally:
        client.loop_stop()
        client.disconnect()
