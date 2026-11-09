import cv2
import numpy as np
from ultralytics import YOLO
import time

CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

def main():
    model = YOLO(r'/home/ssve/github-repo/rpi-cam-yolo11-main/yolo11n.pt')

    img_1 = cv2.imread(r'/home/ssve/github-repo/rpi-cam-yolo11-main/1.jpg')  # Load BGR image

    if img_1 is None:
        print("Error: Could not load image.")
        return [], []

    img_rgb = cv2.cvtColor(img_1, cv2.COLOR_BGR2RGB)
    print("Image loaded and converted")

    start_time = time.time()
    results = model(img_rgb, imgsz=640)[0]
    stop_time = time.time()

    print('Inference time: {:.3f} ms'.format((stop_time - start_time) * 1000))

    center_x_list = []
    center_y_list = []

    for box in results.boxes:
        conf = float(box.conf[0])
        cls_id = int(box.cls[0])
        label = model.names[cls_id]

        # Only process "weed" class
        if label.lower() != "weed":
            continue

        x1, y1, x2, y2 = map(int, box.xyxy[0])
        text = f"{label} {conf:.2f}"

        (text_width, text_height), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
        cv2.rectangle(img_1, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.rectangle(img_1, (x1, y1 - text_height - 10), (x1 + text_width, y1), (0, 255, 0), -1)
        cv2.putText(img_1, text, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

        center_x = int((x1 + x2) / 2)
        center_y = int((y1 + y2) / 2)
        cv2.circle(img_1, (center_x, center_y), 5, (0, 0, 255), -1)

        center_x_list.append(center_x)
        center_y_list.append(center_y)

    output_path = r'/home/ssve/github-repo/rpi-cam-yolo11-main/2.jpg'
    cv2.imwrite(output_path, img_1)
    print(f"Output image saved at: {output_path}")

    print("Center X coordinates:", center_x_list)
    print("Center Y coordinates:", center_y_list)

    return center_x_list, center_y_list

if __name__ == "__main__":
    center_x_list, center_y_list = main()
