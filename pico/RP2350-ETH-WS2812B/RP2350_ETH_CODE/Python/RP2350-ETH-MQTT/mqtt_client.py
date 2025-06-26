from machine import UART
import time
import ubinascii

class MQTTClient:
    def __init__(self, uart):
        self.uart = uart
        self.ClientID = "Waveshare_RP2040_ETH"
        self.connect_message = bytearray([
            0x10,  # MQTT control packet type (CONNECT)
            0x11,  # Remaining Length in the fixed header
            0x00, 0x04,  # Length of the UTF-8 encoded protocol name
            0x4D, 0x51, 0x54, 0x54,  # MQTT string "MQTT"
            0x04,  # Protocol Level (MQTT 3.1.1)
            0x02,  # Connect Flags: Clean Session, No Will, No Will Retain, QoS = 0, No Will Flag, Keep Alive = 60 seconds
            0x00, 0x3C  # Keep Alive Time in seconds  
        ])

    def connect(self):
        byte_array = bytes(self.ClientID, "utf-8")
        length = len(byte_array)
        self.connect_message.extend(length.to_bytes(2, 'big')) # Length of the Client ID
        self.connect_message.extend(byte_array) # Client ID
        self.connect_message[1] = len(self.connect_message) - 2 # Change Length
        self.uart.write(bytes(self.connect_message))

    def publish(self, topic, message):
        publish_message = bytearray([
            0x30, 0x11,   # MQTT control packet type (PUBLISH)
            0x00, 0x0A    # Length of the topic name
        ])
        publish_message.extend(bytes(topic, "utf-8"))   # Topic
        publish_message.extend(bytes(message, "utf-8")) # Message content
        publish_message[1] = len(publish_message) - 2   # Change Length
        publish_message[3] = len(bytes(topic, "utf-8")) # Change Length
        self.uart.write(bytes(publish_message))

    def subscribe(self, topic):
        subscribe_message = bytearray([
            0x82, 0x0A,   # MQTT control packet type (SUBSCRIBE)
            0x00, 0x01    # Remaining length
        ])
        byte_array = bytes(topic, "utf-8")
        length = len(byte_array)
        subscribe_message.extend(length.to_bytes(2, 'big')) # Length of the topic name
        subscribe_message.extend(byte_array) # Topic
        subscribe_message.extend(bytes([0x00])) # qos
        subscribe_message[1] = len(subscribe_message) - 2 # Change Length
        self.uart.write(bytes(subscribe_message))
        
    def send_heartbeat(self):
        heartbeat_message = bytearray([0xC0, 0x00])# Heartbeat message to keep the connection alive
        self.uart.write(heartbeat_message)
        
    def check_heartbeat_response(self):
        response = self.uart.read()# Check for PINGRESP message
        if response == bytes([0xD0, 0x00]):
            return True
        else:
            return False

    def extract_data(self, rxData):
        rxArray = bytearray()
        rxArray.extend(rxData)
        topic = rxArray[4:4 + rxArray[3]].decode('utf-8')
        message = rxArray[4 + rxArray[3]:rxArray[1] + 2].decode('utf-8')
        return topic, message

