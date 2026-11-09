import lgpio
import time
import multiprocessing
import datetime


# ==========================
# MACHINE CONSTANTS
# ==========================
RESOLUTION_X = 400           # steps per revolution
RESOLUTION_Y = 800

BALL_SCREW_PITCH_X = 5      # mm per revolution
BALL_SCREW_PITCH_Y = 10

STEP_DELAY = 0.00045           # pulse width
REST_TIME = 8                # seconds

CW  = 0
CCW = 1

# ==========================
# GPIO PINS (BCM)
# ==========================
X_DIR   = 17 #pin 11
X_STEP  = 27 #pin 13
Y_DIR   = 22 #pin15 
Y_STEP  = 23 #pin 16
RELAY   = 12 #pin32

GPIO_CHIP = 0

# ==========================
# CONVERSION (mm → steps)
# ==========================
def mm_to_steps(mm, axis="x"):
    pitch = BALL_SCREW_PITCH_X if axis == "x" else BALL_SCREW_PITCH_Y
    resolution = RESOLUTION_X if axis == "x" else RESOLUTION_Y
    rotations = mm / pitch
    return int(rotations * resolution)

# ==========================
# MOTOR MOVE
# ==========================
def move_motor(steps, h, dir_pin, step_pin):
    direction = CW if steps >= 0 else CCW
    lgpio.gpio_write(h, dir_pin, direction)

    for _ in range(abs(steps)):
        lgpio.gpio_write(h, step_pin, 1)
        time.sleep(STEP_DELAY)
        lgpio.gpio_write(h, step_pin, 0)
        time.sleep(STEP_DELAY)

# ==========================
# MAIN MOTION FUNCTION
# ==========================
def move_xy(steps_x, steps_y, h):
    px = multiprocessing.Process(
        target=move_motor, args=(steps_x, h, X_DIR, X_STEP)
    )
    py = multiprocessing.Process(
        target=move_motor, args=(steps_y, h, Y_DIR, Y_STEP)
    )
    print("Movement start")
    start=datetime.datetime.now()
    px.start()
    py.start()
    px.join()
    py.join()
    end=datetime.datetime.now()
    print("time taken : ",end-start)
    print("movement end")
# ==========================
# PATH EXECUTION
# ==========================
def xyz(center_list_x, center_list_y):

    # Append home position (0,0)
    center_list_x.append(0)
    center_list_y.append(0)
    print("centerlists :",center_list_x,center_list_y)

    h = lgpio.gpiochip_open(GPIO_CHIP)

    lgpio.gpio_claim_output(h, X_DIR, 0)
    lgpio.gpio_claim_output(h, X_STEP, 0)
    lgpio.gpio_claim_output(h, Y_DIR, 0)
    lgpio.gpio_claim_output(h, Y_STEP, 0)
    lgpio.gpio_claim_output(h, RELAY, 0)

    current_x = 0
    current_y = 0

    for x_mm, y_mm in zip(center_list_x, center_list_y):

        dx_mm = x_mm - current_x
        dy_mm = y_mm - current_y

        steps_x = mm_to_steps(dx_mm, "x")
        steps_y = mm_to_steps(dy_mm, "y")

        # Move motors
        move_xy(steps_x, steps_y, h)

        # Relay ON for 8 seconds
        
        lgpio.gpio_write(h, RELAY, 1)
        print("laser on")
        time.sleep(REST_TIME)
        lgpio.gpio_write(h, RELAY, 0)
        print("laser off")
        
        current_x = x_mm
        current_y = y_mm

    lgpio.gpiochip_close(h)

# ==========================
# EXAMPLE RUN
# ==========================
if __name__ == "__main__":
    center_list_x = [-800]   # mm
    center_list_y = [0]    # mm

    xyz(center_list_x, center_list_y)
