import cv2
import numpy as np
import os

GREEN_IMAGE_PATH = f"/home/ssve/github-repo/rpi-cam-yolo11-main/GREEN DOTS/"
def process_green_image(input_path,
                        output_path=None,
                        G_MIN=120,
                        R_MAX=140,
                        B_MAX=140,
                        background_color=(0, 0, 0)):
    """
    Keeps only green pixels in an image and saves result.

    Parameters:
        input_path (str): Full path of input image
        output_path (str): Full path where processed image will be saved
        G_MIN (int): Minimum green value threshold
        R_MAX (int): Maximum red allowed
        B_MAX (int): Maximum blue allowed
        background_color (tuple): BGR color for background

    Returns:
        int: Number of green pixels detected
    """

    # Load image
    img = cv2.imread(input_path)
    if img is None:
        raise FileNotFoundError(f"Image not found: {input_path}")

    # Define green range (BGR)
    lower_green = np.array([0, G_MIN, 0])
    upper_green = np.array([B_MAX, 255, R_MAX])

    # Create mask
    green_mask = cv2.inRange(img, lower_green, upper_green)

    # Create output image
    output = np.zeros_like(img)
    output[:] = background_color
    output[green_mask > 0] = img[green_mask > 0]
    if output_path is None:
        folder = os.path.dirname(input_path)
        folder = folder.replace("cropped_images","GREEN_DOTS")
        os.makedirs(folder, exist_ok=True)
        output_path = os.path.join(folder, os.path.basename(input_path).replace("-cropped.jpg", "-green.jpg"))
    # Ensure output folder exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Save image
    cv2.imwrite(output_path, output)

    # Count green pixels
    green_pixel_count = int(np.sum(green_mask > 0))
    print(green_pixel_count)
    return output_path
