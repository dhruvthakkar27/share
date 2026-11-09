import lgpio
from time import sleep
import multiprocessing
import sys

# Constants for X axis
RESOLUTION_X = 400
BALL_SCREW_PITCH_X = 5
MAX_LENGTH_X = 790

# Constants for Y axis
RESOLUTION_Y = 800
BALL_SCREW_PITCH_Y = 10
MAX_LENGTH_Y = 790

# Direction flags
cw_direction = False
ccw_direction = True

# Convert mm to steps for X
def mm_to_steps_x(distance_mm):
    distance_mm = min(distance_mm, MAX_LENGTH_X)
    rotations = distance_mm / BALL_SCREW_PITCH_X
    return int(rotations * RESOLUTION_X)

# Convert mm to steps for Y
def mm_to_steps_y(distance_mm):
    distance_mm = min(distance_mm, MAX_LENGTH_Y)
    rotations = distance_mm / BALL_SCREW_PITCH_Y
    return int(rotations * RESOLUTION_Y)

# Move one axis
def move_axis(steps, chip_handle_dir, gpio_dir, chip_handle_pulse, gpio_pulse):
    direction = cw_direction if steps >= 0 else ccw_direction
    lgpio.gpio_write(chip_handle_dir, gpio_dir, int(direction))

    for _ in range(abs(int(steps))):
        lgpio.gpio_write(chip_handle_pulse, gpio_pulse, 1)
        sleep(0.00045)
        lgpio.gpio_write(chip_handle_pulse, gpio_pulse, 0)
        sleep(0.00045)

# X movement
def run_step_x(steps_x, chip_handle_dir_x, gpio_dir_x, chip_handle_pulse_x, gpio_pulse_x):
    move_axis(steps_x, chip_handle_dir_x, gpio_dir_x, chip_handle_pulse_x, gpio_pulse_x)

# Y movement
def run_step_y(steps_y, chip_handle_dir_y, gpio_dir_y, chip_handle_pulse_y, gpio_pulse_y):
    move_axis(steps_y, chip_handle_dir_y, gpio_dir_y, chip_handle_pulse_y, gpio_pulse_y)

# Main dual-axis stepper function
def main(x_distance_mm, y_distance_mm):
    steps_x = mm_to_steps_x(x_distance_mm)
    steps_y = mm_to_steps_y(y_distance_mm)

    # GPIO assignments
    gpio_dir_x = 4     # BCM4 (Pin 7)
    gpio_pulse_x = 5   # BCM5 (Pin 29)
    gpio_dir_y = 6     # BCM6 (Pin 31)
    gpio_pulse_y = 8   # BCM8 (Pin 24)

    chip_dir_x = 0
    chip_pulse_x = 0
    chip_dir_y = 0
    chip_pulse_y = 0

    # Open chips
    h_dir_x = lgpio.gpiochip_open(chip_dir_x)
    h_pulse_x = lgpio.gpiochip_open(chip_pulse_x)
    h_dir_y = lgpio.gpiochip_open(chip_dir_y)
    h_pulse_y = lgpio.gpiochip_open(chip_pulse_y)

    # Claim pins
    lgpio.gpio_claim_output(h_dir_x, gpio_dir_x, 0)
    lgpio.gpio_claim_output(h_pulse_x, gpio_pulse_x, 0)
    lgpio.gpio_claim_output(h_dir_y, gpio_dir_y, 0)
    lgpio.gpio_claim_output(h_pulse_y, gpio_pulse_y, 0)

    process_x = multiprocessing.Process(target=run_step_x, args=(steps_x, h_dir_x, gpio_dir_x, h_pulse_x, gpio_pulse_x))
    process_y = multiprocessing.Process(target=run_step_y, args=(steps_y, h_dir_y, gpio_dir_y, h_pulse_y, gpio_pulse_y))

    try:
        print('Moving both axes...')
        process_x.start()
        process_y.start()
        process_x.join()
        process_y.join()
        print('Movement completed.')

    except KeyboardInterrupt:
        print("\nCtrl+C detected during movement. Terminating motors...")
        process_x.terminate()
        process_y.terminate()
        process_x.join()
        process_y.join()

    finally:
        lgpio.gpiochip_close(h_dir_x)
        lgpio.gpiochip_close(h_pulse_x)
        lgpio.gpiochip_close(h_dir_y)
        lgpio.gpiochip_close(h_pulse_y)

# Run full coordinate list
def xyz(center_list_x, center_list_y):
    x1 = 0
    y1 = 0
    center_list_x.append(0)
    center_list_y.append(0)

    print("center_list_x", center_list_x)
    print("center_list_y", center_list_y)

    # Laser GPIO (BCM 12 = Pin 32, chip 4)
    laser_chip = 4
    laser_pin = 12
    h_laser = lgpio.gpiochip_open(laser_chip)
    lgpio.gpio_claim_output(h_laser, laser_pin, 1)

    try:
        for i in range(len(center_list_x)):
            x2 = center_list_x[i]
            y2 = center_list_y[i]
            dist_x = x2 - x1
            dist_y = y2 - y1
            main(dist_x, dist_y)
            x1 = x2
            y1 = y2

            if i != len(center_list_x) - 1:
                print("i", i)
                lgpio.gpio_write(h_laser, laser_pin, 0)  # Laser on
                print("laser on")
                sleep(2)
                lgpio.gpio_write(h_laser, laser_pin, 1)  # Laser off
                print("laser off")
            else:
                lgpio.gpio_write(h_laser, laser_pin, 1)
                print("home pos reached")

    except KeyboardInterrupt:
        print("\nCtrl+C pressed during laser/motion loop. Aborting...")

    finally:
        # Always turn off laser and close chip
        lgpio.gpio_write(h_laser, laser_pin, 1)
        lgpio.gpiochip_close(h_laser)
        print("Laser GPIO cleaned up.")

# Top-level execution
if __name__ == "__main__":
    center_list_x = [700]
    center_list_y = [700]

    try:
        xyz(center_list_x, center_list_y)
    except KeyboardInterrupt:
        print("\nCtrl+C pressed. Final cleanup and exit...")

    finally:
        print("Program exited cleanly.")
        sys.exit(0)

