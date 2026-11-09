import subprocess
import os
from datetime import datetime

def capture_image(date_str):
    # Output folder
    folder = f"/home/ssve/github-repo/rpi-cam-yolo11-main/captured_images/{date_str}"
    # Create folder if not exists
    os.makedirs(folder, exist_ok=True)

    # Generate a unique filename
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_path = os.path.join(folder, f"{timestamp}.jpg")

    # rpicam-still command with autofocus enabled
    cmd = [
        "rpicam-still",
        "-o", output_path,
        "--autofocus-mode", "auto",     # enable autofocus
        "--autofocus-on-capture",       # do AF before capture
        "--width", "4624",              # 64MP mode width (example)
        "--height", "3472"              # height
    ]

    # Run the command
    subprocess.run(cmd)
    print(f"Image saved: {output_path}")
    return output_path

# Test
if __name__ == "__main__":
    capture_image()