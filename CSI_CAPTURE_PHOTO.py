import subprocess
import os

def capture_image(date_str):
    # Base folder where images must be saved
    BASE_PATH = f"/home/ssve/github-repo/rpi-cam-yolo11-main/captured_images/{date_str}"

    # Create folder if not exists
    os.makedirs(BASE_PATH, exist_ok=True)

    # Full path for saving the image
    image_path = os.path.join(BASE_PATH, "image.jpg")

    # Capture using CSI camera
    subprocess.run([
        "rpicam-still",
        "-n",                    # no preview
        "-o", image_path         # save output file
    ])

    print(f"Image saved to: {image_path}")
    return image_path
