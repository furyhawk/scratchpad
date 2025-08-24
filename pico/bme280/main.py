import utime
from machine import Pin, I2C
import network

# import ahtx0
import bme280
from ssd1306 import SSD1306_I2C
from mpy_env import get_env, load_env

# Global variables for error handling
MAX_RETRIES = 3
WIFI_TIMEOUT = 30
ERROR_COUNT = 0
MAX_ERRORS = 10

def safe_load_env():
    """Safely load environment variables with error handling"""
    try:
        load_env(verbose=True)
        return True
    except Exception as e:
        print(f"Error loading environment: {e}")
        return False

def display_error(oled, message):
    """Display error message on OLED"""
    try:
        oled.fill(0)
        oled.text("ERROR:", 0, 0)
        # Split long messages across lines
        words = message.split(' ')
        line = 1
        current_line = ""
        for word in words:
            if len(current_line + word) < 16:  # OLED character limit
                current_line += word + " "
            else:
                oled.text(current_line.strip(), 0, line * 10)
                line += 1
                current_line = word + " "
                if line > 5:  # Max lines on display
                    break
        if current_line and line <= 5:
            oled.text(current_line.strip(), 0, line * 10)
        oled.show()
    except Exception:
        pass  # If OLED fails, just continue

def connect_wifi(ssid, password, timeout=WIFI_TIMEOUT):
    """Connect to WiFi with timeout and error handling"""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if wlan.isconnected():
        print("Already connected to WiFi")
        return wlan
    
    print(f"Connecting to WiFi: {ssid}")
    wlan.connect(ssid, password)
    
    start_time = utime.time()
    while not wlan.isconnected():
        if utime.time() - start_time > timeout:
            print("WiFi connection timeout")
            return None
        utime.sleep(1)
    
    print("WiFi connected successfully")
    status = wlan.ifconfig()
    print(f'IP: {status[0]}')
    return wlan

def check_wifi_connection(wlan):
    """Check if WiFi is still connected"""
    if wlan and wlan.isconnected():
        return True
    return False

def initialize_i2c():
    """Initialize I2C with error handling"""
    try:
        i2c = I2C(1, scl=Pin(3), sda=Pin(2))
        devices = i2c.scan()
        
        if not devices:
            print("No I2C devices found")
            return None
            
        print("I2C devices found:")
        for d in devices:
            print(f"  {hex(d)}")
        return i2c
    except Exception as e:
        print(f"I2C initialization error: {e}")
        return None

def initialize_sensors(i2c):
    """Initialize OLED and BME280 sensors with error handling"""
    oled = None
    bme = None
    
    try:
        oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)
        print("OLED initialized successfully")
    except Exception as e:
        print(f"OLED initialization error: {e}")
    
    try:
        bme = bme280.BME280(i2c=i2c)
        print("BME280 initialized successfully")
    except Exception as e:
        print(f"BME280 initialization error: {e}")
    
    return oled, bme

def safe_sensor_reading(bme):
    """Safely read sensor values with error handling"""
    try:
        return bme.values
    except Exception as e:
        print(f"Sensor reading error: {e}")
        return None, None, None

def display_startup_screen(oled):
    """Display startup screen safely"""
    try:
        oled.fill(0)
        oled.fill_rect(0, 0, 32, 32, 1)
        oled.fill_rect(2, 2, 28, 28, 0)
        oled.vline(9, 8, 22, 1)
        oled.vline(16, 2, 22, 1)
        oled.vline(23, 8, 22, 1)
        oled.fill_rect(26, 24, 2, 4, 1)
        oled.text("MicroPython", 40, 0, 1)
        oled.text("SSD1306", 40, 12, 1)
        oled.text("OLED 128x64", 40, 24, 1)
        oled.show()
        return True
    except Exception as e:
        print(f"Startup screen error: {e}")
        return False

# Loading `env.json` at once as default.
# if `verbose` is true, the loader will print debug messages
if not safe_load_env():
    print("Failed to load environment, using defaults")

WIDTH = 128  # oled display width
HEIGHT = 64  # oled display height

# Get WiFi credentials with fallback
try:
    ssid = get_env("wifi")
    password = get_env("wifi_pwd")
    if not ssid or not password:
        raise ValueError("WiFi credentials not found")
except Exception as e:
    print(f"WiFi credential error: {e}")
    ssid = "your_wifi_ssid"  # Fallback values
    password = "your_wifi_password"

# Main execution with error handling and restart capability
def main():
    global ERROR_COUNT
    
    print("Starting BME280 sensor program...")
    
    # Connect to WiFi
    wlan = connect_wifi(ssid, password)
    if not wlan:
        print("WiFi connection failed, continuing without network...")
    
    # Initialize I2C
    i2c = initialize_i2c()
    if not i2c:
        print("I2C initialization failed - hardware issue")
        return False
    
    # Initialize sensors
    oled, bme = initialize_sensors(i2c)
    
    if not oled and not bme:
        print("All sensors failed to initialize")
        return False
    
    # Display startup screen
    if oled:
        display_startup_screen(oled)
        utime.sleep(3)
    
    # Main sensor loop
    while True:
        try:
            # Check WiFi connection periodically and reconnect if needed
            if wlan and not check_wifi_connection(wlan):
                print("WiFi disconnected, attempting reconnection...")
                wlan = connect_wifi(ssid, password)
            
            # Read sensor data
            if bme:
                temp, pressure, humidity = safe_sensor_reading(bme)
                
                if temp is not None:
                    print(f"Temp: {temp}, Pressure: {pressure}, Humidity: {humidity}")
                    ERROR_COUNT = 0  # Reset error count on successful reading
                    
                    # Display on OLED if available
                    if oled:
                        try:
                            oled.fill(0)
                            oled.text("BME280 3.3V:", 5, 8)
                            oled.text(f"Temp: {temp}", 1, 25)
                            oled.text(f"Pres: {pressure}", 1, 35)
                            oled.text(f"Hum: {humidity}", 1, 45)
                            oled.show()
                        except Exception as e:
                            print(f"OLED display error: {e}")
                            # Continue without OLED
                else:
                    ERROR_COUNT += 1
                    print(f"Sensor read failed (error count: {ERROR_COUNT})")
                    
                    if oled:
                        display_error(oled, "Sensor read failed")
            else:
                ERROR_COUNT += 1
                print(f"No BME280 sensor available (error count: {ERROR_COUNT})")
                
                if oled:
                    display_error(oled, "No BME280 sensor")
            
            # Check if too many errors occurred
            if ERROR_COUNT >= MAX_ERRORS:
                print("Too many errors, restarting...")
                return False
            
            # Sleep before next reading
            utime.sleep(10)
            
        except KeyboardInterrupt:
            print("Program interrupted by user")
            break
        except Exception as e:
            ERROR_COUNT += 1
            print(f"Unexpected error in main loop: {e}")
            
            if oled:
                display_error(oled, f"Error: {str(e)[:20]}")
            
            if ERROR_COUNT >= MAX_ERRORS:
                print("Too many errors, restarting...")
                return False
            
            utime.sleep(5)  # Wait before retry
    
    return True

# Program entry point with restart capability
def run_with_restart():
    restart_count = 0
    max_restarts = 5
    
    while restart_count < max_restarts:
        try:
            print(f"Program start (attempt {restart_count + 1})")
            
            if main():
                print("Program completed successfully")
                break
            else:
                restart_count += 1
                print(f"Program failed, restart {restart_count}/{max_restarts}")
                
                if restart_count < max_restarts:
                    print("Waiting 10 seconds before restart...")
                    utime.sleep(10)
                    
        except Exception as e:
            restart_count += 1
            print(f"Critical error: {e}")
            print(f"Restart {restart_count}/{max_restarts}")
            
            if restart_count < max_restarts:
                utime.sleep(10)
    
    if restart_count >= max_restarts:
        print("Maximum restart attempts reached. Program stopped.")
    else:
        print("Program finished.")

# Start the program
if __name__ == "__main__":
    run_with_restart()

