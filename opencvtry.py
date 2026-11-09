import cv2  # OpenCV for camera capture and image handling
from ultralytics import YOLO  # YOLOv8 model from the Ultralytics library
import cvzone  # Utility library for drawing labeled boxes easily

# Load COCO class names (used to label detected objects)
with open("coco.txt", "r") as f:
    class_names = f.read().splitlines()  # Read each class name into a list

# Load a pre-trained YOLOv8 model (Nano version in this case)
model = YOLO("yolo11n.pt")

# Open the USB camera (camera index 0 is usually the default one)
cap = cv2.VideoCapture(0)

# Set camera resolution to Full HD (1920x1080)
cap.set(3, 1920)  # Set frame width
cap.set(4, 1080)  # Set frame height

# Capture a single frame from the camera
ret, frame = cap.read()

# Check if frame capture was successful
if not ret:
    print("Failed to capture image.")
    cap.release()
    exit()  # Exit the program if capture fails

# Run YOLOv8 object detection + tracking on the full-resolution image
results = model.track(frame, persist=True)

# If YOLOv8 found any bounding boxes and assigned IDs
if results[0].boxes is not None and results[0].boxes.id is not None:
    # Extract bounding box coordinates, class IDs, track IDs, and confidence scores
    boxes = results[0].boxes.xyxy.int().cpu().tolist()       # Bounding box corners (x1, y1, x2, y2)
    class_ids = results[0].boxes.cls.int().cpu().tolist()    # Class IDs (e.g., 0 = person)
    track_ids = results[0].boxes.id.int().cpu().tolist()     # Unique tracking ID for each object
    confidences = results[0].boxes.conf.cpu().tolist()       # Confidence scores (0 to 1)

    # Loop through each detection and draw it on the frame
    for box, class_id, track_id, conf in zip(boxes, class_ids, track_ids, confidences):
        c = class_names[class_id]  # Get the class name (e.g., "person")
        x1, y1, x2, y2 = box       # Unpack the coordinates

        # Draw the bounding box around the object
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Display the object's tracking ID and class name using cvzone (prettier text)
        cvzone.putTextRect(frame, f'{track_id}', (x1, y2), scale=1, thickness=1)
        cvzone.putTextRect(frame, f'{c}', (x1, y1), scale=1, thickness=1)

# Show the final frame with detections in a window
cv2.imshow("Captured Full HD Image with Detections", frame)
print("Press any key in the image window to exit.")

cv2.waitKey(0)  # Wait indefinitely for a key press
cv2.destroyAllWindows()  # Close the display window
cap.release()  # Release the camera resource 