import cv2

# -----------------------------
# CHANGE THIS TO YOUR IMAGE PATH
# -----------------------------
IMAGE_PATH = "/home/ssve/github-repo/rpi-cam-yolo11-main/GREEN_DOTS/20260406/2026-04-06_15-00-03-green.jpg"

# Load image
img = cv2.imread(IMAGE_PATH)

# Check if image loaded properly
if img is None:
    print("Error: Could not load image. Check file path.")
    exit()

# Clone image (so we can draw text without overwriting original)
display_img = img.copy()

# -----------------------------
# Mouse click event function
# -----------------------------
def click_event(event, x, y, flags, param):
    global display_img

    if event == cv2.EVENT_LBUTTONDOWN:
        # Get BGR values
        b, g, r = img[y, x]

        # Print RGB values
        print(f"Clicked at (X:{x}, Y:{y}) -> RGB = ({r}, {g}, {b})")

        # Draw a small circle where clicked
        cv2.circle(display_img, (x, y), 5, (0, 255, 0), -1)

        # Show RGB text near cursor
        text = f"RGB: ({r},{g},{b})"
        cv2.putText(display_img, text, (x + 10, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (255, 255, 255), 1, cv2.LINE_AA)

        # Refresh window
        cv2.imshow("RGB Picker", display_img)

# -----------------------------
# Create window and bind event
# -----------------------------
cv2.namedWindow("RGB Picker")
cv2.setMouseCallback("RGB Picker", click_event)

print("👉 Click anywhere on the image to get RGB values")
print("👉 Press 'r' to reset drawing")
print("👉 Press 'q' to quit")

# -----------------------------
# Main loop
# -----------------------------
while True:
    cv2.imshow("RGB Picker", display_img)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('r'):
        display_img = img.copy()  # reset image

    elif key == ord('q'):
        break

cv2.destroyAllWindows()