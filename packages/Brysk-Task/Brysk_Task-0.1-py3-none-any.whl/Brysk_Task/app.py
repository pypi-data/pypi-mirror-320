import os
import json
import cv2
from flask import Flask, render_template, request, send_from_directory, jsonify
from ultralytics import YOLO
from class_names import class_names

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def predict_img():
    if request.method == "POST":
        if "file" in request.files and "output_folder" in request.form:
            f = request.files["file"]
            output_folder = request.form["output_folder"]
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            basepath = os.path.dirname(__file__)
            uploads_folder = os.path.join(basepath, "uploads")
            if not os.path.exists(uploads_folder):
                os.makedirs(uploads_folder)
            filepath = os.path.join(uploads_folder, f.filename)
            f.save(filepath)

            file_extension = f.filename.rsplit(".", 1)[1].lower()

            if file_extension == "mp4":
                video_path = filepath
                cap = cv2.VideoCapture(video_path)
                fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                output_video_path = os.path.join(output_folder, "output_video.mp4")
                out = cv2.VideoWriter(
                    output_video_path, fourcc, cap.get(cv2.CAP_PROP_FPS), (640, 480)
                )

                model = YOLO("yolov9s.pt")

                metadata = []
                frame_number = 0

                while True:
                    success, img = cap.read()
                    if not success:
                        break

                    frame_number += 1
                    frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    results = model(frame, save=True)

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
                                    "bbox": {
                                        "x_min": x1,
                                        "y_min": y1,
                                        "x_max": x2,
                                        "y_max": y2,
                                    },
                                }
                                frame_metadata["objects"].append(object_metadata)

                                cv2.rectangle(
                                    frame, (x1, y1), (x2, y2), (255, 0, 255), 3
                                )
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

                    if cv2.waitKey(1) == ord("q"):
                        break

                metadata_path = os.path.join(output_folder, "metadata.json")
                with open(metadata_path, "w") as metadata_file:
                    json.dump(metadata, metadata_file, indent=4)

                return render_template(
                    "index.html",
                    message="Processing complete",
                    metadata_filename="metadata.json",
                    metadata_path=metadata_path,
                    video_path=output_video_path,
                    output_folder=output_folder,
                )

    return render_template("index.html")


@app.route("/metadata", methods=["GET"])
def retrieve_metadata():
    output_folder = request.args.get("output_folder", default="uploads", type=str)
    metadata_path = os.path.join(output_folder, "metadata.json")
    if os.path.exists(metadata_path):
        with open(metadata_path, "r") as metadata_file:
            metadata = json.load(metadata_file)
        return jsonify(metadata)
    else:
        return jsonify({"error": "Metadata not found"}), 404


@app.route("/download_metadata/<filename>")
def download_metadata(filename):
    output_folder = request.args.get("output_folder", default="uploads", type=str)
    metadata_path = os.path.join(output_folder, filename)
    if os.path.exists(metadata_path):
        return send_from_directory(output_folder, filename, as_attachment=True)
    else:
        return jsonify({"error": "Metadata not found"}), 404


if __name__ == "__main__":
    app.run(debug=True)
