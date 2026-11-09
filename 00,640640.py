import cv2
from arducam64photoclick import capture_image
from time import sleep 
# Load the image
print("in delay")
#sleep(10)
#sprint ("out delay") 
img = cv2.imread("/home/ssve/github-repo/rpi-cam-yolo11-main/captured_images/20260102/2026-01-02_14-25-58.jpg")

if img is None:
    raise FileNotFoundError("Image not found at the given path!")

# Get image dimensions
height, width = img.shape[:2]
print(f"Image size: {width}x{height}")

# Points
pt1 = (0, 0)                     # Top-left
pt2 = (width - 1, height - 1)    # Bottom-right

# Mark (0,0)
cv2.circle(img, pt1, 5, (0, 0, 255), -1)
cv2.putText(img, "This is (0,0)", (pt1[0] + 10, pt1[1] + 30),
            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

# Mark bottom-right
cv2.circle(img, pt2, 5, (255, 0, 0), -1)
cv2.putText(img, f"This is ({pt2[0]},{pt2[1]})",
            (pt2[0] - 300, pt2[1] - 10),  # Shift left so text fits
            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

# Show the result
cv2.imshow("Annotated Image", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
