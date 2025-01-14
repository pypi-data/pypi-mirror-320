import numpy as np
from ultralytics import YOLO
import cv2
import json
from class_names import class_names

model = YOLO("yolov9s.pt")
# vinomodel = model.export(format='openvino')

vinomodel = YOLO("yolov9s_openvino_model")

cap = cv2.VideoCapture("D:\\Brysk\\Test\\Test_4.mp4")

output_path = r'D:\Brysk\Output'
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter(output_path, fourcc, cap.get(cv2.CAP_PROP_FPS), (640, 480))

metadata = []

frame_number = 0
while True:
    success, img = cap.read()
    if not success:
        break

    frame_number += 1

    frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = vinomodel(frame)

    frame_metadata = {"frame": frame_number, "objects": []}

    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            if conf > 0.2:
                class_id = int(box.cls[0])
                class_name = class_names[class_id]

                object_metadata = {
                    "class_name": class_name,
                    "confidence": conf,
                    "bbox": {"x_min": x1, "y_min": y1, "x_max": x2, "y_max": y2},
                }
                frame_metadata["objects"].append(object_metadata)

                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 255), 3)
                cv2.putText(
                    frame,
                    f"{class_name} {conf:.2f}",
                    (max(0, x1), max(0, y1 - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 0, 0),
                    2,
                )

    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    frame_resized = cv2.resize(frame_bgr, (640, 480))

    out.write(frame_resized)

    metadata.append(frame_metadata)

    cv2.imshow("Video", frame_resized)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

cap.release()
out.release()

metadata_output_path = "Metadata.json"
with open(metadata_output_path, "w") as f:
    json.dump(metadata, f, indent=4)

cv2.destroyAllWindows()
