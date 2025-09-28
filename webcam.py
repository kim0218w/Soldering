import cv2
from ultralytics import YOLO

def run_webcam():
    model = YOLO("C:/Users/kim02/OneDrive/바탕 화면/soldering/pcb_yolov8m_trained.pt")
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)[0]
        boxes = results.boxes.xyxy.cpu().numpy()
        cls = results.boxes.cls.cpu().numpy().astype(int)
        conf = results.boxes.conf.cpu().numpy()

        # 중심좌표 기반 정렬 (상→하, 좌→우)
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

    cap.release()
    cv2.destroyAllWindows()
