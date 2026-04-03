from machine import Pin
import time
import network
    
def redian():
    # Create a Wi-Fi access point
    ap = network.WLAN(network.AP_IF)
    # Enable access point
    ap.active(True)
    # Set access point parameters
    ap.config(essid='ESP32-S3-GEEK', authmode=network.AUTH_WPA_WPA2_PSK, password='Waveshare')
    # The IP address of the access point is displayed
    print('AP IP address:', ap.ifconfig()[0])

redian()
