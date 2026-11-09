import cv2

def capture_image():
    # Open the default camera
    cap = cv2.VideoCapture(0)

    # Check if the camera is opened correctly
    if not cap.isOpened():
        print("Error opening camera")
        return

    # Capture a single frame
    ret, frame = cap.read()

    # Check if the frame was captured correctly
    if not ret:
        print("Error capturing frame")
        cap.release()
        return

    # Save the captured frame as "1.jpg"
    cv2.imwrite("/home/ssve/github-repo/rpi-cam-yolo11-main/1.jpg", frame)

    # Release the camera
    cap.release()

    print("Image saved as 1.jpg")

# Call the capture_image function to click and save the photo
capture_image()