import cv2
import datetime
import os
from picamera2 import Picamera2

def run_mapping(threshold=0.8):
    save_folder = "file"
    os.makedirs(save_folder, exist_ok=True)

    picam2 = Picamera2()
    picam2.preview_configuration.main.size = (640, 480)
    picam2.preview_configuration.main.format = "RGB888"
    picam2.configure("preview")
    picam2.start()

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
        return False
    template = cv2.resize(template, (roi_width, roi_height))

    print("카메라 실행 중. 'q' 종료")

    pcb_detected = False

    while True:
        frame = picam2.capture_array()

        # ROI 표시
        cv2.rectangle(frame, (roi_x1, roi_y1), (roi_x2, roi_y2), (0, 255, 0), 2)
        roi_frame = frame[roi_y1:roi_y2, roi_x1:roi_x2]

        # Template Matching
        res = cv2.matchTemplate(roi_frame, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(res)

        if max_val >= threshold:
            filename = os.path.join(save_folder, f"pcb_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            cv2.imwrite(filename, roi_frame)
            cv2.putText(frame, "PCB DETECTED", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            print(f"PCB 감지! 자동 저장됨: {filename}")
            pcb_detected = True
            break

        cv2.imshow("Webcam", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    cv2.destroyAllWindows()
    picam2.stop()

    return pcb_detected


if __name__ == "__main__":
    print("PCB 감지 결과:", run_mapping())
