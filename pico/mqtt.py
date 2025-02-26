import time
import ubinascii
from umqtt.simple import MQTTClient
import machine
import random
import usocket as socket
print(socket.socket())
from mpy_env import get_env, load_env
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
    print('ip = ' + status[0])


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
last_publish = time.time()
publish_interval = 5


# Received messages from subscriptions will be delivered to this callback
def sub_cb(topic, msg):
    print((topic, msg))
    if msg.decode() == "ON":
        led.value(1)
    else:
        led.value(0)


def reset():
    print("Resetting...")
    time.sleep(5)
    machine.reset()


# Generate dummy random temperature readings
def get_temperature_reading():
    return random.randint(20, 50)


def main():
    print(f"Begin connection with MQTT Broker :: {MQTT_BROKER}")
    mqttClient = MQTTClient(CLIENT_ID, MQTT_BROKER, 1883, mqtt_user, mqtt_password, keepalive=60)
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
        if (time.time() - last_publish) >= publish_interval:
            random_temp = get_temperature_reading()
            mqttClient.publish(PUBLISH_TOPIC, str(random_temp).encode())
            last_publish = time.time()
        time.sleep(1)


if __name__ == "__main__":
    while True:
        try:
            main()
        except OSError as e:
            print("Error: " + str(e))
            reset()

