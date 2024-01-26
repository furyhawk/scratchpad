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

    while wlan.isconnected() == False:
        print("Waiting for connection...")
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            sleep(1)
        print(wlan.ifconfig())

    ip = wlan.ifconfig()[0]
    print(f"Connected on {ip}")
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


def serve(connection, lps22hb):
    # Start a web server

    try:
        client, addr = connection.accept()
        while True:
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
            html = webpage(pressure, temperature)
            client.send(html)
            client.close()
            print("Sent a response")
            print(f"Pressure is {pressure:6.2f}  hPa")
            print(f"Temperature is {temperature:6.2f} °C")
            sleep(5)
    except OSError as e:
        print("Socket error", e)
    finally:
        connection.close()
        print("Connection closed")


try:
    ip = connect()
    connection = open_socket(ip)
    lps22hb = LPS22HB()
    serve(connection, lps22hb)
except KeyboardInterrupt:
    machine.reset()
