# from picozero import pico_led, LED, Switch
from time import sleep
from machine import Pin, Timer

"""     ---usb---
GP0  1  |o     o| -1  VBUS
GP1  2  |o     o| -2  VSYS
GND  3  |o     o| -3  GND
GP2  4  |o     o| -4  3V3_EN
GP3  5  |o     o| -5  3V3(OUT)
GP4  6  |o     o| -6           ADC_VREF
GP5  7  |o     o| -7  GP28     ADC2
GND  8  |o     o| -8  GND      AGND
GP6  9  |o     o| -9  GP27     ADC1
GP7  10 |o     o| -10 GP26     ADC0
GP8  11 |o     o| -11 RUN
GP9  12 |o     o| -12 GP22
GND  13 |o     o| -13 GND
GP10 14 |o     o| -14 GP21
GP11 15 |o     o| -15 GP20
GP12 16 |o     o| -16 GP19
GP13 17 |o     o| -17 GP18
GND  18 |o     o| -18 GND
GP14 19 |o     o| -19 GP17
GP15 20 |o     o| -20 GP16
        ---------"""

led = Pin(13, Pin.OUT)
timer = Timer()


def blink(timer) -> None:
    led.toggle()


timer.init(freq=10, mode=Timer.PERIODIC, callback=blink)

# try:
#     led = Pin(13, Pin.OUT)
#     timer = Timer()
#     pico_led.on()
#     sleep(1)
#     pico_led.off()

#     firefly = LED(13)  # Use GP13

#     switch = Pin(18, Pin.IN)  # Use GP18

#     while True:
#         if switch.is_closed:  # Wires are connected
#             firefly.on()
#             sleep(0.5)  # Stay on for half a second
#             firefly.off()
#             sleep(2.5)  # Stay off for 2.5 seconds
#         else:  # Wires are not connected
#             firefly.off()
#             sleep(0.1)  # Small delay

# except KeyboardInterrupt:
#     firefly.close()
#     print("finished")
