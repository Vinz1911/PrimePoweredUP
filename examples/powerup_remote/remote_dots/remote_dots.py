from spike import PrimeHub, LightMatrix, Button, StatusLight, ForceSensor, MotionSensor, Speaker, ColorSensor, App, DistanceSensor, Motor, MotorPair
from spike.control import wait_for_seconds, wait_until, Timer
import utime
import ubluetooth
import ubinascii
import struct
from micropython import const


# LEGO(R) Wireless Protocol 3.0
# [0x00, 0x00, 0x00][0x00, 0x00 ... n]
# 1. Message Length
# 2. HUB ID (Unused, use 0x00)
# 3. Message Type
# 4. Port ID
# 5. - n. Specific Type Codes

# +---------------------------------------------------+
# |                Button Mapping Table               |
# +-----------+---------------------------------------+
# | Button ID | Button Name                           |
# +-----------+---------------------------------------+
# |    0      | Released (no button is pressed)       |
# +-----------+---------------------------------------+
# |    1      | 'Button A Plus'                       |
# +-----------+---------------------------------------+
# |    2      | 'Button A Red'                        |
# +-----------+---------------------------------------+
# |    3      | 'Button A Minus'                      |
# +-----------+---------------------------------------+
# |    4      | 'Button B Plus'                       |
# +-----------+---------------------------------------+
# |    5      | 'Button B Red'                        |
# +-----------+---------------------------------------+
# |    6      | 'Button B Minus'                      |
# +-----------+---------------------------------------+
# |    7      | 'Button A Plus' and 'Button B Plus'   |
# +-----------+---------------------------------------+
# |    8      | 'Button A Minus' and 'Button B Minus' |
# +-----------+---------------------------------------+
# |    9      | 'Button A Plus' and 'Button B Minus'  |
# +-----------+---------------------------------------+
# |    10     | 'Button A Minus' and 'Button B Plus'  |
# +-----------+---------------------------------------+
# |    11     | 'Button Center'                       |
# +-----------+---------------------------------------+

class PowerUPHandler:
    """Class to deal with LEGO(R) PowerUp(TM) over BLE"""

    def __init__(self):
        # constants
        self.__IRQ_SCAN_RESULT = const(1 << 4)
        self.__IRQ_SCAN_COMPLETE = const(1 << 5)
        self.__IRQ_PERIPHERAL_CONNECT = const(1 << 6)
        self.__IRQ_PERIPHERAL_DISCONNECT = const(1 << 7)
        self.__IRQ_GATTC_SERVICE_RESULT = const(1 << 8)
        self.__IRQ_GATTC_CHARACTERISTIC_RESULT = const(1 << 9)
        self.__IRQ_GATTC_READ_RESULT = const(1 << 11)
        self.__IRQ_GATTC_NOTIFY = const(1 << 13)

        self.__LEGO_SERVICE_UUID = ubluetooth.UUID("00001623-1212-EFDE-1623-785FEABCD123")
        self.__LEGO_SERVICE_CHAR = ubluetooth.UUID("00001624-1212-EFDE-1623-785FEABCD123")

        # class specific
        self.__ble = ubluetooth.BLE()
        self.__ble.active(True)
        self.__ble.irq(handler=self.__irq)
        self.__decoder = Decoder()
        self.__reset()

    def __reset(self):
        # cached data
        self.__addr = None
        self.__addr_type = None
        self.__adv_type = None
        self.__services = None
        self.__man_data = None
        self.__name = None
        self.__conn_handle = None
        self.__value_handle = None

        # reserved callbacks
        self.__scan_callback = None
        self.__read_callback = None
        self.__notify_callback = None
        self.__connected_callback = None
        self.__disconnected_callback = None

    # start scan for ble devices
    def scan_start(self, timeout, callback):
        self.__scan_callback = callback
        self.__ble.gap_scan(timeout, 30000, 30000)

    # stop current scan
    def scan_stop(self):
        self.__ble.gap_scan(None)

    # write gatt client data
    def write(self, data, adv_value=None):
        if not self.__is_connected():
            return
        if adv_value:
            self.__ble.gattc_write(self.__conn_handle, adv_value, data)
        else:
            self.__ble.gattc_write(self.__conn_handle, self.__value_handle, data)

    # read gatt client
    def read(self, callback):
        if not self.__is_connected():
            return
        self.__read_callback = callback
        self.__ble.gattc_read(self.__conn_handle, self.__value_handle)

    # connect to ble device
    def connect(self, addr_type, addr):
        self.__ble.gap_connect(addr_type, addr)

    # disconnect from ble device
    def disconnect(self):
        if not self.__is_connected():
            return
        self.__ble.gap_disconnect(self.__conn_handle)
        self.__reset()

    # get notification
    def on_notify(self, callback):
        self.__notify_callback = callback

    # get callback on connect
    def on_connect(self, callback):
        self.__connected_callback = callback

    # get callback on connect
    def on_disconnect(self, callback):
        self.__disconnected_callback = callback

    # +-------------------+
    # | Private Functions |
    # +-------------------+

    # connection status
    def __is_connected(self):
        return self.__conn_handle is not None

    # ble event handler
    def __irq(self, event, data):
        # called for every result of a ble scan
        if event == self.__IRQ_SCAN_RESULT:
            addr_type, addr, adv_type, rssi, adv_data = data
            print(self.__decoder.decode_services(adv_data), addr_type)
            if self.__LEGO_SERVICE_UUID in self.__decoder.decode_services(adv_data):
                self.__addr_type = addr_type
                self.__addr = bytes(addr)
                self.__adv_type = adv_type
                self.__name = self.__decoder.decode_name(adv_data)
                self.__services = self.__decoder.decode_services(adv_data)
                self.__man_data = self.__decoder.decode_manufacturer(adv_data)
                self.scan_stop()

        # called after a ble scan is finished
        elif event == self.__IRQ_SCAN_COMPLETE:
            if self.__addr:
                if self.__scan_callback:
                    self.__scan_callback(self.__addr_type, self.__addr, self.__man_data)
                self.__scan_callback = None
            else:
                self.__scan_callback(None, None, None)

        # called if a peripheral device is connected
        elif event == self.__IRQ_PERIPHERAL_CONNECT:
            conn_handle, addr_type, addr = data
            self.__conn_handle = conn_handle
            self.__ble.gattc_discover_services(self.__conn_handle)

        # called if a peripheral device is disconnected
        elif event == self.__IRQ_PERIPHERAL_DISCONNECT:
            conn_handle, _, _ = data
            self.__disconnected_callback()
            if conn_handle == self.__conn_handle:
                self.__reset()

        # called if a service is returned
        elif event == self.__IRQ_GATTC_SERVICE_RESULT:
            conn_handle, start_handle, end_handle, uuid = data
            if conn_handle == self.__conn_handle and uuid == self.__LEGO_SERVICE_UUID:
                self.__ble.gattc_discover_characteristics(self.__conn_handle, start_handle, end_handle)

        # called if a characteristic is returned
        elif event == self.__IRQ_GATTC_CHARACTERISTIC_RESULT:
            conn_handle, def_handle, value_handle, properties, uuid = data
            if conn_handle == self.__conn_handle and uuid == self.__LEGO_SERVICE_CHAR:
                self.__value_handle = value_handle
                # finished discovering, connecting finished
                self.__connected_callback()

        # called if data was successfully read
        elif event == self.__IRQ_GATTC_READ_RESULT:
            conn_handle, value_handle, char_data = data
            if self.__read_callback:
                self.__read_callback(char_data)

        # called if a notification appears
        elif event == self.__IRQ_GATTC_NOTIFY:
            conn_handle, value_handle, notify_data = data
            if self.__notify_callback:
                self.__notify_callback(notify_data)


class Decoder:
    """Class to decode BLE adv_data"""

    def __init__(self):
        self.__COMPANY_IDENTIFIER_CODES = {"0397": "LEGO System A/S"}

    def decode_manufacturer(self, payload):
        man_data = []
        n = self.__decode_field(payload, const(0xFF))
        if not n:
            return []
        company_identifier = ubinascii.hexlify(struct.pack('<h', *struct.unpack('>h', n[0])))
        company_name = self.__COMPANY_IDENTIFIER_CODES.get(company_identifier.decode(), "?")
        company_data = n[0][2:]
        man_data.append(company_identifier.decode())
        man_data.append(company_name)
        man_data.append(company_data)
        return man_data

    def decode_name(self, payload):
        n = self.__decode_field(payload, const(0x09))
        return str(n[0], "utf-8") if n else "parsing failed!"

    def decode_services(self, payload):
        services = []
        for u in self.__decode_field(payload, const(0x3)):
            services.append(ubluetooth.UUID(struct.unpack("<h", u)[0]))
        for u in self.__decode_field(payload, const(0x5)):
            services.append(ubluetooth.UUID(struct.unpack("<d", u)[0]))
        for u in self.__decode_field(payload, const(0x7)):
            services.append(ubluetooth.UUID(u))
        return services

    def __decode_field(self, payload, adv_type):
        i = 0
        result = []
        while i + 1 < len(payload):
            if payload[i + 1] == adv_type:
                result.append(payload[i + 2: i + payload[i] + 1])
            i += 1 + payload[i]
        return result


class PowerUPRemote:
    """Class to handle Lego(R) PowerUP(TM) Remote"""

    def __init__(self):
        # constants
        self.__POWERED_UP_REMOTE_ID = 66
        self.__COLOR_BLUE = 0x03
        self.__COLOR_LIGHT_BLUE = 0x04
        self.__COLOR_LIGHT_GREEN = 0x05
        self.__COLOR_GREEN = 0x06

        self.BUTTON_A_PLUS = self.__create_message([0x05, 0x00, 0x45, 0x00, 0x01])
        self.BUTTON_A_RED = self.__create_message([0x05, 0x00, 0x45, 0x00, 0x7F])
        self.BUTTON_A_MINUS = self.__create_message([0x05, 0x00, 0x45, 0x00, 0xFF])
        self.BUTTON_A_RELEASED = self.__create_message([0x05, 0x00, 0x45, 0x00, 0x00])

        self.BUTTON_B_PLUS = self.__create_message([0x05, 0x00, 0x45, 0x01, 0x01])
        self.BUTTON_B_RED = self.__create_message([0x05, 0x00, 0x45, 0x01, 0x7F])
        self.BUTTON_B_MINUS = self.__create_message([0x05, 0x00, 0x45, 0x01, 0xFF])
        self.BUTTON_B_RELEASED = self.__create_message([0x05, 0x00, 0x45, 0x01, 0x00])

        self.BUTTON_CENTER_GREEN = self.__create_message([0x05, 0x00, 0x08, 0x02, 0x01])
        self.BUTTON_CENTER_RELEASED = self.__create_message([0x05, 0x00, 0x08, 0x02, 0x00])

        self._BUTTON_A = 0
        self._BUTTON_B = 1
        self._BUTTON_CENTER = 2

        # class specific
        self.__handler = PowerUPHandler()
        self.__buttons = [self.BUTTON_A_RELEASED, self.BUTTON_B_RELEASED, self.BUTTON_CENTER_RELEASED]

        # callbacks
        self.__button_callback = None
        self.__connect_callback = None
        self.__disconnect_callback = None

    def connect(self, timeout=3000):
        self.__handler.on_connect(callback=self.__on_connect)
        self.__handler.on_disconnect(callback=self.__on_disconnect)
        self.__handler.on_notify(callback=self.__on_notify)
        self.__handler.scan_start(timeout, callback=self.__on_scan)

    def disconnect(self):
        self.__handler.disconnect()

    def on_button(self, callback):
        self.__button_callback = callback

    def on_connect(self, callback):
        self.__connect_callback = callback

    def on_disconnect(self, callback):
        self.__disconnect_callback = callback

    # +-------------------+
    # | Private Functions |
    # +-------------------+

    def __create_message(self, byte_array):
        message = struct.pack('%sb' % len(byte_array), *byte_array)
        return message

    def __set_remote_color(self, color_byte):
        color = self.__create_message([0x08, 0x00, 0x81, 0x34, 0x11, 0x51, 0x00, color_byte])
        self.__handler.write(color)

    # callback for scan result
    def __on_scan(self, addr_type, addr, man_data):
        if addr and man_data[2][1] == self.__POWERED_UP_REMOTE_ID:
            self.__handler.connect(addr_type, addr)

    def __on_connect(self):
        # enables remote left port notification
        left_port = self.__create_message([0x0A, 0x00, 0x41, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01])
        # enables remote right port notification
        right_port = self.__create_message([0x0A, 0x00, 0x41, 0x01, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01])
        # enables notifier
        notifier = self.__create_message([0x01, 0x00])

        self.__set_remote_color(self.__COLOR_LIGHT_BLUE)
        utime.sleep(0.5)
        self.__handler.write(left_port)
        utime.sleep(0.5)
        self.__handler.write(right_port)
        utime.sleep(0.5)
        self.__handler.write(notifier, 0x0C)
        if self.__connect_callback:
            self.__connect_callback()

    def __on_disconnect(self):
        if self.__disconnect_callback:
            self.__disconnect_callback()

    def __on_notify(self, data):
        if data == self.BUTTON_A_PLUS:
            self.__buttons[self._BUTTON_A] = self.BUTTON_A_PLUS
        if data == self.BUTTON_A_RED:
            self.__buttons[self._BUTTON_A] = self.BUTTON_A_RED
        if data == self.BUTTON_A_MINUS:
            self.__buttons[self._BUTTON_A] = self.BUTTON_A_MINUS
        if data == self.BUTTON_A_RELEASED:
            self.__buttons[self._BUTTON_A] = self.BUTTON_A_RELEASED
        if data == self.BUTTON_B_PLUS:
            self.__buttons[self._BUTTON_B] = self.BUTTON_B_PLUS
        if data == self.BUTTON_B_RED:
            self.__buttons[self._BUTTON_B] = self.BUTTON_B_RED
        if data == self.BUTTON_B_MINUS:
            self.__buttons[self._BUTTON_B] = self.BUTTON_B_MINUS
        if data == self.BUTTON_B_RELEASED:
            self.__buttons[self._BUTTON_B] = self.BUTTON_B_RELEASED
        if data == self.BUTTON_CENTER_GREEN:
            self.__buttons[self._BUTTON_CENTER] = self.BUTTON_CENTER_GREEN
        if data == self.BUTTON_CENTER_RELEASED:
            self.__buttons[self._BUTTON_CENTER] = self.BUTTON_CENTER_RELEASED

        self.__on_button(self.__buttons)

    def __on_button(self, buttons):
        if buttons[self._BUTTON_A] == self.BUTTON_A_RELEASED and buttons[self._BUTTON_B] == self.BUTTON_B_RELEASED and buttons[self._BUTTON_CENTER] == self.BUTTON_CENTER_RELEASED:
            button = 0
        elif buttons[self._BUTTON_A] == self.BUTTON_A_PLUS and buttons[self._BUTTON_B] == self.BUTTON_B_RELEASED and buttons[self._BUTTON_CENTER] == self.BUTTON_CENTER_RELEASED:
            button = 1
        elif buttons[self._BUTTON_A] == self.BUTTON_A_RED and buttons[self._BUTTON_B] == self.BUTTON_B_RELEASED and buttons[self._BUTTON_CENTER] == self.BUTTON_CENTER_RELEASED:
            button = 2
        elif buttons[self._BUTTON_A] == self.BUTTON_A_MINUS and buttons[self._BUTTON_B] == self.BUTTON_B_RELEASED and buttons[self._BUTTON_CENTER] == self.BUTTON_CENTER_RELEASED:
            button = 3
        elif buttons[self._BUTTON_B] == self.BUTTON_B_PLUS and buttons[self._BUTTON_A] == self.BUTTON_A_RELEASED and buttons[self._BUTTON_CENTER] == self.BUTTON_CENTER_RELEASED:
            button = 4
        elif buttons[self._BUTTON_B] == self.BUTTON_B_RED and buttons[self._BUTTON_A] == self.BUTTON_A_RELEASED and buttons[self._BUTTON_CENTER] == self.BUTTON_CENTER_RELEASED:
            button = 5
        elif buttons[self._BUTTON_B] == self.BUTTON_B_MINUS and buttons[self._BUTTON_A] == self.BUTTON_A_RELEASED and buttons[self._BUTTON_CENTER] == self.BUTTON_CENTER_RELEASED:
            button = 6
        elif buttons[self._BUTTON_A] == self.BUTTON_A_PLUS and buttons[self._BUTTON_B] == self.BUTTON_B_PLUS and buttons[self._BUTTON_CENTER] == self.BUTTON_CENTER_RELEASED:
            button = 7
        elif buttons[self._BUTTON_A] == self.BUTTON_A_MINUS and buttons[self._BUTTON_B] == self.BUTTON_B_MINUS and buttons[self._BUTTON_CENTER] == self.BUTTON_CENTER_RELEASED:
            button = 8
        elif buttons[self._BUTTON_A] == self.BUTTON_A_PLUS and buttons[self._BUTTON_B] == self.BUTTON_B_MINUS and buttons[self._BUTTON_CENTER] == self.BUTTON_CENTER_RELEASED:
            button = 9
        elif buttons[self._BUTTON_A] == self.BUTTON_A_MINUS and buttons[self._BUTTON_B] == self.BUTTON_B_PLUS and buttons[self._BUTTON_CENTER] == self.BUTTON_CENTER_RELEASED:
            button = 10
        elif buttons[self._BUTTON_CENTER] == self.BUTTON_CENTER_GREEN and buttons[self._BUTTON_A] == self.BUTTON_A_RELEASED and buttons[self._BUTTON_B] == self.BUTTON_B_RELEASED:
            button = 11
        else:
            button = 0

        # callback the button data
        if self.__button_callback:
            self.__button_callback(button)


def on_connect():
    hub.status_light.on("azure")


def on_disconnect():
    hub.status_light.on("white")


def on_button(button_id):
    hub.light_matrix.off()
    if button_id == 1:
        hub.light_matrix.set_pixel(0, 0, brightness=100)
    elif button_id == 2:
        hub.light_matrix.set_pixel(1, 0, brightness=100)
    elif button_id == 3:
        hub.light_matrix.set_pixel(2, 0, brightness=100)
    elif button_id == 4:
        hub.light_matrix.set_pixel(3, 0, brightness=100)
    elif button_id == 5:
        hub.light_matrix.set_pixel(4, 0, brightness=100)
    elif button_id == 6:
        hub.light_matrix.set_pixel(0, 1, brightness=100)
    elif button_id == 7:
        hub.light_matrix.set_pixel(0, 2, brightness=100)
    elif button_id == 0:
        hub.light_matrix.off()
    else:
        hub.light_matrix.off()


# set up hub
hub = PrimeHub()

# create remote and connect
remote = PowerUPRemote()
remote.on_connect(callback=on_connect)
remote.on_disconnect(callback=on_disconnect)
remote.on_button(callback=on_button)
remote.connect()