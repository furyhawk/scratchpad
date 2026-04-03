import machine

uart = machine.UART(1, baudrate=115200, tx=machine.Pin(43), rx=machine.Pin(44))

def send_data(data):
    uart.write(data)

def receive_data():
    if uart.any():
        data = uart.read()
        print("Received data:",data)

send_data("Hello UART")

while True:
    receive_data()