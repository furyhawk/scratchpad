import ntptime
import time
import network
from machine import Pin

from mpy_env import get_env, load_env

# Loading `env.json` at once as default.
# if `verbose` is true, the loader will print debug messages
load_env(verbose=True)


ssid = get_env("wifi")
password = get_env("wifi_pwd")

pico_led = Pin("LED", Pin.OUT)
pico_led.on()  # set pin to "on" (high) level


def connect():
    # Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    while wlan.isconnected() == False:
        print("Waiting for connection...")
        time.sleep(1)
        print(wlan.ifconfig())

    # if needed, overwrite default time server pool.ntp.org
    ntptime.host = "1.europe.pool.ntp.org"

    try:
        print("Local time before synchronization：%s" % str(time.localtime()))
        # make sure to have internet connection
        ntptime.settime()
        print("Local time after synchronization：%s" % str(time.localtime()))
    except:
        pico_led.off()
        print("Error syncing time")


connect()
