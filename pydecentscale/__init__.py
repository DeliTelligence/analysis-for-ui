# https://github.com/lucapinello/pydecentscale
# Open source library for interacting with decent scale
# Date cloned 07/11/2024
# Clone the Resource to use it
import asyncio
import binascii
import functools
import logging
import operator
import threading
from itertools import cycle
from bleak import BleakScanner, BleakClient

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class AsyncioEventLoopThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loop = asyncio.new_event_loop()
        self.running = False

    def run(self):
        self.running = True
        self.loop.run_forever()

    def run_coro(self, coro, wait_for_result=True):
        if wait_for_result:
            return asyncio.run_coroutine_threadsafe(coro, self.loop).result()
        else:
            return asyncio.run_coroutine_threadsafe(coro, self.loop)

    def stop(self):
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.join()
        self.running = False


class DecentScale(AsyncioEventLoopThread):
    def __init__(self, timeout=20, fix_dropped_command=True):
        super().__init__()
        self.client = None
        self.timeout = timeout
        self.connected = False
        self.fix_dropped_command = fix_dropped_command
        self.dropped_command_sleep = 0.05  # API Docs says 50ms
        self._weight = None
        self.weight_lock = threading.Lock()

        self.CHAR_READ = '0000FFF4-0000-1000-8000-00805F9B34FB'
        self.CHAR_WRITE = '000036f5-0000-1000-8000-00805f9b34fb'

        tare_commands = [bytearray.fromhex(c) for c in ['030F000000000C', '030F010000000D', '030F020000000E']]
        self.tare_commands = cycle(tare_commands)
        self.led_on_command = bytearray.fromhex('030A0101000009')
        self.led_off_command = bytearray.fromhex('030A0000000009')
        self.start_time_command = bytearray.fromhex('030B030000000B')
        self.stop_time_command = bytearray.fromhex("030B0000000008")
        self.reset_time_command = bytearray.fromhex("030B020000000A")
        self.daemon = True
        super().start()

    @property
    def weight(self):
        with self.weight_lock:
            return self._weight

    @weight.setter
    def weight(self, value):
        with self.weight_lock:
            self._weight = value

    def check_connection(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.connected:
                return func(self, *args, **kwargs)
            else:
                logger.warning("Scale is not connected.")
                return None

        return wrapper

    async def _find_address(self):
        device = await BleakScanner.find_device_by_filter(
            lambda d, ad: d.name and d.name == 'Decent Scale', timeout=self.timeout
        )
        if device:
            return device.address
        else:
            logger.error('Error: Scale not found. Trying again...')
            return None

    async def _connect(self, address):
        self.client = BleakClient(address)
        if not self.running:
            super().start()
        try:
            connected = await self.client.connect(timeout=self.timeout)
            if connected:
                self.connected = True
                logger.info(f"Connected to scale: {address}")
                return True
        except Exception as e:
            logger.error(f"Error: {e}\nTrying again...")
        self.connected = False
        return False

    async def _disconnect(self):
        try:
            await self.client.disconnect()
            self.connected = False
            logger.info("Disconnected from the scale")
        except Exception as e:
            logger.error(f"Error: {e}\nTrying again...")

    async def __send(self, cmd):
        await self.client.write_gatt_char(self.CHAR_WRITE, cmd)
        if self.fix_dropped_command:
            await asyncio.sleep(self.dropped_command_sleep)
            await self.client.write_gatt_char(self.CHAR_WRITE, cmd)
        await asyncio.sleep(0.2)

    async def _tare(self):
        await self.__send(next(self.tare_commands))

    async def _led_on(self):
        await self.__send(self.led_on_command)

    async def _led_off(self):
        await self.__send(self.led_off_command)

    async def _start_time(self):
        await self.__send(self.start_time_command)

    async def _stop_time(self):
        await self.__send(self.stop_time_command)

    async def _reset_time(self):
        await self.__send(self.reset_time_command)

    def notification_handler(self, sender, data):
        logger.debug(f"Received Notification: {binascii.hexlify(data)}")

        if data[0] != 0x03:
            logger.info("Invalid model byte in notification")
            return

        type_ = data[1]
        if type_ not in [0xCA, 0xCE]:
            logger.warning(f"Unknown type in notification: {type_:02x}")
            return

        if len(data) == 7:
            weight_raw = data[2:4]
        elif len(data) == 10:
            weight_raw = data[2:4]
        else:
            logger.info("Invalid notification length")
            return

        # Parse weight and adjust to grams
        weight = int.from_bytes(weight_raw, byteorder='big', signed=True) / 10
        logger.debug(f"Parsed weight: {weight} g from raw bytes: {binascii.hexlify(weight_raw)}")

        xor_msg = functools.reduce(operator.xor, data[:-1])
        if xor_msg != data[-1]:
            logger.warning("XOR verification failed for notification")
            return

        self.weight = weight
        logger.debug(f"Weight updated: {self.weight} g")

    async def _enable_notification(self):
        await self.client.start_notify(self.CHAR_READ, self.notification_handler)
        await asyncio.sleep(1)
        logger.info("Notifications enabled")

    async def _disable_notification(self):
        await self.client.stop_notify(self.CHAR_READ)
        self.weight = None
        logger.info("Notifications disabled")

    @check_connection
    def enable_notification(self):
        return self.run_coro(self._enable_notification())

    @check_connection
    def disable_notification(self):
        return self.run_coro(self._disable_notification())

    def find_address(self):
        return self.run_coro(self._find_address())

    def connect(self, address):
        if not self.connected:
            self.connected = self.run_coro(self._connect(address))
            if self.connected:
                self.led_off()
                self.led_on()
        else:
            logger.info("Already connected.")
        return self.connected

    def disconnect(self):
        if self.connected:
            self.connected = not self.run_coro(self._disconnect())
        else:
            logger.info("Already disconnected.")
        return not self.connected

    def auto_connect(self, n_retries=3):
        address = None
        for i in range(n_retries):
            address = self.find_address()
            if address:
                logger.info(f"Found Decent Scale: {address}")
                break
            else:
                logger.info(i)
        if address:
            for i in range(n_retries):
                if self.connect(address):
                    logger.info("Scale connected!")
                    return True
        logger.error("Autoconnect failed. Make sure the scale is on.")
        return False

    @check_connection
    def tare(self):
        return self.run_coro(self._tare())

    @check_connection
    def start_time(self):
        return self.run_coro(self._start_time())

    @check_connection
    def stop_time(self):
        return self.run_coro(self._stop_time())

    @check_connection
    def reset_time(self):
        return self.run_coro(self._reset_time())

    @check_connection
    def led_off(self):
        return self.run_coro(self._led_off())

    @check_connection
    def led_on(self):
        return self.run_coro(self._led_on())