#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick  # type:ignore
from pybricks.ev3devices import (  # type:ignore
    Motor, TouchSensor, ColorSensor, InfraredSensor, UltrasonicSensor, GyroSensor)  # type:ignore
from pybricks.parameters import Port, Stop, Direction, Button, Color  # type:ignore
from pybricks.tools import wait, StopWatch, DataLog  # type:ignore
from pybricks.robotics import DriveBase  # type:ignore
from pybricks.media.ev3dev import SoundFile, ImageFile  # type:ignore
from communications import start


# This program requires LEGO EV3 MicroPython v2.0 or higher.
# Click "Open user guide" on the EV3 extension tab for more information.

# Create your objects here.
ev3 = EV3Brick()
# Motor A - tube
# Motor D - trapdoor
MOTORS = {"A": Motor(Port.A),
          "B": Motor(Port.B),
          "C": None,
          "D": Motor(Port.D)}

SENSORS = {"1": TouchSensor(Port.S1),
           "2": None,
           "3": None,
           "4": None}

BRICK_BUTTONS = ev3.buttons

# Write your program here.
start(MOTORS, SENSORS, BRICK_BUTTONS)
