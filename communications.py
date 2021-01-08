import socket
import threading
from constants import *


GENERAL_CONNECTION = None
EXIT_CONNECTION = None
MOTORS = []
SENSORS = []
BRICK_BUTTONS = None
RUNNING = True


def contains(container: list, subset: list):
    """Returns if all of the items in the subset are contained in the container"""
    for item in subset:
        inside = False
        for contain in container:
            if contain == item:
                inside = True
                break
        if not inside:
            return False
    return True


def has_one(container: list, subset: list):
    """Returns if one of the items from subset are in the container"""
    for item in subset:
        if item in container:
            return True
    return False


def is_number(s: str):
    try:
        float(s)
        return True
    except ValueError:
        return False


def send(connection: socket, data: str):
    """Sends data as bytes with a 4 byte header acting as the message's length (big endian)"""
    data = data.encode()
    connection.send(len(data).to_bytes(4, "big"))
    connection.send(data)


def receive(connection: socket):
    """Receives data according to the 4 bytes header protocol, see send function"""
    length = int.from_bytes(connection.recv(4), "big")
    return connection.recv(length).decode()


def str_to_bool(string: str):
    """
    Converts a string to boolean, ignores capitalization\n
    Return - value, validity (is True/False and not something else)
    """
    if string.lower() == "true":
        return True, True
    elif string.lower() == "false":
        return False, True
    else:
        return False, False


def motor_run_angle(parts: list):
    """
    Runs the motor at a constant speed by a given angle.\n
    parts = [port, speed, angle, then=Stop.HOLD, wait=True]\n
    Note that if you want to specify the wait value you must specify the then value.\n
    https://pybricks.github.io/ev3-micropython/ev3devices.html#pybricks.ev3devices.Motor.run_target
    """

    if len(parts) == 5:
        return ERROR_WRONG_ARGUMENT_COUNT

    motor = None
    speed = 0
    angle = 0
    then = STOPS["HOLD"]
    wait = True

    if parts[1] in MOTORS.keys():
        motor = MOTORS[parts[1]]
    else:
        return ERROR_INVALID_PORT

    if motor == None:
        return ERROR_INVALID_MOTOR

    if is_number(parts[2]):
        speed = int(parts[2])
    else:
        return ERROR_NOT_A_NUMBER

    if is_number(parts[3]):
        angle = int(parts[3])
    else:
        return ERROR_NOT_A_NUMBER

    if len(parts) > 5:
        if parts[4] in STOPS.keys():
            then = STOPS[parts[4]]
        else:
            return ERROR_INVALID_STOP
        wait, valid = str_to_bool(parts[5])
        if not valid:
            return ERROR_NOT_BOOLEAN

    motor.run_angle(speed, angle, then, wait)
    return SUCCESS


def motor_run_time(parts: list):
    """
    Runs the motor at a constant speed for a given period of time.\n
    parts = [port, time, angle, then=Stop.HOLD, wait=True]\n
    Note that if you want to specify the wait value you must specify the then value.\n
    https://pybricks.github.io/ev3-micropython/ev3devices.html#pybricks.ev3devices.Motor.motor_run_time
    """

    if len(parts) == 5:
        return ERROR_WRONG_ARGUMENT_COUNT

    motor = None
    speed = 0
    time = 0
    then = STOPS["HOLD"]
    wait = False

    if parts[1] in MOTORS.keys():
        motor = MOTORS[parts[1]]
    else:
        return ERROR_INVALID_PORT

    if motor == None:
        return ERROR_INVALID_MOTOR

    if is_number(parts[2]):
        speed = int(parts[2])
    else:
        return ERROR_NOT_A_NUMBER

    if is_number(parts[3]):
        time = int(parts[3])
    else:
        return ERROR_NOT_A_NUMBER

    if len(parts) > 4:
        if parts[4] in STOPS.keys():
            then = STOPS[parts[4]]
        else:
            return ERROR_INVALID_STOP

        wait, valid = str_to_bool(parts[5])
        if not valid:
            return ERROR_NOT_BOOLEAN

    motor.run_time(speed, time, then, wait)
    return SUCCESS


def motor_run(parts: list):
    """
    Runs the motor indefinitely\n
    parts = [port, speed]
    """
    if len(parts) != 3:
        return ERROR_WRONG_ARGUMENT_COUNT

    motor = None
    speed = 0

    if parts[1] in MOTORS.keys():
        motor = MOTORS[parts[1]]
    else:
        return ERROR_INVALID_PORT

    if motor == None:
        return ERROR_INVALID_MOTOR

    if is_number(parts[2]):
        speed = int(parts[2])
    else:
        return ERROR_NOT_A_NUMBER

    motor.run(speed)
    return SUCCESS


def motor_stop(parts: list):
    """
    Stops the motor and lets it spin freely. The motor gradually stops due to friction.\n
    parts = [port]
    """
    if len(parts) != 2:
        return ERROR_WRONG_ARGUMENT_COUNT

    motor = None

    if parts[1] in MOTORS.keys():
        motor = MOTORS[parts[1]]
    else:
        return ERROR_INVALID_PORT
    if motor == None:
        return ERROR_INVALID_MOTOR

    motor.stop()
    return SUCCESS


def motor_brake(parts: list):
    """
    Passively brakes the motor.\n
    The motor stops due to friction, plus the voltage that is generated while the motor is still moving.\n
    parts = [port]
    """
    if len(parts) != 2:
        return ERROR_WRONG_ARGUMENT_COUNT

    motor = None

    if parts[1] in MOTORS.keys():
        motor = MOTORS[parts[1]]
    else:
        return ERROR_INVALID_PORT
    if motor == None:
        return ERROR_INVALID_MOTOR

    motor.brake()
    return SUCCESS


def motor_hold(parts: list):
    """
    Stops the motor and actively holds it at its current angle.\n
    parts = [port]
    """
    if len(parts) != 2:
        return ERROR_WRONG_ARGUMENT_COUNT

    motor = None
    if parts[1] in MOTORS.keys():
        motor = MOTORS[parts[1]]
    else:
        return ERROR_INVALID_PORT
    if motor == None:
        return ERROR_INVALID_MOTOR

    motor.hold()
    return SUCCESS


def sensor_touch(parts: list):
    """
    Returns the status of the touch sensor as a boolean string\n
    parts = [port]
    """
    if len(parts) != 2:
        return ERROR_WRONG_ARGUMENT_COUNT

    sensor = None
    if parts[1] in SENSORS.keys():
        sensor = SENSORS[parts[1]]
    else:
        return ERROR_INVALID_PORT
    if sensor == None:
        return ERROR_INVALID_TOUCH_SENSOR

    return str(sensor.pressed())


def sensor_touch_wait_until_pressed(parts: list):
    """
    Returns when the touch sensor has been pressed\n
    parts = [port]
    """
    if len(parts) != 2:
        return ERROR_WRONG_ARGUMENT_COUNT

    sensor = None
    if parts[1] in SENSORS.keys():
        sensor = SENSORS[parts[1]]
    else:
        return ERROR_INVALID_PORT
    if sensor == None:
        return ERROR_INVALID_TOUCH_SENSOR

    while not sensor.pressed() and RUNNING:
        pass

    return SUCCESS if RUNNING else EXIT


def sensor_touch_wait_until_clicked(parts: list):
    """
    Returns when the touch sensor is clicked (off -> on -> off)\n
    parts = [port]
    """
    if len(parts) != 2:
        return ERROR_WRONG_ARGUMENT_COUNT

    sensor = None
    if parts[1] in SENSORS.keys():
        sensor = SENSORS[parts[1]]
    else:
        return ERROR_INVALID_PORT
    if sensor == None:
        return ERROR_INVALID_TOUCH_SENSOR

    while sensor.pressed() and RUNNING:
        pass

    while not sensor.pressed() and RUNNING:
        pass

    while sensor.pressed() and RUNNING:
        pass

    return SUCCESS if RUNNING else EXIT


def buttons_pressed(parts: list):
    """
    Takes in a list of buttons (as string, seperated by spaces) and 
    returns when all of them are pressed at the same time.
    """
    if len(parts) < 2:
        return ERROR_WRONG_ARGUMENT_COUNT

    test_buttons = []
    for i in range(1, len(parts)):
        if parts[i] in BUTTONS.keys():
            test_buttons.append(BUTTONS[parts[i]])
        else:
            return ERROR_INVALID_BUTTON

    while not contains(BRICK_BUTTONS.pressed(), test_buttons) and RUNNING:
        pass

    return SUCCESS if RUNNING else EXIT


def buttons_clicked(parts: list):
    """
    Takes in a list of buttons (as string, seperated by spaces) and 
    returns when all of them are clicked (off -> on -> off) at the same time.
    """
    if len(parts) < 2:
        return ERROR_WRONG_ARGUMENT_COUNT

    test_buttons = []
    for i in range(1, len(parts)):
        if parts[i] in BUTTONS.keys():
            test_buttons.append(BUTTONS[parts[i]])
        else:
            return ERROR_INVALID_BUTTON

    while has_one(BRICK_BUTTONS.pressed(), test_buttons) and RUNNING:
        pass

    while not contains(BRICK_BUTTONS.pressed(), test_buttons) and RUNNING:
        pass

    while has_one(BRICK_BUTTONS.pressed(), test_buttons) and RUNNING:
        pass

    return SUCCESS if RUNNING else EXIT


def button_status(parts: list):
    """
    Returns whether the button is pressed or not\n
    parts = [port]
    """
    if len(parts) != 2:
        return ERROR_WRONG_ARGUMENT_COUNT

    button = None

    if parts[1] in BUTTONS.keys():
        button = BUTTONS[parts[1]]
    else:
        return ERROR_INVALID_BUTTON

    return str(button in BRICK_BUTTONS.pressed())


COMMANDS = {
    "motor_run_angle": motor_run_angle,
    "motor_run_time": motor_run_time,
    "motor_run": motor_run,
    "motor_stop": motor_stop,
    "motor_brake": motor_brake,
    "motor_hold": motor_hold,
    "sensor_touch": sensor_touch,
    "sensor_touch_wait_until_clicked": sensor_touch_wait_until_clicked,
    "sensor_touch_wait_until_pressed": sensor_touch_wait_until_pressed,
    "buttons_clicked": buttons_clicked,
    "buttons_pressed": buttons_pressed,
    "button_status": button_status
}


def start(motors: list, sensors: list, brick_buttons: list):
    """Starts the server"""
    global GENERAL_CONNECTION
    global EXIT_CONNECTION
    global MOTORS
    global SENSORS
    global BRICK_BUTTONS

    MOTORS = motors
    SENSORS = sensors
    BRICK_BUTTONS = brick_buttons

    general_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    general_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    general_server.bind(('0.0.0.0', GENERAL_PORT))
    general_server.listen(5)

    print("Listening")

    GENERAL_CONNECTION = general_server.accept()[0]

    exit_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    exit_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    exit_server.bind(('0.0.0.0', EXIT_PORT))
    exit_server.listen(5)
    EXIT_CONNECTION = exit_server.accept()[0]

    t = threading.Thread(target=exit)
    t.daemon = True
    t.start()

    run()

    GENERAL_CONNECTION.close()
    general_server.close()
    EXIT_CONNECTION.close()
    exit_server.close()


def exit():
    global RUNNING

    test_buttons = BUTTONS["CENTER"], BUTTONS["LEFT"]
    while has_one(BRICK_BUTTONS.pressed(), test_buttons):
        pass

    while not contains(BRICK_BUTTONS.pressed(), test_buttons):
        pass

    while has_one(BRICK_BUTTONS.pressed(), test_buttons):
        pass

    RUNNING = False
    send(EXIT_CONNECTION, EXIT)


def run():
    """Handles communication, should be the only function receiving in the program"""

    data = receive(GENERAL_CONNECTION)
    print(data)
    while data != "exit" and RUNNING:
        parts = data.split(" ")

        if parts[0] in COMMANDS:
            out = COMMANDS[parts[0]](parts)
            send(GENERAL_CONNECTION, out)
        else:
            send(GENERAL_CONNECTION, ERROR_UNRECOGNIZED_COMMAND)

        data = receive(GENERAL_CONNECTION)
        print(data)


