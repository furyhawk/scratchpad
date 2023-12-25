import sys

sys.path.append("")

from micropython import const

import uasyncio as asyncio
import aioble
import bluetooth

import random
import struct


from machine import Pin, I2C, freq

from ssd1306 import SSD1306_I2C

WIDTH = const(128)  # oled display width
HEIGHT = const(64)  # oled display height


i2c = I2C(
    0, scl=Pin(17), sda=Pin(16), freq=400_000
)  # Init I2C using pins GP8 & GP9 (default I2C0 pins)

print("Speed set to " + str(freq()) + "Hz")  # get the current frequency of the CPU
print("I2C Address      : " + hex(i2c.scan()[0]).upper())  # Display device address
print("I2C Configuration: " + str(i2c))  # Display I2C config
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)  # Init oled display

# Clear the oled display in case it has junk on it.
oled.fill(0)

# org.bluetooth.service.environmental_sensing
_ENV_SENSE_UUID = bluetooth.UUID(0x181A)
# org.bluetooth.characteristic.temperature
_ENV_SENSE_TEMP_UUID = bluetooth.UUID(0x2A6E)


# Helper to decode the temperature characteristic encoding (sint16, hundredths of a degree).
def _decode_temperature(data):
    return struct.unpack("<h", data)[0] / 100


async def find_temp_sensor():
    # Scan for 5 seconds, in active mode, with very low interval/window (to
    # maximise detection rate).
    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            # See if it matches our name and the environmental sensing service.
            if result.name() == "mpy-temp" and _ENV_SENSE_UUID in result.services():
                return result.device
    return None


async def main():
    device = await find_temp_sensor()
    if not device:
        print("Temperature sensor not found")
        return

    try:
        print("Connecting to", device)
        connection = await device.connect()
    except asyncio.TimeoutError:
        print("Timeout during connection")
        return

    async with connection:
        try:
            temp_service = await connection.service(_ENV_SENSE_UUID)
            temp_characteristic = await temp_service.characteristic(_ENV_SENSE_TEMP_UUID)
        except asyncio.TimeoutError:
            print("Timeout discovering services/characteristics")
            return

        while True:
            temp_deg_c = _decode_temperature(await temp_characteristic.read())
            # print("Temperature: {:.2f}".format(temp_deg_c))
            oled.fill(0)
            oled.text("Temp: {:.2f}".format(temp_deg_c), 4, 40)
            oled.show()
            await asyncio.sleep_ms(2000)


asyncio.run(main())
