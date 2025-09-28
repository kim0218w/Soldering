"""
controller.py
- maping.py 에서 PCB 감지되면
- webcam.py 실행하여 YOLOv8 객체 검출 + 넘버링
"""

import maping
import webcam

def main():
    print("[Controller] PCB 매핑(템플릿 매칭) 시작...")
    detected = maping.run_mapping()

    if detected:
        print("[Controller] PCB 감지됨 → YOLO 객체 검출 시작")
        webcam.run_webcam()
    else:
        print("[Controller] PCB 감지되지 않음 → YOLO 실행 안 함")

if __name__ == "__main__":
    main()
