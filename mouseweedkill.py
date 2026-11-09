import cv2
import sys
import time
from datetime import datetime 
# Import your existing modules
from arducam64photoclick import capture_image
from stepper_multi import xyz
from croppedimage import crop_image

# ==========================================
# GLOBAL LISTS TO STORE CLICKED POINTS
# ==========================================
clicked_x = []
clicked_y = []

date_str = datetime.now().strftime("%Y%m%d")
print("FOR DATE : ", date_str)
# ==========================================
# MOUSE CLICK FUNCTION
# ==========================================
def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"[CLICK] X={x}, Y={y}")

        clicked_x.append(x)
        clicked_y.append(y)

        # Draw point on image
        cv2.circle(param, (x, y), 5, (0, 0, 255), -1)
        cv2.putText(param, f"{x},{y}", (x+10, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)


# ==========================================
# MAIN FUNCTION
# ==========================================
def main():

    # Step 1: Capture image
    image_path = capture_image(date_str)
    print(f"[INFO] Using image: {image_path}")
    
    cropped_image_path = crop_image(image_path)

    # Step 2: Load image
    img = cv2.imread(cropped_image_path)

    if img is None:
        print("[ERROR] Could not load image")
        return

    clone = img.copy()

    # Step 3: Set mouse callback
    cv2.namedWindow("Image")
    cv2.setMouseCallback("Image", mouse_callback, clone)

    print("\n[INSTRUCTION]")
    print(" - Click on image to select points")
    print(" - Press 'r' to reset")
    print(" - Press 'q' to send to stepper\n")

    # Step 4: Loop
    while True:
        cv2.imshow("Image", clone)
        key = cv2.waitKey(1) & 0xFF

        # Reset points
        if key == ord("r"):
            print("[RESET]")
            clone = img.copy()
            clicked_x.clear()
            clicked_y.clear()

        # Send to stepper
        elif key == ord("q"):
            print("\n[FINAL POINTS]")
            print("X:", clicked_x)
            print("Y:", clicked_y)

            if len(clicked_x) > 0:
                xyz(clicked_x, clicked_y)
            else:
                print("[WARNING] No points selected")

            break

    cv2.destroyAllWindows()


# ==========================================
# RUN
# ==========================================
if __name__ == "__main__":
    main()