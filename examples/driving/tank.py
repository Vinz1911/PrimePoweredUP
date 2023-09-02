from runtime import VirtualMachine
from spike import PrimeHub, Motor
from spike.remote import Remote
import hub

# create remote
remote = Remote()

# Speed & steer settings
SPEED = 75
STEER = 45

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
    left_motor, right_motor = Motor('A'), Motor('B')
    left_motor.set_stop_action('coast')
    right_motor.set_stop_action('coast')

    # connect remote
    await remote.connect()

    # Set colors of remote and hub
    print(remote.address())
    prime.status_light.on('cyan')
    remote.color(remote.colors.LIGHTGREEN)

    while True:
        # Read pressed buttons from remote
        buttons = remote.pressed()

        # Stop vm if remote get disconnected
        if buttons is None: vm.stop(); break

        # Move robot based on pressed buttons
        if remote.buttons.RIGHT_PLUS in buttons: left_motor.start(speed=-SPEED)
        elif remote.buttons.RIGHT_MINUS in buttons: left_motor.start(speed=SPEED)
        else: left_motor.stop()

        if remote.buttons.LEFT_PLUS in buttons: right_motor.start(speed=SPEED)
        elif remote.buttons.LEFT_MINUS in buttons: right_motor.start(speed=-SPEED)
        else: right_motor.stop()
        yield


async def on_cancel(vm, stack):
    remote.cancel()


def setup(rpc, system, stop):
    vm = VirtualMachine(rpc, system, stop, "3f157bda4908")
    vm.register_on_start("f76afdd318a1", on_start)
    vm.register_on_button("accda9ebca74", on_cancel, "center", "pressed")
    return vm
