# This example demonstrates a simple temperature sensor peripheral.
#
# The sensor's local value updates every second, and it will notify
# any connected central every 10 seconds.

# This example demonstrates the low-level bluetooth module. For most
# applications, we recommend using the higher-level aioble library which takes
# care of all IRQ handling and connection management. See
# https://github.com/micropython/micropython-lib/tree/master/micropython/bluetooth/aioble
# and in particular the temp_sensor.py example included with aioble.

import bluetooth
import random
import struct
import utime

from machine import Pin, I2C

from micropython import const

import ahtx0
from ble_advertising import advertising_payload

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_INDICATE_DONE = const(20)

_FLAG_READ = const(0x0002)
_FLAG_NOTIFY = const(0x0010)
_FLAG_INDICATE = const(0x0020)

# org.bluetooth.service.environmental_sensing
_ENV_SENSE_UUID = bluetooth.UUID(0x181A)
# org.bluetooth.characteristic.temperature
_TEMP_CHAR = (
    bluetooth.UUID(0x2A6E),
    _FLAG_READ | _FLAG_NOTIFY | _FLAG_INDICATE,
)
_ENV_SENSE_SERVICE = (
    _ENV_SENSE_UUID,
    (_TEMP_CHAR,),
)

# org.bluetooth.characteristic.gap.appearance.xml
_ADV_APPEARANCE_GENERIC_THERMOMETER = const(768)


class BLETemperature:
    def __init__(self, ble, name="mpy-temp"):
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)
        ((self._handle,),) = self._ble.gatts_register_services((_ENV_SENSE_SERVICE,))
        self._connections = set()
        self._payload = advertising_payload(
            name=name,
            services=[_ENV_SENSE_UUID],
            appearance=_ADV_APPEARANCE_GENERIC_THERMOMETER,
        )
        self._advertise()

    def _irq(self, event, data):
        # Track connections so we can send notifications.
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            self._connections.add(conn_handle)
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            self._connections.remove(conn_handle)
            # Start advertising again to allow a new connection.
            self._advertise()
        elif event == _IRQ_GATTS_INDICATE_DONE:
            conn_handle, value_handle, status = data

    def set_temperature(self, temp_deg_c, notify=False, indicate=False):
        # Data is sint16 in degrees Celsius with a resolution of 0.01 degrees Celsius.
        # Write the local value, ready for a central to read.
        self._ble.gatts_write(self._handle, struct.pack("<h", int(temp_deg_c * 100)))
        if notify or indicate:
            for conn_handle in self._connections:
                if notify:
                    # Notify connected centrals.
                    self._ble.gatts_notify(conn_handle, self._handle)
                if indicate:
                    # Indicate connected centrals.
                    self._ble.gatts_indicate(conn_handle, self._handle)

    def _advertise(self, interval_us=500000):
        self._ble.gap_advertise(interval_us, adv_data=self._payload)


def demo():
    ble = bluetooth.BLE()
    temp = BLETemperature(ble)

    # I2C for the Wemos D1 Mini with ESP8266
    i2c = I2C(
        0, scl=Pin(1), sda=Pin(0), freq=400_000
    )  # Init I2C using pins GP8 & GP9 (default I2C0 pins)

    # Print out any addresses found
    devices = i2c.scan()
    # Create the sensor object using I2C 0x38
    sensor = ahtx0.AHT20(i2c)

    if devices:
        for d in devices:
            print(hex(d))
        i = 0

    while True:
        # Write every second, notify every 10 seconds.
        i = (i + 1) % 10
        print("\nTemperature: %0.2f C" % sensor.temperature)
        print("Humidity: %0.2f %%" % sensor.relative_humidity)
        temp.set_temperature(sensor.temperature, notify=i == 0, indicate=False)
        # Random walk the temperature.
        utime.sleep_ms(1000)


if __name__ == "__main__":
    demo()
