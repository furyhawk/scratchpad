import network
import socket
from time import sleep
from lps22hbtr import LPS22HB
import machine

ssid = "wifi_name"
password = "12345678"


def connect():
    # Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    while wlan.isconnected() == False:
        print("Waiting for connection...")
        sleep(1)
        print(wlan.ifconfig())
    ip = wlan.ifconfig()[0]
    print(f"Connected on {ip}")
    return ip


def open_socket(ip):
    # Open a socket
    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    print(connection)
    return connection


def webpage(pressure, temperature):
    # Template HTML
    html = f"""
            <!DOCTYPE html>
            <html>
            <body>
            <p>Pressure is {pressure:6.2f}  hPa</p>
            <p>Temperature is {temperature:6.2f} °C</p>
            </body>
            </html>
            """
    return str(html)


def serve(connection):
    # Start a web server
    lps22hb = LPS22HB()
    while True:
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        print(request)
        try:
            request = request.split()[1]
        except IndexError:
            pass

        html = webpage(lps22hb.pressure, lps22hb.temperature)
        client.send(html)
        sleep(5)
        client.close()


try:
    ip = connect()
    connection = open_socket(ip)
    serve(connection)
except KeyboardInterrupt:
    machine.reset()
