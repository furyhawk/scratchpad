from machine import UART, Pin
from mqtt_client import MQTTClient
from ch9120 import CH9120
import time

# MQTT
CLIENT_ID = "Waveshare_RP2040_ETH"
SUBSCRIBE_TOPIC = "test_topic1"
PUBLISH_TOPIC = "test_topic2"

# CH9120
MODE = 1  #0:TCP Server 1:TCP Client 2:UDP Server 3:UDP Client
GATEWAY = (192, 168, 1, 1)     # GATEWAY
TARGET_IP = (47, 92, 129, 18)  # TARGET_IP
LOCAL_IP = (192, 168, 1, 200)  # LOCAL_IP
SUBNET_MASK = (255,255,255,0)  # SUBNET_MASK
LOCAL_PORT1 = 1000             # LOCAL_PORT1
TARGET_PORT = 1883             # TARGET_PORT
BAUD_RATE = 115200             # BAUD_RATE

uart1 = UART(1, baudrate=9600, tx=Pin(20), rx=Pin(21))

def ch9120_configure():
    global uart1 
    ch9120 = CH9120(uart1)
    ch9120.enter_config() # enter configuration mode
    ch9120.set_mode(MODE)    
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
    mqtt_client = MQTTClient(uart1)
    mqtt_client.ClientID = CLIENT_ID # Set ClientID
    mqtt_client.connect() # Connect to MQTT server
    mqtt_client.subscribe(SUBSCRIBE_TOPIC) # Subscribe to topic：test_topic1
    
    mqtt_client.send_heartbeat()
    last_heartbeat_time = time.time()
    time.sleep_ms(60) # Sending the first heartbeat
    uart1.read() # Clear unnecessary data

    while True:
        rxData = uart1.read()
        if rxData is not None:
            topic, message = mqtt_client.extract_data(rxData) # Parse the received data
            if topic == SUBSCRIBE_TOPIC:
                print("Topic:", topic)
                print("Message:", message)
                mqtt_client.publish(PUBLISH_TOPIC, message) # Send received data to topic：test_topic2
                
        current_time = time.time()
        if current_time - last_heartbeat_time >= 30:
            mqtt_client.send_heartbeat() # Send a heartbeat every 30 seconds
            last_heartbeat_time = current_time
            time.sleep_ms(60) # Waiting for the server to respond
            if not mqtt_client.check_heartbeat_response():
                while True:
                    print("Reconnecting...")
                    mqtt_client = MQTTClient(uart1)
                    mqtt_client.ClientID = CLIENT_ID # Set ClientID
                    mqtt_client.connect() # Connect to MQTT server
                    mqtt_client.subscribe(SUBSCRIBE_TOPIC) # Subscribe to topic：test_topic1
                    time.sleep_ms(200) # Waiting for the server to respond
                    uart1.read() # Clear unnecessary data
                    mqtt_client.send_heartbeat() # Sending the first heartbeat
                    last_heartbeat_time = current_time # Clear unnecessary data
                    time.sleep_ms(60) # Waiting for the server to respond
                    if mqtt_client.check_heartbeat_response():
                        print("Reconnection successful!")
                        break
            
        time.sleep_ms(20)
        
        