# ======================================================
# IMPORT REQUIRED LIBRARIES
# ======================================================

import lgpio
import time
import multiprocessing
import datetime


# ======================================================
# CAMERA & MACHINE CONSTANTS
# ======================================================

IMAGE_WIDTH  = 3497
IMAGE_HEIGHT = 3409

MAX_MM_X = 700
MAX_MM_Y = 700

RESOLUTION_X = 400
RESOLUTION_Y = 800

BALL_SCREW_PITCH_X = 5
BALL_SCREW_PITCH_Y = 10

STEP_DELAY = 0.00045
LASER_ON_TIME = 15

CW  = 0
CCW = 1


# ======================================================
# GPIO PIN DEFINITIONS (BCM)
# ======================================================

Y_DIR  = 17
Y_STEP = 27
X_DIR  = 22
X_STEP = 23
RELAY  = 12

GPIO_CHIP = 0


# ======================================================
# CROP PROTECTION COORDINATES
# Define coordinates where crops/seeds are located
# These will NOT be targeted by the laser
# ======================================================

# List of (x, y) pixel coordinates where your crops are planted
CROP_COORDINATES = [
    (2009, 106),
    (2109, 1519),
    (2103, 2542),
    (1067, 3270),
    (941, 2134),
    (2913, 929),
    (3001, 2015),
    (3124, 2990),
    (1838,1074),
]

# Tolerance in pixels - how close a weed can be to a crop before being filtered
# This is the RADIUS of protection zone around each crop
CROP_TOLERANCE_PIXELS = 100


# ======================================================
# FILTER FUNCTION - REMOVE WEEDS NEAR CROPS
# ======================================================

def filter_weeds_near_crops(center_list_x_px, center_list_y_px, crop_coords=None, tolerance=CROP_TOLERANCE_PIXELS):
    """
    Remove weed detections that are too close to crop positions.
    
    Args:
        center_list_x_px: List of weed X coordinates (pixels)
        center_list_y_px: List of weed Y coordinates (pixels)
        crop_coords: List of (x, y) tuples representing crop positions
        tolerance: Minimum distance in pixels - weeds closer than this are filtered
    
    Returns:
        Tuple of (filtered_x_list, filtered_y_list)
    """
    # Use default crop coordinates if none provided
    if crop_coords is None:
        crop_coords = CROP_COORDINATES
    
    # If no crop coordinates defined, return original lists
    if not crop_coords:
        print("[CROP FILTER] ⚠️  No crop coordinates - skipping filter")
        return center_list_x_px, center_list_y_px
    
    print("\n" + "="*60)
    print("🛡️  CROP PROTECTION FILTER")
    print("="*60)
    print(f"Protected crops: {len(crop_coords)}")
    print(f"Tolerance: {tolerance} pixels")
    print(f"Original detections: {len(center_list_x_px)}")
    print("-"*60)
    
    filtered_x = []
    filtered_y = []
    filtered_count = 0
    
    # Check each detected weed
    for weed_idx, (weed_x, weed_y) in enumerate(zip(center_list_x_px, center_list_y_px)):
        is_safe_to_target = True
        closest_distance = float('inf')
        
        # Check distance to each crop
        for crop_x, crop_y in crop_coords:
            # Calculate Euclidean distance
            distance = ((weed_x - crop_x) ** 2 + (weed_y - crop_y) ** 2) ** 0.5
            
            if distance < closest_distance:
                closest_distance = distance
            
            # If weed is too close to ANY crop, filter it out
            if distance <= tolerance:
                print(f"❌ Weed #{weed_idx+1} at ({weed_x}, {weed_y}) - FILTERED (distance: {distance:.1f}px)")
                is_safe_to_target = False
                filtered_count += 1
                break
        
        # If weed is far enough from all crops, keep it
        if is_safe_to_target:
            filtered_x.append(weed_x)
            filtered_y.append(weed_y)
            print(f"✅ Weed #{weed_idx+1} at ({weed_x}, {weed_y}) - SAFE (closest: {closest_distance:.1f}px)")
    
    print("-"*60)
    print(f"Filtered: {filtered_count} | Safe to target: {len(filtered_x)}")
    print("="*60 + "\n")
    
    return filtered_x, filtered_y


# ======================================================
# PIXEL → MM CONVERSION (ABSOLUTE POSITION)
# ======================================================

def pixel_to_mm(px, py):
    print(f"[PIXEL INPUT] px={px}, py={py}")

    x_mm = (px / IMAGE_WIDTH) * MAX_MM_X
    y_mm = (py / IMAGE_HEIGHT) * MAX_MM_Y

    print(f"[PIXEL → MM] x_mm={x_mm:.3f}, y_mm={y_mm:.3f}")

    return x_mm, y_mm


# ======================================================
# MM → STEPS CONVERSION (RELATIVE MOVEMENT)
# ======================================================

def mm_to_steps(mm, axis):
    pitch = BALL_SCREW_PITCH_X if axis == "x" else BALL_SCREW_PITCH_Y
    resolution = RESOLUTION_X if axis == "x" else RESOLUTION_Y

    steps = int((mm / pitch) * resolution)

    print(f"[MM → STEPS] axis={axis}, mm={mm:.3f}, steps={steps}")

    return steps


# ======================================================
# LOW-LEVEL STEPPER MOTOR MOVEMENT
# ======================================================

def move_motor(steps, h, dir_pin, step_pin):
    direction = CW if steps >= 0 else CCW
    dir_str = "CW" if direction == CW else "CCW"

    print(f"[MOTOR] dir_pin={dir_pin}, step_pin={step_pin}")
    print(f"[MOTOR] steps={steps}, direction={dir_str}")

    lgpio.gpio_write(h, dir_pin, direction)

    for i in range(abs(steps)):
        lgpio.gpio_write(h, step_pin, 1)
        time.sleep(STEP_DELAY)
        lgpio.gpio_write(h, step_pin, 0)
        time.sleep(STEP_DELAY)


# ======================================================
# MOVE X AND Y AXES TOGETHER
# ======================================================

def move_xy(steps_x, steps_y, h):
    print(f"[MOVE_XY] steps_x={steps_x}, steps_y={steps_y}")

    px = multiprocessing.Process(
        target=move_motor, args=(steps_x, h, X_DIR, X_STEP)
    )
    py = multiprocessing.Process(
        target=move_motor, args=(steps_y, h, Y_DIR, Y_STEP)
    )

    start = datetime.datetime.now()
    print("[MOVE_XY] Movement started")

    px.start()
    py.start()

    px.join()
    py.join()

    print("[MOVE_XY] Movement finished")
    print("[MOVE_XY] Duration:", datetime.datetime.now() - start)


# ======================================================
# MAIN EXECUTION FUNCTION
# ======================================================

def xyz(center_list_x_px, center_list_y_px, crop_coords=None, tolerance=CROP_TOLERANCE_PIXELS):
    """
    Main function to move laser to detected weed positions.
    Now includes crop protection filtering.
    
    Args:
        center_list_x_px: List of weed X coordinates (pixels)
        center_list_y_px: List of weed Y coordinates (pixels)
        crop_coords: Optional list of (x, y) crop positions to protect
        tolerance: Minimum distance from crops in pixels
    """
    print("========== START xyz() ==========")
    print("Input center_list_x:", center_list_x_px)
    print("Input center_list_y:", center_list_y_px)
    
    # ======================================================
    # FILTER WEEDS NEAR CROPS
    # ======================================================
    center_list_x_px, center_list_y_px = filter_weeds_near_crops(
        center_list_x_px, 
        center_list_y_px, 
        crop_coords, 
        tolerance
    )
    
    # If all weeds were filtered out, return early
    if not center_list_x_px:
        print("\n⚠️  All detections filtered - no valid targets")
        print("========== END xyz() ==========")
        return
    
    print(f"\n🎯 Proceeding with {len(center_list_x_px)} target(s)")
    print(f"Targets X: {center_list_x_px}")
    print(f"Targets Y: {center_list_y_px}\n")
    # ======================================================

    h = lgpio.gpiochip_open(GPIO_CHIP)

    lgpio.gpio_claim_output(h, X_DIR, 0)
    lgpio.gpio_claim_output(h, X_STEP, 0)
    lgpio.gpio_claim_output(h, Y_DIR, 0)
    lgpio.gpio_claim_output(h, Y_STEP, 0)
    lgpio.gpio_claim_output(h, RELAY, 0)

    current_x_mm = 0.0
    current_y_mm = 0.0

    print(f"[START POS] current_x_mm={current_x_mm}, current_y_mm={current_y_mm}")

    for idx, (px, py) in enumerate(zip(center_list_x_px, center_list_y_px)):
        print("\n--------------------------------")
        print(f"[TARGET {idx+1}/{len(center_list_x_px)}] Processing")

        target_x_mm, target_y_mm = pixel_to_mm(px, py)

        dx_mm = target_x_mm - current_x_mm
        dy_mm = target_y_mm - current_y_mm

        print(f"[DELTA MM] dx_mm={dx_mm:.3f}, dy_mm={dy_mm:.3f}")

        steps_x = mm_to_steps(dx_mm, "x")
        steps_y = mm_to_steps(dy_mm, "y")

        move_xy(steps_x, steps_y, h)

        print("[LASER] ON")
        lgpio.gpio_write(h, RELAY, 1)
        time.sleep(LASER_ON_TIME)
        lgpio.gpio_write(h, RELAY, 0)
        print("[LASER] OFF")

        current_x_mm = target_x_mm
        current_y_mm = target_y_mm

        print(f"[UPDATE POS] current_x_mm={current_x_mm:.3f}, current_y_mm={current_y_mm:.3f}")

    print("\n========== RETURN HOME ==========")

    dx_mm = 0 - current_x_mm
    dy_mm = 0 - current_y_mm

    print(f"[HOME DELTA] dx_mm={dx_mm:.3f}, dy_mm={dy_mm:.3f}")

    steps_x = mm_to_steps(dx_mm, "x")
    steps_y = mm_to_steps(dy_mm, "y")

    print("[LASER] OFF (HOMING)")
    lgpio.gpio_write(h, RELAY, 0)

    move_xy(steps_x, steps_y, h)

    lgpio.gpiochip_close(h)

    print("========== END xyz() ==========")
    print("Machine at home (0,0)")


# ======================================================
# EXAMPLE USAGE
# ======================================================

if __name__ == "__main__":
    
    # Example: Detected weeds at these positions
    center_list_x = [100, 500, 1000, 1500, 2000, 2009, 2100]
    center_list_y = [200, 600, 1000, 1400, 1800, 106, 1500]
    
    # Run with default crop coordinates and tolerance
    xyz(center_list_x, center_list_y)
