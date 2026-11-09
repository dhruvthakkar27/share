import cv2

# -----------------------------
# IMAGE PATH
# -----------------------------
IMAGE_PATH = "/home/ssve/github-repo/rpi-cam-yolo11-main/captured_images/20260413/2026-04-13_12-05-47.jpg"
OUTPUT_PATH = "/home/ssve/github-repo/rpi-cam-yolo11-main/captured_images/20260413/04624.jpg"

# -----------------------------
# IMAGE SIZE (FIXED)
# -----------------------------
IMAGE_WIDTH  = 4624
IMAGE_HEIGHT = 3472

# -----------------------------
# LOAD IMAGE
# -----------------------------
img = cv2.imread(IMAGE_PATH)

if img is None:
    raise IOError("Image not found or cannot be loaded")

# -----------------------------
# CORNER POINTS
# -----------------------------
points = {
    "0,0": (0, 0),
    "4624,0": (IMAGE_WIDTH - 1, 0),
    "4624,3472": (IMAGE_WIDTH - 1, IMAGE_HEIGHT - 1),
    "0,3472": (0, IMAGE_HEIGHT - 1),
}

# -----------------------------
# DRAW POINTS & TEXT
# -----------------------------
for text, (x, y) in points.items():
    # Draw circle
    cv2.circle(img, (x, y), radius=15, color=(0, 0, 255), thickness=-1)

    # Offset text so it is visible inside image
    text_x = x + 20 if x == 0 else x - 350
    text_y = y + 40 if y == 0 else y - 20

    cv2.putText(
        img,
        text,
        (text_x, text_y),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.2,
        (255, 0, 0),
        3,
        cv2.LINE_AA
    )

# -----------------------------
# SAVE OUTPUT
# -----------------------------
cv2.imwrite(OUTPUT_PATH, img)

print("✅ Corner-marked image saved to:")
print(OUTPUT_PATH)
