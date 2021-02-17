# PrimePowerUP

`PrimePoweredUP` contains a library for Lego Spike Prime to connect to PoweredUP Remote (Handset) over BLE.
The core is based on the MicroPython ubluetooth low level api.

### Description
- the library use lot of memory. i recommend to pre compile the library from `remote/control` and install it on the prime hub.
a very good way to do that is using this awesome tool: [Spike Tools](https://github.com/XenseEducation/spiketools-release/releases)

- there are two examples in `examples` folder. The first one shows how to light up dot's on Prime Hub and the second one 
shows how to control a motor pair with the remote. examples are created by using the control.py installed as pre compiled lib
(it's also possible to copy all together and load it on the hub)

### Known Problems:
- the ubluetooth class has some problems with event loop based functions from Lego. This means, if you run a event loop based
function within the button pressed callback, the entire hub will freeze. This is currently not possible to fix that, maybe with 
a new firmare which supports uasyncio library. **Event based functions ?!** are functions like playing sound until end, wait for or 
motor functions like run_to_position or run_for_degrees and so on.