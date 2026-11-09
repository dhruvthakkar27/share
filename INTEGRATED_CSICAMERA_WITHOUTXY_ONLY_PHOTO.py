# integrated_controller.py

from arducam64photoclick import capture_image
from INFERENCE_CAMERA import main as run_inference
from stepper_multi import xyz  # Use correct module name if needed (e.g., STEPPER_MOTOR not STEPPER MOTOR)
from datetime import datetime
from upload_image import send_all_images
date_str = datetime.now().strftime("%Y%m%d")
print("FOR DATE : ",date_str)
def main(date_str):
    # Step 1: Capture the image
    print("Capturing image...")
    capture_image(date_str)
    send_all_images(date_str,"captured_images")
    ######
    # Step 2: Run inference and get coordinates
    ######
    print("Running inference...")
    #center_x_list, center_y_list = run_inference(date_str)
    ######
    #send_all_images(date_str,"inference_images")
    ######
    # Step 3: Move stepper motors
    #if center_x_list and center_y_list:
        #print("Moving stepper motors based on detected positions...")
        #xyz(center_x_list, center_y_list)
    #else:
        #print("No valid detections (e.g., no 'weed' found). Stepper motor not activated.")

if __name__ == "__main__":
    main(date_str)




