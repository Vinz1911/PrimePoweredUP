# PrimePoweredUP

`PrimePoweredUP` contains a library for Lego Spike Prime / Robot Inventor to connect to the Lego PoweredUP Remote (Handset) over BLE.
The core is based on the MicroPython ubluetooth low level api.

### Compatibility
- Works with the latest version of `Spike Prime` and `Mindstorms Robot Inventor`.

### Description
- the library is build for the use inside the `Lego Python VM`. This means you need the advanced Python setup for the Spike Prime / Robot Inventor.
- for an easy start with the advanced Python setup, it's recommended to use VSCode with this plugin: [Spike Prime/RI Extension](https://marketplace.visualstudio.com/items?itemName=PeterStaev.lego-spikeprime-mindstorms-vscode).
- **WARNING:** the library does **not** work with the normal python setup due to `async/await` of the connection process.
- examples can be found in `./examples` directory.

### Usage
- The pre-compiled library is inside the `./remote` directory, it's recommended to copy the library inside the `./spike` directory
of the Spike Prime / Robot Inventor. You can do this by using a script or with [rshell](https://github.com/dhylands/rshell).

```bash
# example using rshell
Connecting to /dev/cu.usbmodem3382397933381 (buffer-size 512)...
Trying to connect to REPL  connected
Retrieving sysname ... LEGO Technic Large Hub
...
Welcome to rshell. Use Control-D (or the exit command) to exit rshell.

# copy file to hub
/remote> cp ./remote.mpy /pyboard/spike/
```
#### Example
```python
from runtime import VirtualMachine
from spike.remote import Remote, Buttons
from util.print_override import spikeprint as print

# create remote
remote = Remote()


async def on_start(vm, stack):
    print("connecting...")
    await remote.connect() # wait for connection establishment
    print("connected")
    
    while True:
        buttons = remote.pressed() # read pressed buttons
        print(buttons) # Output is a tuple for example: (LEFT_PLUS, RIGHT_PLUS, CENTER)
        yield


async def on_cancel(vm, stack):
    remote.cancel() # disconnect if the program exit's 


def setup(rpc, system, stop):
    vm = VirtualMachine(rpc, system, stop, "3f157bda4908")
    vm.register_on_start("f76afdd318a1", on_start)
    vm.register_on_button("accda9ebca74", on_cancel, "center", "pressed")
    return vm
```

### Known Issues:
- The library uses an async connection process, this is why we need the python vm for the usage. performance is also better.
- The library uses internally ble notification service, sometimes the hub needs a restart to make this work (if tuple is empty on button press).
- I didn't found a good way to disconnect the remote if you reach the end of a program (there is currently no way to run `cleanup` code on program's end). fallback solution is to use the `Start/Stop` button.
So just for clarification: **remote needs to be reconnected on program start**. if your program is exited and the remote is still connected
you need to unpair the remote by holding the green button until it's unpaired.