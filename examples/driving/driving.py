from runtime import VirtualMachine
from spike import PrimeHub, MotorPair
from spike.remote import Remote
import hub
from util.print_override import spikeprint as print

# create remote
remote = Remote()

animation = [
    "03450:00060:09870:00000:00000",
    "00340:09050:08760:00000:00000",
    "09030:08040:07650:00000:00000",
    "08900:07030:06540:00000:00000",
    "07890:06000:05430:00000:00000",
    "06780:05090:04300:00000:00000",
    "05670:04080:03090:00000:00000",
    "04560:03070:00980:00000:00000"
]

async def on_start(vm, stack):
    frames = [hub.Image(frame) for frame in animation]
    vm.system.display.show(frames, clear=False, delay=round(1000 / 12), loop=True, fade=1)

    prime = PrimeHub()
    pair = MotorPair('A', 'B')
    pair.set_stop_action('coast')

    print("connecting...")
    await remote.connect()
    print("connected")
    prime.status_light.on('blue')

    while True:
        buttons = remote.pressed()
        if buttons == (remote.button.RIGHT_PLUS,): pair.start(speed=65)
        elif buttons == (remote.button.RIGHT_MINUS,): pair.start(speed=-65)
        elif buttons == (remote.button.LEFT_MINUS, remote.button.RIGHT_PLUS): pair.start(speed=65, steering=-45)
        elif buttons == (remote.button.LEFT_PLUS, remote.button.RIGHT_PLUS): pair.start(speed=65, steering=45)
        elif buttons == (remote.button.LEFT_MINUS, remote.button.RIGHT_MINUS): pair.start(speed=-65, steering=-45)
        elif buttons == (remote.button.LEFT_PLUS, remote.button.RIGHT_MINUS): pair.start(speed=-65, steering=45)
        else: pair.stop()
        yield


async def on_cancel(vm, stack):
    remote.cancel()


def setup(rpc, system, stop):
    vm = VirtualMachine(rpc, system, stop, "3f157bda4908")
    vm.register_on_start("f76afdd318a1", on_start)
    vm.register_on_button("accda9ebca74", on_cancel, "center", "pressed")
    return vm