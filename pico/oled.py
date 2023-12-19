# Display Image & text on I2C driven ssd1306 OLED display
from machine import Pin, I2C, ADC, RTC, freq
import time

from ssd1306 import SSD1306_I2C


rtc = RTC()
analog_value = ADC(28)
conversion_factor = 3.3 / (65535)


WIDTH = 128  # oled display width
HEIGHT = 64  # oled display height

i2c = I2C(
    0, scl=Pin(17), sda=Pin(16), freq=400_000
)  # Init I2C using pins GP8 & GP9 (default I2C0 pins)

print("Speed set to " + str(freq()) + "Hz")  # get the current frequency of the CPU
print("I2C Address      : " + hex(i2c.scan()[0]).upper())  # Display device address
print("I2C Configuration: " + str(i2c))  # Display I2C config

oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)  # Init oled display


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

while True:
    try:
        oled.fill(0)
        reading = analog_value.read_u16()
        print("ADC: ", reading)
        time.sleep(0.2)
        voltageValue = reading * conversion_factor

        oled.text("Voltage:", 5, 8)
        oled.text(str(voltageValue) + "V", 15, 25)
        year, month, day, weekday, hours, minutes, seconds, subseconds = rtc.datetime()
        oled.text(f"{day}/{month}/{year}", 5, 40)
        oled.text(f"{hours}:{minutes}:{seconds}:{subseconds}", 5, 48)
        oled.show()
        time.sleep(0.9)
    except:
        print("Finished.")
        break
