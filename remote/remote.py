from micropython import const
import ubluetooth
import ubinascii
import struct


class Remote:
    def __init__(self):
        self.buttons = _RemoteButtons()
        self.colors = _RemoteColors()
        self.__ble = ubluetooth.BLE()
        self.__ble.active(True)
        self.__ble.irq(self.__irq)
        self.__ble_const = _RemoteConstant()

        self.__address = bytes()
        self.__pressed = tuple()
        self.__state = [''] * 7

    async def connect(self, address=None, timeout=5000):
        if address: self.__address = ubinascii.unhexlify(address.replace(':', str()))
        self.__ble_const = _RemoteConstant()
        self.__ble.gap_scan(timeout, 30000, 30000)
        while not self.__ble_const.enabled: yield

    def cancel(self):
        self.__ble.gap_scan(None)
        if self.__ble_const.conn_handle: self.__ble.gap_disconnect(self.__ble_const.conn_handle)

    def pressed(self) -> tuple:
        return self.__pressed

    def address(self) -> str:
        if not self.__address: return str()
        return ubinascii.hexlify(self.__address, ':').decode('UTF-8')

    def color(self, color: int):
        message = _Decoder.bytes([0x08, 0x00, 0x81, 0x34, 0x11, 0x51, 0x00, color])
        self.__write_bytes(message)

    def __write_bytes(self, data, adv_value=None, callback=None):
        try:
            if self.__ble_const.conn_handle is None: return
            if adv_value: self.__ble.gattc_write(self.__ble_const.conn_handle, adv_value, data, True)
            else: self.__ble.gattc_write(self.__ble_const.conn_handle, self.__ble_const.value_handle, data, True)
            self.__write_callback = callback
        except: pass

    def __enable(self):
        message = _Decoder.bytes([0x08, 0x00, 0x81, 0x34, 0x11, 0x51, 0x00, 0x3])
        self.__write_bytes(message, callback=lambda: enable())
        def enable(): self.__ble_const.enabled = True

    def __irq(self, event, data):
        if event == _RemoteConstant.IRQ_SCAN_RESULT: self.__scan_result(data)
        elif event == _RemoteConstant.IRQ_SCAN_DONE: self.__scan_complete(data)
        elif event == _RemoteConstant.IRQ_PERIPHERAL_CONNECT: self.__peripheral_connect(data)
        elif event == _RemoteConstant.IRQ_PERIPHERAL_DISCONNECT: self.__peripheral_disconnect(data)
        elif event == _RemoteConstant.IRQ_GATTC_SERVICE_RESULT: self.__gattc_service_result(data)
        elif event == _RemoteConstant.IRQ_GATTC_CHARACTERISTIC_RESULT: self.__gattc_characteristic_result(data)
        elif event == _RemoteConstant.IRQ_GATTC_WRITE_DONE: self.__gattc_write_done(data)
        elif event == _RemoteConstant.IRQ_GATTC_NOTIFY: self.__gattc_notify(data)

    def __scan_result(self, data):
        addr_type, addr, _, _, adv_data = data
        if _RemoteConstant.SERVICE_UUID in _Decoder.decode_services(adv_data):
            self.__ble_const.addr_type = addr_type
            self.__ble_const.addr = bytes(addr)
            self.__ble_const.man_data = _Decoder.company_data(adv_data)
            self.__ble.gap_scan(None)

    def __scan_complete(self, data):
        if not self.__ble_const.addr: return
        if not self.__address: self.__address = self.__ble_const.addr
        if self.__address == self.__ble_const.addr and self.__ble_const.man_data[1] == 66: self.__ble.gap_connect(self.__ble_const.addr_type, self.__ble_const.addr)

    def __peripheral_connect(self, data):
        conn_handle, _, _ = data
        self.__ble_const.conn_handle = conn_handle
        self.__ble.gattc_discover_services(self.__ble_const.conn_handle)

    def __peripheral_disconnect(self, data):
        self.__ble_const.conn_handle = None
        self.__pressed = None

    def __gattc_service_result(self, data):
        conn_handle, start_handle, end_handle, uuid = data
        if conn_handle == self.__ble_const.conn_handle and uuid == _RemoteConstant.SERVICE_UUID: self.__ble.gattc_discover_characteristics(self.__ble_const.conn_handle, start_handle, end_handle)

    def __gattc_characteristic_result(self, data):
        conn_handle, _, value_handle, _, uuid = data
        if conn_handle == self.__ble_const.conn_handle and uuid == _RemoteConstant.SERVICE_CHAR:
            self.__ble_const.value_handle = value_handle
            left_port = _Decoder.bytes([0x0A, 0x00, 0x41, 0x00, 0x04, 0x01, 0x00, 0x00, 0x00, 0x01])
            right_port = _Decoder.bytes([0x0A, 0x00, 0x41, 0x01, 0x04, 0x01, 0x00, 0x00, 0x00, 0x01])
            notifier = _Decoder.bytes([0x01, 0x00])

            self.__write_bytes(left_port, callback=lambda:
            self.__write_bytes(right_port, callback=lambda:
            self.__write_bytes(notifier, 0x0C, callback=lambda:
            self.__enable())))

    def __gattc_write_done(self, data):
        if self.__write_callback: self.__write_callback()

    def __gattc_notify(self, data):
        _, _, notify_data = data
        if notify_data[0] == 0x5 and notify_data[2] == 0x8 and notify_data[3] == 0x2:
            self.__state[6] = _RemoteConstant.Center_Button[notify_data[4]]
        if notify_data[0] == 0x7 and notify_data[2] == 0x45:
            if notify_data[3] == 0x0:
                self.__state[0] = _RemoteConstant.Left_Button[0][notify_data[4]]
                self.__state[1] = _RemoteConstant.Left_Button[1][notify_data[5]]
                self.__state[2] = _RemoteConstant.Left_Button[2][notify_data[6]]
            if notify_data[3] == 0x1:
                self.__state[3] = _RemoteConstant.Right_Button[0][notify_data[4]]
                self.__state[4] = _RemoteConstant.Right_Button[1][notify_data[5]]
                self.__state[5] = _RemoteConstant.Right_Button[2][notify_data[6]]
        self.__pressed = tuple([i for i in self.__state if i != str()])


class _RemoteButtons:
    LEFT_PLUS = 'LEFT_PLUS'
    LEFT = 'LEFT'
    LEFT_MINUS = 'LEFT_MINUS'
    RIGHT_PLUS = 'RIGHT_PLUS'
    RIGHT = 'RIGHT'
    RIGHT_MINUS = 'RIGHT_MINUS'
    CENTER = 'CENTER'


class _RemoteColors:
    OFF = const(0x00)
    PINK = const(0x01)
    PURPLE = const(0x02)
    BLUE = const(0x03)
    LIGHTBLUE = const(0x04)
    LIGHTGREEN = const(0x05)
    GREEN = const(0x06)
    YELLOW = const(0x07)
    ORANGE = const(0x08)
    RED = const(0x09)
    WHITE = const(0x0A)


class _RemoteConstant:
    SERVICE_UUID = ubluetooth.UUID('00001623-1212-EFDE-1623-785FEABCD123')
    SERVICE_CHAR = ubluetooth.UUID('00001624-1212-EFDE-1623-785FEABCD123')

    IRQ_SCAN_RESULT = const(5)
    IRQ_SCAN_DONE = const(6)
    IRQ_PERIPHERAL_CONNECT = const(7)
    IRQ_PERIPHERAL_DISCONNECT = const(8)
    IRQ_GATTC_SERVICE_RESULT = const(9)
    IRQ_GATTC_SERVICE_DONE = const(10)
    IRQ_GATTC_CHARACTERISTIC_RESULT = const(11)
    IRQ_GATTC_CHARACTERISTIC_DONE = const(12)
    IRQ_GATTC_WRITE_DONE = const(17)
    IRQ_GATTC_NOTIFY = const(18)

    Left_Button = [{0x0: str(), 0x1: 'LEFT_PLUS'}, {0x0: str(), 0x1: 'LEFT'}, {0x0: str(), 0x1: 'LEFT_MINUS'}]
    Right_Button = [{0x0: str(), 0x1: 'RIGHT_PLUS'}, {0x0: str(), 0x1: 'RIGHT'}, {0x0: str(), 0x1: 'RIGHT_MINUS'}]
    Center_Button = {0x0: str(), 0x1: 'CENTER'}

    def __init__(self):
        self.addr = None
        self.addr_type = None
        self.man_data = None
        self.conn_handle = None
        self.value_handle = None
        self.enabled = False


class _Decoder:
    @classmethod
    def bytes(cls, byte_array):
        return struct.pack('%sb' % len(byte_array), *byte_array)

    @classmethod
    def company_data(cls, payload):
        decode = cls.__decode_field(payload, const(0xFF))
        if not decode: return []
        return decode[0][2:]

    @classmethod
    def decode_services(cls, payload):
        services = []
        for char in cls.__decode_field(payload, const(0x3)): services.append(ubluetooth.UUID(struct.unpack('<h', char)[0]))
        for char in cls.__decode_field(payload, const(0x5)): services.append(ubluetooth.UUID(struct.unpack('<d', char)[0]))
        for char in cls.__decode_field(payload, const(0x7)): services.append(ubluetooth.UUID(char))
        return services

    @classmethod
    def __decode_field(cls, payload, adv_type):
        i = 0; result = []
        while i + 1 < len(payload):
            if payload[i + 1] == adv_type: result.append(payload[i + 2: i + payload[i] + 1])
            i += 1 + payload[i]
        return result
