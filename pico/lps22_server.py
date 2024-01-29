import machine
import network
import socket
from time import sleep
from lps22hbtr import LPS22HB
from ina219 import INA219
from ds3231_gen import DS3231

from mpy_env import get_env, load_env

# Loading `env.json` at once as default.
# if `verbose` is true, the loader will print debug messages
load_env(verbose=True)


ssid = get_env("wifi")
password = get_env("wifi_pwd")

#    the new version use i2c0,if it dont work,try to uncomment the line 14 and comment line 17
#    it should solder the R3 with 0R resistor if want to use alarm function,please refer to the Sch file on waveshare Pico-RTC-DS3231 wiki
#    https://www.waveshare.net/w/upload/0/08/Pico-RTC-DS3231_Sch.pdf
I2C_PORT = 0
I2C_SDA = 20
I2C_SCL = 21

ALARM_PIN = 3


def connect():
    # Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    while wlan.isconnected() == False:
        print("Waiting for connection...")
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            sleep(1)
        print(wlan.ifconfig())

    ip = wlan.ifconfig()[0]
    print(f"Connected on http://{ip}")
    return ip


def open_socket(ip):
    # Open a socket
    address = (ip, 80)
    connection = socket.socket()
    connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    connection.bind(address)
    connection.listen(1)
    print(connection)
    return connection


def webpage(pressure, temperature, bus_voltage, current, P, curr_datetime):
    # Template HTML
    html = f"""
            <!DOCTYPE html>
            <html>
            <body>
            <p>Pressure is {pressure:6.2f} hPa</p>
            <p>Temperature is {temperature:6.2f} °C</p>
            <p>bus_voltage is {bus_voltage:6.3f} V</p>
            <p>current is {current:6.3f} A</p>
            <p>Charged is {P:6.2%}</p>
            <p>Current time is {curr_datetime}</p>
            </body>
            </html>
            """
    return str(html)


def serve(connection):
    lps22hb = LPS22HB()
    # Create an ADS1115 ADC (16-bit) instance.
    ina219 = INA219(addr=0x43)
    i2c = machine.I2C(I2C_PORT, scl=machine.Pin(I2C_SCL), sda=machine.Pin(I2C_SDA))
    dc3231 = DS3231(i2c)
    # Set time
    dc3231.set_time()
    print(str(dc3231.get_time()))
    rtc = machine.RTC()
    # Start a web server

    try:
        while True:
            client, addr = connection.accept()
            request = client.recv(1024)
            if not request:
                print(f">> {addr} disconnected")
                continue
            request = str(request)
            print(request)
            try:
                request = request.split()[1]
            except IndexError:
                pass

            pressure = lps22hb.pressure
            temperature = lps22hb.temperature

            bus_voltage = ina219.getBusVoltage_V()  # voltage on V- (load side)
            current = ina219.getCurrent_mA()  # current in mA
            P = (bus_voltage - 3) / 1.2 * 100
            if P < 0:
                P = 0
            elif P > 100:
                P = 100

            curr_datetime = rtc.datetime()
            curr_datetime = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
                curr_datetime[0],
                curr_datetime[1],
                curr_datetime[2],
                curr_datetime[4],
                curr_datetime[5],
                curr_datetime[6],
            )

            html = webpage(
                pressure,
                temperature,
                bus_voltage,
                current / 1000,
                P / 100,
                curr_datetime,
            )
            client.send(html)
            client.close()
            print("Sent a response")
            print(f"Pressure is {pressure:6.2f} hPa")
            print(f"Temperature is {temperature:6.2f} °C")
            # INA219 measure bus voltage on the load side. So PSU voltage = bus_voltage + shunt_voltage
            print("Voltage:  {:6.3f} V".format(bus_voltage))
            print("Current:  {:6.3f} A".format(current / 1000))
            print("Percent:  {:6.1f} %".format(P))
            print("Current time is {}".format(curr_datetime))
            sleep(1)
    except OSError as e:
        print("Socket error", e)
    finally:
        connection.close()
        print("Connection closed")


try:
    ip = connect()
    connection = open_socket(ip)

    serve(connection)
except KeyboardInterrupt:
    machine.reset()
