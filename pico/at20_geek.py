import utime
from machine import Pin, I2C, SoftI2C

import ahtx0

# I2C for the Wemos D1 Mini with ESP8266
i2c = SoftI2C(
    scl=Pin(29), sda=Pin(28)
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

