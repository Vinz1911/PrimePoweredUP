from spike import PrimeHub, LightMatrix, Button, StatusLight, ForceSensor, MotionSensor, Speaker, ColorSensor, App, DistanceSensor, Motor, MotorPair
from spike.control import wait_for_seconds, wait_until, Timer
from remote.control import PoweredUPRemote, PoweredUPColors, PoweredUPButtons

"""
LEGO(R) SPIKE PRIME + POWERED UP
--------------------------------

This is a basic example:
This example let light up different dot's on
a prime/inventor hub for different buttons pressed
on the powered up remote
"""


def on_connect():
    """
    callback on connect
    """
    hub.status_light.on("blue")


def on_disconnect():
    """
    callback on disconnect
    """
    hub.status_light.on("white")


def on_button(button):
    """
    callback on button press
    :param button: button id
    """
    hub.light_matrix.off()
    if button == PoweredUPButtons.LEFT_PLUS:
        hub.light_matrix.set_pixel(0, 0, brightness=100)
    elif button == PoweredUPButtons.LEFT_RED:
        hub.light_matrix.set_pixel(1, 0, brightness=100)
    elif button == PoweredUPButtons.LEFT_MINUS:
        hub.light_matrix.set_pixel(2, 0, brightness=100)
    elif button == PoweredUPButtons.RIGHT_PLUS:
        hub.light_matrix.set_pixel(3, 0, brightness=100)
    elif button == PoweredUPButtons.RIGHT_RED:
        hub.light_matrix.set_pixel(4, 0, brightness=100)
    elif button == PoweredUPButtons.RIGHT_MINUS:
        hub.light_matrix.set_pixel(0, 1, brightness=100)
    elif button == PoweredUPButtons.LEFT_PLUS_RIGHT_PLUS:
        hub.light_matrix.set_pixel(0, 2, brightness=100)
    elif button == PoweredUPButtons.RELEASED:
        hub.light_matrix.off()
    else:
        hub.light_matrix.off()


# set up hub
hub = PrimeHub()

# create remote and connect
remote = PoweredUPRemote()
remote.debug = True
remote.on_connect(callback=on_connect)
remote.on_disconnect(callback=on_disconnect)
remote.on_button(callback=on_button)
remote.connect()