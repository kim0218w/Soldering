import paho.mqtt.client as mqtt
import time
from webcam import run_webcam
from maping import run_mapping
from predict import run_predict

# === MQTT 설정 ===
BROKER_IP = "192.168.0.21"   # 브로커 IP (공유기에서 카메라 RPi IP로 설정 가능)
COMMAND_TOPIC = "command/robotarm"
STATUS_TOPIC = "status/robotarm"

# MQTT 클라이언트 생성
client = mqtt.Client()

def on_message(client, userdata, msg):
    data = msg.payload.decode()
    print(f"[라즈베리파이B 메시지 수신] {data}")

    if data == "납땜 완료":
        print("📷 카메라 촬영 및 AI 판독 시작...")
        saved = run_webcam()   # 웹캠으로 이미지 저장
        if saved:
            run_predict(saved)  # 저장한 이미지 분류
        else:
            print("⚠️ 이미지 저장 실패")

# 콜백 등록
client.on_message = on_message
client.connect(BROKER_IP, 1883)
client.subscribe(STATUS_TOPIC)
client.loop_start()

# === Controller 메뉴 ===
def controller_menu():
    while True:
        print("\n=== Controller Menu ===")
        print("1. PCB 매핑 실행")
        print("2. YOLO 웹캠 실행")
        print("3. 카메라 촬영 및 AI 판독")
        print("4. 로봇팔 작업 시작 (신호 전송)")
        print("5. 전체 실행 (매핑→YOLO→AI→로봇팔)")
        print("6. 종료")
        print("========================")

        choice = input("선택: ").strip()

        if choice == "1":
            run_mapping()

        elif choice == "2":
            run_webcam()

        elif choice == "3":
            saved = run_webcam()
            if saved:
                run_predict(saved)

        elif choice == "4":
            print("👉 로봇팔 시작 신호 전송: OK")
            client.publish(COMMAND_TOPIC, "OK")

        elif choice == "5":
            run_mapping()
            saved = run_webcam()
            if saved:
                run_predict(saved)
            print("👉 로봇팔 시작 신호 전송: OK")
            client.publish(COMMAND_TOPIC, "OK")

        elif choice == "6":
            print("종료합니다.")
            break

        else:
            print("⚠️ 잘못된 선택")

if __name__ == "__main__":
    try:
        controller_menu()
    except KeyboardInterrupt:
        print("\n종료 (Ctrl+C)")
    finally:
        client.loop_stop()
        client.disconnect()
