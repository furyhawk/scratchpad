import utime
from machine import Pin, I2C
import network

from umqtt.simple import MQTTClient
# import ahtx0
import bme280
from ssd1306 import SSD1306_I2C
from mpy_env import get_env, load_env

from micropython import const

import uasyncio as asyncio
import aioble
import bluetooth

import struct

# Loading `env.json` at once as default.
# if `verbose` is true, the loader will print debug messages
load_env(verbose=True)

WIDTH = 128  # oled display width
HEIGHT = 64  # oled display height

ssid = get_env("wifi")
password = get_env("wifi_pwd")


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



# connect to wifi
# wlan = network.WLAN(network.STA_IF)
# if not wlan.isconnected():
#     print("establishing wifi connection...")
#     wlan.active(True)
#     wlan.connect(ssid, password)
#     while not wlan.isconnected():
#         pass
#     print("wifi connected")
#     status = wlan.ifconfig()
#     print('ip = ' + status[0])

# print("establishing mqtt broker connection...")
# c = MQTTClient("umqtt_client", "localhost") #, port=15672
# c.connect()
# print("connected to mqtt broker")


# I2C for the Wemos D1 Mini with ESP8266
i2c = I2C(
    1, scl=Pin(3), sda=Pin(2)
)  # Init I2C using pins GP8 & GP9 (default I2C0 pins)

# Print out any addresses found
devices = i2c.scan()

if devices:
    for d in devices:
        print(hex(d))

oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)  # Init oled display
utime.sleep(1)
bme = bme280.BME280(i2c=i2c)


# Clear the oled display in case it has junk on it.
oled.fill(0)

# Add some text
oled.fill(0)
oled.fill_rect(0, 0, 32, 32, 1)
oled.fill_rect(2, 2, 28, 28, 0)
oled.vline(9, 8, 22, 1)
oled.vline(16, 2, 22, 1)
oled.vline(23, 8, 22, 1)
oled.fill_rect(26, 24, 2, 4, 1)
oled.text("MicroPython", 40, 0, 1)
oled.text("SSD1306", 40, 12, 1)
oled.text("OLED 128x64", 40, 24, 1)

# Finally update the oled display so the image & text is displayed
oled.show()
time.sleep(3)

# Create the sensor object using I2C 0x38
# $sensor = ahtx0.AHT10(i2c)


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

            oled.text("BME280 3.3V:", 5, 8)
            temp, pressure, humidity = bme.values
            oled.text(f"Temp: {temp}", 1, 25)
            oled.text(f"pres: {pressure}", 1, 35)
            oled.text(f"hum: {humidity}", 1, 45)
            print(bme.values)
            # print("\nTemperature: %0.2f C" % sensor.temperature)
            # print("Humidity: %0.2f %%" % sensor.relative_humidity)

            oled.text("Temp: {:.2f}".format(temp_deg_c), 1, 55)
            oled.show()
            await asyncio.sleep_ms(2000)

asyncio.run(main())
