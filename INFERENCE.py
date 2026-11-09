# Import necessary libraries
import cv2                        # OpenCV for image processing
import numpy as np               # NumPy for array operations
from ultralytics import YOLO     # Ultralytics YOLO for loading and running YOLOv8 models
import time                      # Time module to measure inference duration
from datetime import datetime    #importing date and time for saving images
import os
# Set camera dimensions (used for drawing and scaling if needed)
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

def main(date_str):
    # Load the YOLOv8 model (nano model or your custom-trained one)
    model = YOLO(r'/home/ssve/github-repo/rpi-cam-yolo11-main/v8best.pt')

    # Read the input image from file
    img_1 = cv2.imread(r'/home/ssve/github-repo/rpi-cam-yolo11-main/inference_images/2.jpg')  # BGR format

    if img_1 is None:
        print("Error: Could not load image.")
        return [], []

    # Convert image from BGR to RGB for YOLO
    img_rgb = cv2.cvtColor(img_1, cv2.COLOR_BGR2RGB)

    print("Image loaded and converted")

    # Record start time
    start_time = time.time()

    # Run inference
    results = model(img_rgb, imgsz=640)[0]  # results[0] is the Results object
    print("ran inference")
    # Record end time
    stop_time = time.time()
    print('Inference time: {:.3f} ms'.format((stop_time - start_time) * 1000))

    # Lists to store detected centers
    center_x_list = []
    center_y_list = []

    # Loop over detections
    for box in results.boxes:
        # Get coordinates
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        print("IN THE FOR LOOP")
        # Get confidence and class ID
        conf = float(box.conf[0])
        cls_id = int(box.cls[0])

        # Get label name
        label = model.names[cls_id]

        # Prepare label text
        text = f"{label} {conf:.2f}"

        # Get text size for label box
        (text_width, text_height), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)

        # Draw bounding box
        cv2.rectangle(img_1, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Draw label background
        cv2.rectangle(img_1, (x1, y1 - text_height - 10), (x1 + text_width, y1), (0, 255, 0), -1)

        # Draw label text
        cv2.putText(img_1, text, (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

        # Compute and draw center
        center_x = int((x1 + x2) / 2)
        center_y = int((y1 + y2) / 2)
        cv2.circle(img_1, (center_x, center_y), 5, (0, 0, 255), -1)

        # Store centers
        center_x_list.append(center_x)
        center_y_list.append(center_y)

    # Save the annotated output image
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    dirs = "/home/ssve/github-repo/rpi-cam-yolo11-main/inference_images/" + str(date_str)
    os.makedirs(dirs, exist_ok=True)
    Data_clicked = "/home/ssve/github-repo/rpi-cam-yolo11-main/inference_images/" + str(date_str) + "/" + timestamp + ".jpg"
    #output_path = r'/home/ssve/github-repo/rpi-cam-yolo11-main/2.jpg'
    cv2.imwrite(Data_clicked, img_1)
    print(f"Output image saved at: {Data_clicked}")
    

    # Print center points
    print("Center X coordinates:", center_x_list)
    print("Center Y coordinates:", center_y_list)

    return center_x_list, center_y_list

# Run main
if __name__ == "__main__":
    center_x_list, center_y_list = main("20251217")
    pass

