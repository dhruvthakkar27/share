import lgpio
from time import sleep
import multiprocessing
import threading
import sys
import select

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

# Keyboard listener to stop movement
def keyboard_listener(stop_event):
    print("Press 's' + Enter to stop movement.")
    while not stop_event.is_set():
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            line = sys.stdin.readline()
            if 's' in line.lower():
                print("Stop signal received.")
                stop_event.set()
                break

# Move one axis
def move_axis(steps, chip_handle_dir, gpio_dir, chip_handle_pulse, gpio_pulse, stop_event):
    direction = cw_direction if steps >= 0 else ccw_direction
    lgpio.gpio_write(chip_handle_dir, gpio_dir, int(direction))

    for _ in range(abs(int(steps))):
        if stop_event.is_set():
            print("Movement stopped.")
            break
        lgpio.gpio_write(chip_handle_pulse, gpio_pulse, 1)
        sleep(0.00045)
        lgpio.gpio_write(chip_handle_pulse, gpio_pulse, 0)
        sleep(0.00045)

# X movement
def run_step_x(steps_x, chip_handle_dir_x, gpio_dir_x, chip_handle_pulse_x, gpio_pulse_x, stop_event):
    move_axis(steps_x, chip_handle_dir_x, gpio_dir_x, chip_handle_pulse_x, gpio_pulse_x, stop_event)

# Y movement
def run_step_y(steps_y, chip_handle_dir_y, gpio_dir_y, chip_handle_pulse_y, gpio_pulse_y, stop_event):
    move_axis(steps_y, chip_handle_dir_y, gpio_dir_y, chip_handle_pulse_y, gpio_pulse_y, stop_event)

# Main movement executor
def xyz(center_list_x, center_list_y):
    if not center_list_x or not center_list_y:
        print("No coordinates provided.")
        return

    x1 = 0
    y1 = 0

    print("center_list_x", center_list_x)
    print("center_list_y", center_list_y)

    laser_chip = 4
    laser_pin = 12
    h_laser = lgpio.gpiochip_open(laser_chip)
    lgpio.gpio_claim_output(h_laser, laser_pin, 1)

    stop_event = multiprocessing.Event()
    threading.Thread(target=keyboard_listener, args=(stop_event,), daemon=True).start()

    for i in range(len(center_list_x)):
        if stop_event.is_set():
            break

        x2 = center_list_x[i]
        y2 = center_list_y[i]
        dist_x = x2 - x1
        dist_y = y2 - y1
        main(dist_x, dist_y, stop_event)
        x1 = x2
        y1 = y2

        if i != len(center_list_x) - 1:
            print("i", i)
            lgpio.gpio_write(h_laser, laser_pin, 0)
            print("laser on")
            sleep(2)
            lgpio.gpio_write(h_laser, laser_pin, 1)
            print("laser off")
        else:
            print("End of list reached.")

    lgpio.gpiochip_close(h_laser)

# Main dual-axis stepper function
def main(x_distance_mm, y_distance_mm, stop_event):
    steps_x = mm_to_steps_x(x_distance_mm)
    steps_y = mm_to_steps_y(y_distance_mm)

    gpio_dir_x = 4
    gpio_pulse_x = 5
    gpio_dir_y = 6
    gpio_pulse_y = 8

    chip_dir_x = chip_pulse_x = chip_dir_y = chip_pulse_y = 0

    h_dir_x = lgpio.gpiochip_open(chip_dir_x)
    h_pulse_x = lgpio.gpiochip_open(chip_pulse_x)
    h_dir_y = lgpio.gpiochip_open(chip_dir_y)
    h_pulse_y = lgpio.gpiochip_open(chip_pulse_y)

    lgpio.gpio_claim_output(h_dir_x, gpio_dir_x, 0)
    lgpio.gpio_claim_output(h_pulse_x, gpio_pulse_x, 0)
    lgpio.gpio_claim_output(h_dir_y, gpio_dir_y, 0)
    lgpio.gpio_claim_output(h_pulse_y, gpio_pulse_y, 0)

    try:
        print('Moving both axes...')

        process_x = multiprocessing.Process(target=run_step_x, args=(steps_x, h_dir_x, gpio_dir_x, h_pulse_x, gpio_pulse_x, stop_event))
        process_y = multiprocessing.Process(target=run_step_y, args=(steps_y, h_dir_y, gpio_dir_y, h_pulse_y, gpio_pulse_y, stop_event))

        process_x.start()
        process_y.start()
        process_x.join()
        process_y.join()

        print('Movement completed.')

    except KeyboardInterrupt:
        print("KeyboardInterrupt received. Exiting...")

    finally:
        lgpio.gpiochip_close(h_dir_x)
        lgpio.gpiochip_close(h_pulse_x)
        lgpio.gpiochip_close(h_dir_y)
        lgpio.gpiochip_close(h_pulse_y)

# Example test
if __name__ == "__main__":
    center_list_x = [-700]
    center_list_y = [700]
    xyz(center_list_x, center_list_y)
