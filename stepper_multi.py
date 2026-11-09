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

IMAGE_WIDTH  = 3490
IMAGE_HEIGHT = 3390

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

        #if i % 500 == 0 and i != 0:
            #print(f"[MOTOR] step pulse {i}/{abs(steps)}")


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

def xyz(center_list_x_px, center_list_y_px):
    print("========== START xyz() ==========")
    print("Input center_list_x:", center_list_x_px)
    print("Input center_list_y:", center_list_y_px)

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
        print(f"[TARGET {idx}] Processing new target")

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

    center_list_x = [0]
    center_list_y = [-3390]

    xyz(center_list_x, center_list_y)
