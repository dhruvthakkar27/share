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

IMAGE_WIDTH  = 3444 #x axis
IMAGE_HEIGHT = 3941 #y axis

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
# HARD-CODED CROP PIXEL COORDINATES
# These positions must NEVER be targeted
# ======================================================

CROP_COORDINATES = [
    (2009, 106),
    (2109, 1519),
    (2103, 2542),
    (1067, 3270),
    (941, 2134),
    (2913, 929),
    (3001, 2015),
    (3124, 2990),
    (1838, 1074),
]

# Pixel tolerance for matching crop points
CROP_MATCH_TOLERANCE_PX = 10


# ======================================================
# FILTER FUNCTION - REMOVE CROP PIXEL MATCHES
# ======================================================

def filter_exact_crop_matches(center_list_x_px,
                              center_list_y_px,
                              crop_coords=CROP_COORDINATES,
                              match_tolerance_px=CROP_MATCH_TOLERANCE_PX):
    """
    Removes any (x, y) that matches a crop coordinate.
    Matching condition:
    |x - crop_x| <= tolerance AND |y - crop_y| <= tolerance
    """

    print("\n" + "=" * 60)
    print("🛡️  CROP PIXEL MATCH FILTER")
    print("=" * 60)

    filtered_x = []
    filtered_y = []
    removed = 0

    for idx, (wx, wy) in enumerate(zip(center_list_x_px, center_list_y_px)):
        is_crop = False

        for cx, cy in crop_coords:
            if abs(wx - cx) <= match_tolerance_px and abs(wy - cy) <= match_tolerance_px:
                print(f"❌ Removed weed ({wx}, {wy}) → crop match ({cx}, {cy})")
                removed += 1
                is_crop = True
                break

        if not is_crop:
            filtered_x.append(wx)
            filtered_y.append(wy)
            print(f"✅ Kept weed ({wx}, {wy})")

    print("-" * 60)
    print(f"Removed: {removed}")
    print(f"Remaining targets: {len(filtered_x)}")
    print("=" * 60 + "\n")

    return filtered_x, filtered_y


# ======================================================
# PIXEL → MM CONVERSION (ABSOLUTE)
# ======================================================

def pixel_to_mm(px, py):
    print(f"[PIXEL INPUT] px={px}, py={py}")

    x_mm = (px / IMAGE_WIDTH) * MAX_MM_X
    y_mm = (py / IMAGE_HEIGHT) * MAX_MM_Y

    print(f"[PIXEL → MM] x_mm={x_mm:.3f}, y_mm={y_mm:.3f}")
    return x_mm, y_mm


# ======================================================
# MM → STEPS CONVERSION
# ======================================================

def mm_to_steps(mm, axis):
    pitch = BALL_SCREW_PITCH_X if axis == "x" else BALL_SCREW_PITCH_Y
    resolution = RESOLUTION_X if axis == "x" else RESOLUTION_Y

    steps = int((mm / pitch) * resolution)
    print(f"[MM → STEPS] axis={axis}, mm={mm:.3f}, steps={steps}")

    return steps


# ======================================================
# LOW-LEVEL MOTOR CONTROL
# ======================================================

def move_motor(steps, h, dir_pin, step_pin):
    direction = CW if steps >= 0 else CCW
    lgpio.gpio_write(h, dir_pin, direction)

    for _ in range(abs(steps)):
        lgpio.gpio_write(h, step_pin, 1)
        time.sleep(STEP_DELAY)
        lgpio.gpio_write(h, step_pin, 0)
        time.sleep(STEP_DELAY)


# ======================================================
# MOVE X & Y TOGETHER
# ======================================================

def move_xy(steps_x, steps_y, h):
    px = multiprocessing.Process(
        target=move_motor, args=(steps_x, h, X_DIR, X_STEP)
    )
    py = multiprocessing.Process(
        target=move_motor, args=(steps_y, h, Y_DIR, Y_STEP)
    )

    px.start()
    py.start()

    px.join()
    py.join()


# ======================================================
# MAIN EXECUTION FUNCTION
# ======================================================

def xyz(center_list_x_px, center_list_y_px):
    print("\n========== START xyz() ==========")
    print("Input X:", center_list_x_px)
    print("Input Y:", center_list_y_px)

    # ======================================================
    # REMOVE CROP COORDINATE MATCHES
    # ======================================================

    center_list_x_px, center_list_y_px = filter_exact_crop_matches(
        center_list_x_px,
        center_list_y_px
    )

    if not center_list_x_px:
        print("⚠️ No valid weed targets after filtering")
        print("========== END xyz() ==========")
        return

    # ======================================================
    # GPIO INIT
    # ======================================================

    h = lgpio.gpiochip_open(GPIO_CHIP)

    lgpio.gpio_claim_output(h, X_DIR, 0)
    lgpio.gpio_claim_output(h, X_STEP, 0)
    lgpio.gpio_claim_output(h, Y_DIR, 0)
    lgpio.gpio_claim_output(h, Y_STEP, 0)
    lgpio.gpio_claim_output(h, RELAY, 0)

    current_x_mm = 0.0
    current_y_mm = 0.0

    for idx, (px, py) in enumerate(zip(center_list_x_px, center_list_y_px)):
        print(f"\n[TARGET {idx+1}]")

        target_x_mm, target_y_mm = pixel_to_mm(px, py)

        dx_mm = target_x_mm - current_x_mm
        dy_mm = target_y_mm - current_y_mm

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

    # ======================================================
    # RETURN HOME
    # ======================================================

    dx_mm = -current_x_mm
    dy_mm = -current_y_mm

    steps_x = mm_to_steps(dx_mm, "x")
    steps_y = mm_to_steps(dy_mm, "y")

    move_xy(steps_x, steps_y, h)

    lgpio.gpiochip_close(h)

    print("========== END xyz() ==========")
    print("Machine at HOME (0,0)")


# ======================================================
# EXAMPLE USAGE
# ======================================================

if __name__ == "__main__":

    center_list_x = [0]
    center_list_y = [3444]

    xyz(center_list_x, center_list_y)
