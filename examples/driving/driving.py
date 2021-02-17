from spike import PrimeHub, LightMatrix, Button, StatusLight, ForceSensor, MotionSensor, Speaker, ColorSensor, App, DistanceSensor, Motor, MotorPair
from spike.control import wait_for_seconds, wait_until, Timer
from remote.control import PoweredUPRemote, PoweredUPColors, PoweredUPButtons

"""
LEGO(R) SPIKE PRIME + POWERED UP
--------------------------------

This is a basic example:
This example let control a motor pair
with the powered up remote
"""


def on_connect():
    """
    callback on connect
    """
    hub.status_light.on("azure")


def on_disconnect():
    """
    callback on disconnect
    """
    hub.status_light.on("white")
    motor_pair.stop()


def on_button(button):
    """
    callback on button press

    :param button: button id
    """
    if button == PoweredUPButtons.B_PLUS:
        motor_pair.start(speed=75)
    elif button == PoweredUPButtons.B_MINUS:
        motor_pair.start(speed=-75)
    elif button == PoweredUPButtons.A_PLUS_B_PLUS:
        motor_pair.start(steering=-45, speed=75)
    elif button == PoweredUPButtons.A_MINUS_B_PLUS:
        motor_pair.start(steering=45, speed=75)
    elif button == PoweredUPButtons.A_MINUS_B_MINUS:
        motor_pair.start(steering=45, speed=-75)
    elif button == PoweredUPButtons.A_PLUS_B_MINUS:
        motor_pair.start(steering=-45, speed=-75)
    elif button == PoweredUPButtons.RELEASED:
        motor_pair.stop()
    else:
        motor_pair.stop()


# set up hub
hub = PrimeHub()

# set up motors
motor_pair = MotorPair('A', 'E')
motor_pair.set_stop_action('coast')

# create remote and connect
remote = PoweredUPRemote()
remote.on_connect(callback=on_connect)
remote.on_disconnect(callback=on_disconnect)
remote.on_button(callback=on_button)
remote.connect()
