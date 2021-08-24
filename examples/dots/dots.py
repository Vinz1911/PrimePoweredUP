from runtime import VirtualMachine
from spike import PrimeHub
from spike.remote import Remote
from util.print_override import spikeprint as print

# create remote
remote = Remote()


async def on_start(vm, stack):
    hub = PrimeHub()
    print("connecting...")
    await remote.connect()
    print("connected")
    hub.status_light.on('blue')

    print(remote.button)

    while True:
        buttons = remote.pressed()
        if remote.button.LEFT_PLUS in buttons: hub.light_matrix.set_pixel(0, 0, brightness=100)
        if remote.button.LEFT_PLUS not in buttons: hub.light_matrix.set_pixel(0, 0, brightness=0)
        if remote.button.LEFT in buttons: hub.light_matrix.set_pixel(0, 2, brightness=100)
        if remote.button.LEFT not in buttons: hub.light_matrix.set_pixel(0, 2, brightness=0)
        if remote.button.LEFT_MINUS in buttons: hub.light_matrix.set_pixel(0, 4, brightness=100)
        if remote.button.LEFT_MINUS not in buttons: hub.light_matrix.set_pixel(0, 4, brightness=0)

        if remote.button.RIGHT_PLUS in buttons: hub.light_matrix.set_pixel(4, 0, brightness=100)
        if remote.button.RIGHT_PLUS not in buttons: hub.light_matrix.set_pixel(4, 0, brightness=0)
        if remote.button.RIGHT in buttons: hub.light_matrix.set_pixel(4, 2, brightness=100)
        if remote.button.RIGHT not in buttons: hub.light_matrix.set_pixel(4, 2, brightness=0)
        if remote.button.RIGHT_MINUS in buttons: hub.light_matrix.set_pixel(4, 4, brightness=100)
        if remote.button.RIGHT_MINUS not in buttons: hub.light_matrix.set_pixel(4, 4, brightness=0)
        yield


async def on_cancel(vm, stack):
    remote.cancel()


def setup(rpc, system, stop):
    vm = VirtualMachine(rpc, system, stop, "3f157bda4908")
    vm.register_on_start("f76afdd318a1", on_start)
    vm.register_on_button("accda9ebca74", on_cancel, "center", "pressed")
    return vm
