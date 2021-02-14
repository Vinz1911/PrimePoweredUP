from spike import PrimeHub, LightMatrix, Button, StatusLight, ForceSensor, MotionSensor, Speaker, ColorSensor, App, DistanceSensor, Motor, MotorPair
from spike.control import wait_for_seconds, wait_until, Timer
from remote.control import PowerUPRemote, PowerUPButtons, PowerUPColors

def on_connect():
    hub.status_light.on("azure")


def on_disconnect():
    hub.status_light.on("white")


def on_button(button):
    hub.light_matrix.off()
    if button == PowerUPButtons.A_PLUS:
        hub.light_matrix.set_pixel(0, 0, brightness=100)
    elif button == PowerUPButtons.A_RED:
        hub.light_matrix.set_pixel(1, 0, brightness=100)
    elif button == PowerUPButtons.A_MINUS:
        hub.light_matrix.set_pixel(2, 0, brightness=100)
    elif button == PowerUPButtons.B_PLUS:
        hub.light_matrix.set_pixel(3, 0, brightness=100)
    elif button == PowerUPButtons.B_RED:
        hub.light_matrix.set_pixel(4, 0, brightness=100)
    elif button == PowerUPButtons.B_MINUS:
        hub.light_matrix.set_pixel(0, 1, brightness=100)
    elif button == PowerUPButtons.A_PLUS_B_PLUS:
        hub.light_matrix.set_pixel(0, 2, brightness=100)
    elif button == PowerUPButtons.CENTER:
        remote.disconnect()
    elif button == PowerUPButtons.RELEASED:
        hub.light_matrix.off()
    else:
        hub.light_matrix.off()


# set up hub
hub = PrimeHub()

# create remote and connect
remote = PowerUPRemote()
remote.debug = True
remote.on_connect(callback=on_connect)
remote.on_disconnect(callback=on_disconnect)
remote.on_button(callback=on_button)
remote.connect(color=PowerUPColors.RED)
