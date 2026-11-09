import cv2
import os



def crop_image(image_path, output_path = None):
    points = [
        (217,134),
        (302,3455),
        (4165,3467),
        (3903,16)
        ]
    img = cv2.imread(image_path)
    if img is None:
        raise IOError("Image not found or cannot be loaded")
    h, w, _ = img.shape
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    # -----------------------------
    # SAFETY CHECK
    # -----------------------------
    if min_x < 0 or min_y < 0 or max_x > w or max_y > h:
        raise ValueError("Crop region exceeds image boundaries")

    # -----------------------------
    # CROP IMAGE
    # -----------------------------
    cropped = img[min_y:max_y, min_x:max_x]

    # -----------------------------
    # PRINT CROPPED SIZE
    # -----------------------------
    crop_h, crop_w, _ = cropped.shape
    print(f"✅ Cropped image size: {crop_w} x {crop_h} pixels")

    if output_path is None:
        folder = os.path.dirname(image_path)
        folder = folder.replace("captured_images", "cropped_images")
        os.makedirs(folder, exist_ok=True)
        output_path = os.path.join(folder, os.path.basename(image_path).replace(".jpg", "-cropped.jpg"))
    cv2.imwrite(output_path, cropped)
    print(f"📁 Cropped image saved to: {output_path}")
    return output_path
