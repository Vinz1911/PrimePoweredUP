from runtime import VirtualMachine
from spike import PrimeHub, MotorPair
from spike.remote import Remote, Buttons
from util.print_override import spikeprint as print

# create remote
remote = Remote()


async def on_start(vm, stack):
    hub = PrimeHub()
    pair = MotorPair('A', 'B')
    pair.set_stop_action('coast')

    print("connecting...")
    await remote.connect()
    print("connected")
    hub.status_light.on('blue')

    while True:
        buttons = remote.pressed()
        if buttons == (Buttons.RIGHT_PLUS,): pair.start(speed=65)
        elif buttons == (Buttons.RIGHT_MINUS,): pair.start(speed=-65)
        elif buttons == (Buttons.LEFT_MINUS, Buttons.RIGHT_PLUS): pair.start(speed=65, steering=-45)
        elif buttons == (Buttons.LEFT_PLUS, Buttons.RIGHT_PLUS): pair.start(speed=65, steering=45)
        elif buttons == (Buttons.LEFT_MINUS, Buttons.RIGHT_MINUS): pair.start(speed=-65, steering=-45)
        elif buttons == (Buttons.LEFT_PLUS, Buttons.RIGHT_MINUS): pair.start(speed=-65, steering=45)
        else: pair.stop()
        yield


async def on_cancel(vm, stack):
    remote.cancel()


def setup(rpc, system, stop):
    vm = VirtualMachine(rpc, system, stop, "3f157bda4908")
    vm.register_on_start("f76afdd318a1", on_start)
    vm.register_on_button("accda9ebca74", on_cancel, "center", "pressed")
    return vm