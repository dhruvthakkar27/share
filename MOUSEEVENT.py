import cv2

# -----------------------------
# IMAGE PATH
# -----------------------------
IMAGE_PATH = "/home/ssve/github-repo/rpi-cam-yolo11-main/cropped_images/20260413/2026-04-13_13-38-06-cropped.jpg"

# -----------------------------
# MOUSE CALLBACK FUNCTION
# -----------------------------
def mouse_event(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEMOVE:
        # Print live coordinates in terminal (overwrite line)
        print(f"\rCursor at: ({x}, {y})", end="")

    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"\n📍 Clicked at pixel: ({x}, {y})")

# -----------------------------
# LOAD IMAGE
# -----------------------------
img = cv2.imread(IMAGE_PATH)

if img is None:
    raise IOError("Image not found or cannot be loaded")

# -----------------------------
# DISPLAY WINDOW
# -----------------------------
cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
cv2.imshow("Image", img)

# Register mouse callback
cv2.setMouseCallback("Image", mouse_event)

print("🖱 Move mouse over image to see pixel coordinates")
print("🔘 Left click to lock a point")
print("❌ Press 'q' to quit")

# -----------------------------
# EVENT LOOP
# -----------------------------
while True:
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

cv2.destroyAllWindows()
