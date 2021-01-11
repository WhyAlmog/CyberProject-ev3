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
    """Returns if all of the items in the subset are contained in the container

    Args:
        container (list): list of the container items
        subset (list): list of items to test if included inside container

    Returns:
        bool: if all of the items inside of subset are contained in container
    """
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
    """Tests if a list contains at least one item from a sub-list

    Args:
        container (list): list of container items
        subset (list): list of items to tests if included in Container

    Returns:
        [type]: if at least one item from subset is inside of container
    """
    for item in subset:
        if item in container:
            return True
    return False


def is_number(s: str):
    """Tests if a given string represents a number

    Args:
        s (str): string representation of a number

    Returns:
        bool: if the given string represents a number or not
    """
    try:
        float(s)
        return True
    except ValueError:
        return False


def send(connection: socket, data: str):
    """Sends data through the socket according to the following protocol:
    [4 bytes, big endian - data length] + [data as byte-stream]

    Args:
        connection (socket): socket to send the data through
        data (str): string representation of the data
    """
    data = data.encode()
    connection.send(len(data).to_bytes(4, "big"))
    connection.send(data)


def receive(connection: socket):
    """Receives data from the socket according to the following protocol:
    [4 bytes, big endian - data length] + [data as byte-stream]

    Args:
        connection (socket): socket to receive the data from
    Returns:
        str: data read from the socket represented as a string
    """
    length = int.from_bytes(connection.recv(4), "big")
    return connection.recv(length).decode()


def str_to_bool(string: str):
    """Converts a string to boolean (ignoring capitalization), also checks if the string is a valid boolean string.
    invalid strings return False in the first value, example:
    str_to_bool("test") will return False, False

    Args:
        string (str):  the string containing the boolean text

    Returns:
        tuple: first value is the value of the string, second value is the validity of the string
    """
    if string.lower() == "true":
        return True, True
    elif string.lower() == "false":
        return False, True
    else:
        return False, False


def motor_run_angle(parts: list):
    """Runs the motor at a constant speed by a given angle. 
    Note that if you want to specify the wait value you must specify the then value.

    https://pybricks.github.io/ev3-micropython/ev3devices.html#pybricks.ev3devices.Motor.run_target

    Args:
        parts (list): [port, speed, angle, then=Stop.HOLD, wait=True]

    Returns:
        str: success/error
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
    """Runs the motor at a constant speed for a given period of time.
    Note that if you want to specify the wait value you must specify the then value.
    https://pybricks.github.io/ev3-micropython/ev3devices.html#pybricks.ev3devices.Motor.motor_run_time

    Args:
        parts (list): [port, speed, time, then=Stop.HOLD, wait=True]

    Returns:
        str: success/error
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
    """Runs the motor indefinitely.

    Args:
        parts (list): [port, speed]

    Returns:
        str: success/error
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
    """Stops the motor and lets it spin freely. The motor gradually stops due to friction.

    Args:
        parts (list): [port]

    Returns:
        str: success/error
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
    """Passively brakes the motor.
    The motor stops due to friction, plus the voltage that is generated while the motor is still moving.

    Args:
        parts (list): [port]

    Returns:
        str: success/error
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
    """Stops the motor and actively holds it at its current angle.

    Args:
        parts (list): [port]

    Returns:
        str: success/error
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
    """Returns the status of the touch sensor as a boolean string

    Args:
        parts (list): [port]

    Returns:
        str: success/error
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
    """Returns when the touch sensor has been pressed.

    Args:
        parts (list): [port]

    Returns:
        str: success/exit/error
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
    """Returns when the touch sensor is clicked (off -> on -> off)

    Args:
        parts (list): [port]

    Returns:
        str: success/exit/error
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
    """Takes in a list of buttons (as string, seperated by spaces) and 
    returns when all of them are pressed at the same time.

    Args:
        parts (list): [button]

    Returns:
       str: success/exit/error
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
    """Takes in a list of buttons (as string, seperated by spaces) and 
    returns when all of them are clicked (off -> on -> off) at the same time.

    Args:
        parts (list): [button]

    Returns:
        str: success/exit/error
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
    """Returns whether the button is pressed or not

    Args:
        parts (list): [button]

    Returns:
        str: success/exit/error
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
    """Starts both of the general and exit server and their respective threads.

    Args:
        motors (list): list of the EV3 motors
        sensors (list): list of the EV3 sensors
        brick_buttons (list): list of the EV3 brick buttons
    """
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
    """Takes care of exiting the program. When both the center and the left brick buttons are pressed,
    the RUNNING flag will be set to False and EXIT will be sent to the client.
    """
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
    """Takes care of communications on the general socket and command processing.
    Receive from the socket -> process the command -> send response."""

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
