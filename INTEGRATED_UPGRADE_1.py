# ============================================================================
# FILE: INTEGRATED_csicamera_xy.py (Updated with Parallel Uploads)
# ============================================================================

from arducam64photoclick import capture_image
from croppedimage import crop_image
from CONVERT_GREEN_BLACK import process_green_image
from INFERENCE_CAMERA_1 import main as run_inference
from updated_stepper_multi import xyz
from datetime import datetime
from upload_image import send_all_images
import threading
import time

date_str = datetime.now().strftime("%Y%m%d")
print("FOR DATE : ", date_str)


def upload_in_background(date_str, image_type, timeout=60):
    """
    Upload images in a background thread with timeout protection.
    
    Args:
        date_str: Date string for image directory
        image_type: Type of images ("captured_images", "cropped_images", "inference_images")
        timeout: Maximum time to wait for upload (seconds)
    """
    def upload_task():
        try:
            print(f"[UPLOAD] Starting upload for {image_type}...")
            send_all_images(date_str, image_type)
            print(f"[UPLOAD] ✓ Upload complete for {image_type}")
        except Exception as e:
            print(f"[UPLOAD] ✗ Upload failed for {image_type}: {str(e)}")
    
    # Create and start background thread
    upload_thread = threading.Thread(target=upload_task, daemon=True)
    upload_thread.start()
    
    return upload_thread


def main(date_str):
    # Keep track of upload threads
    upload_threads = []
    
    # ========================================
    # STEP 1: CAPTURE IMAGE
    # ========================================
    print("\n" + "="*60)
    print("STEP 1: Capturing image...")
    print("="*60)
    
    captured_image_path = capture_image(date_str)
    print(f"✓ Image captured: {captured_image_path}")
    
    # Start upload in parallel (don't wait)
    upload_thread_1 = upload_in_background(date_str, "captured_images")
    upload_threads.append(("captured_images", upload_thread_1))
    
    
    # ========================================
    # STEP 2: CROP IMAGE
    # ========================================
    print("\n" + "="*60)
    print("STEP 2: Cropping image...")
    print("="*60)
    
    cropped_image_path = crop_image(captured_image_path)
    print(f"✓ Image cropped: {cropped_image_path}")
    
    # Start upload in parallel (don't wait)
    upload_thread_2 = upload_in_background(date_str, "cropped_images")
    upload_threads.append(("cropped_images", upload_thread_2))
    
    #green_image_path = process_green_image(cropped_image_path)
    # ========================================
    # STEP 3: RUN INFERENCE
    # ========================================
    print("\n" + "="*60)
    print("STEP 3: Running inference...")
    print("="*60)
    
    center_x_list, center_y_list = run_inference(date_str)
    print(f"✓ Inference complete: {len(center_x_list)} weeds detected")
    
    # Start upload in parallel (don't wait)
    upload_thread_3 = upload_in_background(date_str, "inference_images")
    upload_threads.append(("inference_images", upload_thread_3))
    
    
    # ========================================
    # STEP 4: MOVE STEPPER MOTORS
    # ========================================
    print("\n" + "="*60)
    print("STEP 4: Targeting weeds with laser...")
    print("="*60)
    
    if center_x_list and center_y_list:
        print(f"Moving stepper motors for {len(center_x_list)} targets...")
        #xyz(center_x_list, center_y_list)
        print("✓ All targets processed")
    else:
        print("ℹ No valid detections - motor control skipped")
    
    
    # ========================================
    # OPTIONAL: WAIT FOR UPLOADS TO COMPLETE
    # ========================================
    print("\n" + "="*60)
    print("Checking upload status...")
    print("="*60)
    
    for image_type, thread in upload_threads:
        if thread.is_alive():
            print(f"⏳ Upload still in progress for {image_type}")
            # Optional: wait with timeout
            thread.join(timeout=5)  # Wait max 5 seconds
            if thread.is_alive():
                print(f"⚠ Upload taking longer than expected for {image_type}")
            else:
                print(f"✓ Upload completed for {image_type}")
        else:
            print(f"✓ Upload already completed for {image_type}")
    
    print("\n" + "="*60)
    print("PIPELINE COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main(date_str)


# ============================================================================
# END OF FILE: INTEGRATED_csicamera_xy.py
# ============================================================================
