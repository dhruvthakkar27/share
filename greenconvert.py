import cv2
import numpy as np
import os

# ----------------------------------
# CONFIG
# ----------------------------------
INPUT_IMAGE_PATH = "/home/ssve/github-repo/rpi-cam-yolo11-main/GREEN_DOTS/20260406/2026-04-06_15-00-03-green.jpg"   # 🔁 change this
TARGET_RGB = (75, 153, 113)     # 🎯 target color (R,G,B)
TOLERANCE = 15                  # 🔧 adjust if needed
BACKGROUND_COLOR = (0, 0, 0)    # black background (BGR)

# ----------------------------------
# FUNCTION
# ----------------------------------
def detect_specific_color(input_path,
                          output_path=None,
                          target_rgb=(75,153,113),
                          tolerance=10,
                          background_color=(0,0,0)):

    # Convert RGB → BGR (OpenCV uses BGR)
    target_bgr = (target_rgb[2], target_rgb[1], target_rgb[0])

    # Load image
    img = cv2.imread(input_path)
    if img is None:
        raise FileNotFoundError(f"Image not found: {input_path}")

    # Create lower and upper bounds
    lower = np.array([
        max(0, target_bgr[0] - tolerance),
        max(0, target_bgr[1] - tolerance),
        max(0, target_bgr[2] - tolerance)
    ], dtype=np.uint8)

    upper = np.array([
        min(255, target_bgr[0] + tolerance),
        min(255, target_bgr[1] + tolerance),
        min(255, target_bgr[2] + tolerance)
    ], dtype=np.uint8)

    # Create mask
    mask = cv2.inRange(img, lower, upper)

    # Create output image
    output = np.zeros_like(img)
    output[:] = background_color
    output[mask > 0] = img[mask > 0]

    # Auto-generate output path if not provided
    if output_path is None:
        folder = os.path.dirname(input_path)
        folder = folder.replace("cropped_images", "GREEN_DOTS")
        if folder == "":
            folder = "output"
        os.makedirs(folder, exist_ok=True)

        filename = os.path.basename(input_path)
        output_path = os.path.join(folder, f"processed_{filename}")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Save result
    cv2.imwrite(output_path, output)

    # Count detected pixels
    pixel_count = int(np.sum(mask > 0))
    print(f"Detected pixels: {pixel_count}")

    return output_path


# ----------------------------------
# RUN
# ----------------------------------
if __name__ == "__main__":
    result_path = detect_specific_color(
        INPUT_IMAGE_PATH,
        target_rgb=TARGET_RGB,
        tolerance=TOLERANCE
    )

    print(f"Output saved at: {result_path}")