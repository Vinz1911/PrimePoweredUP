def on_connect():
    hub.status_light.on("azure")
    remote.set_color(PowerUPColors.LIGHTBLUE)


def on_disconnect():
    hub.status_light.on("white")


def on_button(button):
    hub.light_matrix.off()
    if button == PowerUPButtons.LEFT_PLUS:
        hub.light_matrix.set_pixel(0, 0, brightness=100)
    elif button == PowerUPButtons.LEFT_RED:
        hub.light_matrix.set_pixel(1, 0, brightness=100)
    elif button == PowerUPButtons.LEFT_MINUS:
        hub.light_matrix.set_pixel(2, 0, brightness=100)
    elif button == PowerUPButtons.RIGHT_PLUS:
        hub.light_matrix.set_pixel(3, 0, brightness=100)
    elif button == PowerUPButtons.RIGHT_RED:
        hub.light_matrix.set_pixel(4, 0, brightness=100)
    elif button == PowerUPButtons.RIGHT_MINUS:
        hub.light_matrix.set_pixel(0, 1, brightness=100)
    elif button == PowerUPButtons.LEFT_PLUS_RIGHT_PLUS:
        hub.light_matrix.set_pixel(0, 2, brightness=100)
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
remote.connect()

# address="58:93:D8:DD:6F:B3"