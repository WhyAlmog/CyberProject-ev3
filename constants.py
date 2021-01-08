from pybricks.parameters import Stop, Button  # type:ignore

GENERAL_PORT = 8070
EXIT_PORT = 8071  # sometimes requests on GENERAL_PORT are blocking, so this port is only for exit commands

ERROR_WRONG_ARGUMENT_COUNT = "Error: Wrong argument count"
ERROR_INVALID_PORT = "Error: Invalid port"
ERROR_INVALID_MOTOR = "Error: No motor is connected to this port"
ERROR_INVALID_BUTTON = "Error: Invalid brick button"
ERROR_INVALID_TOUCH_SENSOR = "Error: No touch sensor is connected to this port"
ERROR_NOT_A_NUMBER = "Error: Value is not a number"
ERROR_INVALID_STOP = "Error: Invalid stop type"
ERROR_NOT_BOOLEAN = "Error: Value is not boolean"
ERROR_UNRECOGNIZED_COMMAND = "Error: Unrecognized command"

SUCCESS = "success"
EXIT = "exit"

STOPS = {"COAST": Stop.COAST,
         "BRAKE": Stop.BRAKE,
         "HOLD": Stop.HOLD}

BUTTONS = {"UP": Button.UP,
           "DOWN": Button.DOWN,
           "RIGHT": Button.RIGHT,
           "LEFT": Button.LEFT,
           "CENTER": Button.CENTER}
