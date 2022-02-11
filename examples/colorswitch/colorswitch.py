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

        # change remote color based on pressed button
        if remote.buttons.LEFT_PLUS in buttons: remote.color(remote.colors.PINK)
        if remote.buttons.LEFT in buttons: remote.color(remote.colors.PURPLE)
        if remote.buttons.LEFT_MINUS in buttons: remote.color(remote.colors.BLUE)

        if remote.buttons.RIGHT_PLUS in buttons: remote.color(remote.colors.GREEN)
        if remote.buttons.RIGHT in buttons: remote.color(remote.colors.YELLOW)
        if remote.buttons.RIGHT_MINUS in buttons: remote.color(remote.colors.ORANGE)

        if remote.buttons.CENTER in buttons: remote.color(remote.colors.OFF)
        yield


async def on_cancel(vm, stack):
    remote.cancel()


def setup(rpc, system, stop):
    vm = VirtualMachine(rpc, system, stop, "3f157bda4908")
    vm.register_on_start("f76afdd318a1", on_start)
    vm.register_on_button("accda9ebca74", on_cancel, "center", "pressed")
    return vm
