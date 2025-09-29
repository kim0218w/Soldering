import paho.mqtt.client as mqtt
import time
import runmot  # 모터 제어 코드

BROKER_IP = "192.168.0.21"
COMMAND_TOPIC = "command/robotarm"
STATUS_TOPIC = "status/robotarm"

client = mqtt.Client()

def on_message(client, userdata, msg):
    cmd = msg.payload.decode()
    print(f"[라즈베리파이A 명령 수신] {cmd}")

    if cmd == "OK":
        print("🤖 로봇팔 동작 시작")
        runmot.run_motors()  # runmot.py 내부 제어 함수 실행
        time.sleep(5)        # 납땜 시간 시뮬레이션
        print("납땜 완료 → 카메라 RPi에 보고")
        client.publish(STATUS_TOPIC, "납땜 완료")

client.on_message = on_message
client.connect(BROKER_IP, 1883)
client.subscribe(COMMAND_TOPIC)
client.loop_forever()
