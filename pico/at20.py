import utime
from machine import Pin, I2C

import ahtx0

# I2C for the Wemos D1 Mini with ESP8266
i2c = I2C(
    1, scl=Pin(3), sda=Pin(2), freq=40_000
)  # Init I2C using pins GP8 & GP9 (default I2C0 pins)

# Print out any addresses found
devices = i2c.scan()

if devices:
    for d in devices:
        print(hex(d))


# Create the sensor object using I2C 0x38
sensor = ahtx0.AHT10(i2c)

while True:
    print("\nTemperature: %0.2f C" % sensor.temperature)
    print("Humidity: %0.2f %%" % sensor.relative_humidity)
    utime.sleep(5)
