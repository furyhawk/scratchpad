import network
from machine import I2C, Pin, RTC, DEEPSLEEP, DEEPSLEEP_RESET, reset_cause
from umqtt.simple import MQTTClient

import ahtx0
from mpy_env import get_env, load_env

# Loading `env.json` at once as default.
# if `verbose` is true, the loader will print debug messages
load_env(verbose=True)


ssid = get_env("wifi")
password = get_env("wifi_pwd")

# I2C for the Wemos D1 Mini with ESP8266
i2c = I2C(1, scl=Pin(3), sda=Pin(2))

# Create the sensor object using I2C
sensor = ahtx0.AHT10(i2c)

# configure pin to prevent deepsleep, must by connected to GND to stop deepsleep
ds_pin = Pin(14, Pin.IN, Pin.PULL_UP)

# configure RTC.ALARM0 to be able to wake the device
rtc = RTC()
rtc.irq(trigger=rtc.ALARM0, wake=DEEPSLEEP)

# check if the device woke from a deep sleep
if reset_cause() == DEEPSLEEP_RESET:
    print("woke from a deep sleep")

# set RTC.ALARM0 to fire after 10 seconds (waking the device)
rtc.alarm(rtc.ALARM0, 10000)

# connect to wifi
wlan = network.WLAN(network.STA_IF)
if not wlan.isconnected():
    print("establishing wifi connection...")
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        pass
    print("wifi connected")

print("establishing mqtt broker connection...")
c = MQTTClient("umqtt_client", "hostname")
c.connect()
print("connected to mqtt broker")
c.publish(b"temp1/temperature", "{:.2f}".format(sensor.temperature))
c.publish(b"temp1/humidity", "{:.2f}".format(sensor.relative_humidity))
c.disconnect()

print("\nTemperature: %0.2f C" % sensor.temperature)
print("Humidity: %0.2f %%" % sensor.relative_humidity)

# put the device to sleep if ds_pin not connected to GND
if ds_pin.value() == 1:
    print("\nfalling into deepsleep for {} microseconds".format(10000))
    machine.deepsleep()

