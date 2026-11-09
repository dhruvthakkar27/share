from datetime import datetime
from click_photo_updated import capture_image
from upload_image import send_all_images
from stepper_multi import xyz as main_stepper

def run_data_collection():
    date_str = datetime.now().strftime("%Y-%m-%d")

    # Step 1: Capture photo
    #capture_image(date_str)

    # Step 2: Upload last captured image to Telegram
    #send_all_images(date_str, types="captured_images")

    # Step 3: Move steppers
    print("stepper first move")
    main_stepper([700,0,700,0,700,0,700,0,700],[700,0,700,0,700,0,700,0,700])   # Move to 700, 700
    print("first move complete")
    main_stepper(0, 0) # Back to 0,0
    main_stepper([700,0,700],[700,0,700])   # Back to 700, 700
    main_stepper(0, 0)
    print("Data collection sequence completed.")


if __name__ == "__main__":
    run_data_collection()
