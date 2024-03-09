import utime
import ubinascii
from umqtt.simple import MQTTClient
import machine
import network

from mpy_env import get_env, load_env

# import ahtx0
import bme280
from ssd1306 import SSD1306_I2C

WIDTH = 128  # oled display width
HEIGHT = 64  # oled display height

# Loading `env.json` at once as default.
# if `verbose` is true, the loader will print debug messages
load_env(verbose=True)

ssid = get_env("wifi")
password = get_env("wifi_pwd")

# connect to wifi
wlan = network.WLAN(network.STA_IF)
if not wlan.isconnected():
    print("establishing wifi connection...")
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        pass
    print("wifi connected")
    status = wlan.ifconfig()
    print("ip = " + status[0])

# Default  MQTT_BROKER to connect to
MQTT_BROKER = "192.168.50.57"
CLIENT_ID = ubinascii.hexlify(machine.unique_id())
mqtt_user = get_env("mqtt_user")
mqtt_password = get_env("mqtt_password")
SUBSCRIBE_TOPIC = b"led"
PUBLISH_TOPIC = b"temperature"

# Setup built in PICO LED as Output
led = machine.Pin("LED", machine.Pin.OUT)

# Publish MQTT messages after every set timeout
last_publish = utime.time()
publish_interval = 20


# I2C for the Wemos D1 Mini with ESP8266
i2c = machine.I2C(
    1, scl=machine.Pin(3), sda=machine.Pin(2)
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
utime.sleep(3)


# Received messages from subscriptions will be delivered to this callback
def sub_cb(topic, msg):
    print((topic, msg))
    if msg.decode() == "ON":
        led.value(1)
    else:
        led.value(0)


def reset():
    print("Resetting...")
    utime.sleep(5)
    machine.reset()


# Generate dummy random temperature readings
def get_temperature_reading():
    return bme.values


def main():
    print(f"Begin connection with MQTT Broker :: {MQTT_BROKER}")
    mqttClient = MQTTClient(
        CLIENT_ID, MQTT_BROKER, 1883, mqtt_user, mqtt_password, keepalive=60
    )
    mqttClient.set_callback(sub_cb)
    mqttClient.connect()
    print("connected")
    mqttClient.subscribe(SUBSCRIBE_TOPIC)
    print(
        f"Connected to MQTT  Broker :: {MQTT_BROKER}, and waiting for callback function to be called!"
    )
    while True:
        # Non-blocking wait for message
        mqttClient.check_msg()
        global last_publish
        if (utime.time() - last_publish) >= publish_interval:
            temp, pressure, humidity = get_temperature_reading()
            mqttClient.publish(PUBLISH_TOPIC, str(temp).encode())
            last_publish = utime.time()
            oled.fill(0)
            oled.text("BME280 3.3V:", 5, 8)
            oled.text(f"Temp: {temp}", 1, 25)
            oled.text(f"pres: {pressure}", 1, 35)
            oled.text(f"hum: {humidity}", 1, 45)
            oled.show()

        utime.sleep(1)


if __name__ == "__main__":
    while True:
        try:
            main()
        except OSError as e:
            print("Error: " + str(e))
            reset()

