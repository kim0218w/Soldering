import cv2
import datetime
import os

def run_mapping(threshold=0.8):
    """
    PCB 템플릿 매칭으로 감지 여부를 확인하는 함수.
    - threshold: 매칭 유사도 임계값 (기본 0.8)
    - 반환값: PCB 감지되면 True, 종료 시까지 감지 못하면 False
    """
    save_folder = "file"
    os.makedirs(save_folder, exist_ok=True)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("카메라를 열 수 없습니다.")
        return False

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))

    recording = False
    print("카메라 실행 중. 'q' 종료, 'c' 캡처(ROI만), 'r' 녹화 토글.")

    frame_width, frame_height = 640, 480
    roi_width, roi_height = 300, 210
    roi_x1 = (frame_width - roi_width) // 2
    roi_y1 = (frame_height - roi_height) // 2
    roi_x2 = roi_x1 + roi_width
    roi_y2 = roi_y1 + roi_height

    template_path = 'template/template.png'
    template = cv2.imread(template_path)
    if template is None:
        print(f"Template 이미지 로드 실패: {template_path}")
        cap.release()
        out.release()
        return False
    template = cv2.resize(template, (roi_width, roi_height))

    pcb_detected = False

    while True:
        ret, frame = cap.read()
        if not ret:
            print("프레임을 가져올 수 없습니다.")
            break

        # ROI 표시
        cv2.rectangle(frame, (roi_x1, roi_y1), (roi_x2, roi_y2), (0, 255, 0), 2)
        roi_frame = frame[roi_y1:roi_y2, roi_x1:roi_x2]

        # Template Matching
        res = cv2.matchTemplate(roi_frame, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(res)

        if max_val >= threshold:  # PCB 감지
            filename = os.path.join(save_folder, f"pcb_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            cv2.imwrite(filename, roi_frame)
            cv2.putText(frame, "PCB DETECTED", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            print(f"PCB 감지! 자동 저장됨: {filename}")
            pcb_detected = True
            # 감지 즉시 루프 종료 → True 반환
            break

        if recording:
            out.write(frame)
            cv2.putText(frame, 'REC', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.imshow('Webcam', frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c'):
            filename = os.path.join(save_folder, f"capture_roi_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            cv2.imwrite(filename, roi_frame)
            print(f"ROI 캡처 저장: {filename}")
        elif key == ord('r'):
            recording = not recording
            print("녹화 시작" if recording else "녹화 종료")

    cap.release()
    out.release()
    cv2.destroyAllWindows()

    return pcb_detected


# 단독 실행 시 동작 확인
if __name__ == "__main__":
    detected = run_mapping()
    print("PCB 감지 결과:", detected)
