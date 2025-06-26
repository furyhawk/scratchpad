from machine import UART, Pin
from ch9120 import CH9120
import time

# CH9120
MODE = 1  #0:TCP Server 1:TCP Client 2:UDP Server 3:UDP Client
GATEWAY = (192, 168, 1, 1)    # GATEWAY
TARGET_IP = (192, 168, 1, 10) # TARGET_IP
LOCAL_IP = (192, 168, 1, 200) # LOCAL_IP
SUBNET_MASK = (255,255,255,0) # SUBNET_MASK
LOCAL_PORT1 = 1000            # LOCAL_PORT1
TARGET_PORT = 2000            # TARGET_PORT
BAUD_RATE = 115200            # BAUD_RATE

uart1 = UART(1, baudrate=9600, tx=Pin(20), rx=Pin(21))

def ch9120_configure():
    # Configure
    global uart1 
    ch9120 = CH9120(uart1)
    ch9120.enter_config() # enter configuration mode
    ch9120.set_mode(MODE)    # 0:TCP Server 1:TCP Client 2:UDP Server 3:UDP Client
    ch9120.set_localIP(LOCAL_IP)
    ch9120.set_subnetMask(SUBNET_MASK)
    ch9120.set_gateway(GATEWAY)
    ch9120.set_localPort(LOCAL_PORT1)
    ch9120.set_targetIP(TARGET_IP)
    ch9120.set_targetPort(TARGET_PORT)
    ch9120.set_baudRate(BAUD_RATE)
    ch9120.exit_config()  # exit configuration mode
    
    # Clear cache and reconfigure uart1
    uart1.read(uart1.any())
    time.sleep(0.5)
    uart1 = UART(1, baudrate=115200, tx=Pin(20), rx=Pin(21))
    
if __name__ == "__main__":
    ch9120_configure()
    while True:
        time.sleep(0.1)
        while uart1.any() > 0:
            rxData1 = uart1.read(uart1.any())
            uart1.write(rxData1)
            print(rxData1.decode('utf8'))
