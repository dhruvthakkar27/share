import cv2
import os
from datetime import datetime

def capture_image(date_str):
    # Define paths
    temp_filename = "/home/ssve/github-repo/rpi-cam-yolo11-main/1.jpg"
    Data_clicked = "/home/ssve/github-repo/rpi-cam-yolo11-main/captured_images/" + str(date_str)

    # Create archive folder if it doesn't exist
    os.makedirs(Data_clicked, exist_ok=True)

    # Open the default camera
    cap = cv2.VideoCapture(0)

    # Check if the camera is opened correctly
    if not cap.isOpened():
        print("Error opening camera")
        return

    # Capture a single frame
    ret, frame = cap.read()

    if not ret:
        print("Error capturing frame")
        cap.release()
        return

    # Save temporary working image (overwritten every time)
    cv2.imwrite(temp_filename, frame)

    # Create unique filename with date and time
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    jpg_filename = f"{Data_clicked}/{timestamp}.jpg"

    # Save the archived copy
    cv2.imwrite(jpg_filename, frame)

    # Release the camera
    cap.release()

    print(f"Image saved as 1.jpg and archived as {jpg_filename}")

# Example usage:
#capture_image()
