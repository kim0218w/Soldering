import cv2
from ultralytics import YOLO
from picamera2 import Picamera2

def run_webcam():
    model = YOLO("pcb_yolov8m_trained.pt")

    picam2 = Picamera2()
    picam2.preview_configuration.main.size = (640, 480)
    picam2.preview_configuration.main.format = "RGB888"
    picam2.configure("preview")
    picam2.start()

    while True:
        frame = picam2.capture_array()

        results = model(frame)[0]
        boxes = results.boxes.xyxy.cpu().numpy()
        cls = results.boxes.cls.cpu().numpy().astype(int)
        conf = results.boxes.conf.cpu().numpy()

        centers = [((b[0]+b[2])/2, (b[1]+b[3])/2, i) for i, b in enumerate(boxes)]
        centers_sorted = sorted(centers, key=lambda x: (int(x[1]//50), x[0]))

        for idx, (_, _, i) in enumerate(centers_sorted, start=1):
            x1, y1, x2, y2 = boxes[i].astype(int)
            label = f"{idx}: {model.names[cls[i]]} {conf[i]:.2f}"
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (0, 255, 0), 2)

        cv2.imshow("YOLOv8 Numbered Detection", frame)
        if cv2.waitKey(1) & 0xFF == 27:  # ESC
            break

    cv2.destroyAllWindows()
    picam2.stop()
