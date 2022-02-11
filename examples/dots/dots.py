from runtime import VirtualMachine
from spike import PrimeHub
from spike.remote import Remote
from util.print_override import spikeprint as print

# create remote
remote = Remote()


async def on_start(vm, stack):
    prime = PrimeHub()
    # connect remote
    await remote.connect()

    # set colors of remote and hub
    prime.status_light.on('cyan')
    remote.color(remote.colors.LIGHTGREEN)

    while True:
        # read pressed buttons
        buttons = remote.pressed()

        # stop vm if remote get disconnected
        if buttons is None: vm.stop(); break

        # change pixel from the hub based on pressed button
        if remote.buttons.LEFT_PLUS in buttons: prime.light_matrix.set_pixel(0, 0, brightness=100)
        if remote.buttons.LEFT_PLUS not in buttons: prime.light_matrix.set_pixel(0, 0, brightness=0)
        if remote.buttons.LEFT in buttons: prime.light_matrix.set_pixel(0, 2, brightness=100)
        if remote.buttons.LEFT not in buttons: prime.light_matrix.set_pixel(0, 2, brightness=0)
        if remote.buttons.LEFT_MINUS in buttons: prime.light_matrix.set_pixel(0, 4, brightness=100)
        if remote.buttons.LEFT_MINUS not in buttons: prime.light_matrix.set_pixel(0, 4, brightness=0)

        if remote.buttons.RIGHT_PLUS in buttons: prime.light_matrix.set_pixel(4, 0, brightness=100)
        if remote.buttons.RIGHT_PLUS not in buttons: prime.light_matrix.set_pixel(4, 0, brightness=0)
        if remote.buttons.RIGHT in buttons: prime.light_matrix.set_pixel(4, 2, brightness=100)
        if remote.buttons.RIGHT not in buttons: prime.light_matrix.set_pixel(4, 2, brightness=0)
        if remote.buttons.RIGHT_MINUS in buttons: prime.light_matrix.set_pixel(4, 4, brightness=100)
        if remote.buttons.RIGHT_MINUS not in buttons: prime.light_matrix.set_pixel(4, 4, brightness=0)
        yield


async def on_cancel(vm, stack):
    remote.cancel()


def setup(rpc, system, stop):
    vm = VirtualMachine(rpc, system, stop, "3f157bda4908")
    vm.register_on_start("f76afdd318a1", on_start)
    vm.register_on_button("accda9ebca74", on_cancel, "center", "pressed")
    return vm
