import utime
import ubinascii
from umqtt.simple import MQTTClient
import machine
import network
try:
    import ntptime  # MicroPython NTP client
except Exception:
    ntptime = None

from mpy_env import get_env, load_env

# import ahtx0
import bme280
from ssd1306 import SSD1306_I2C

# Loading `env.json` at once as default.
# if `verbose` is true, the loader will print debug messages
try:
    load_env(verbose=True)
except Exception as e:
    print(f"Failed to load environment: {e}")
    machine.reset()

# Validate required environment variables
try:
    ssid = get_env("wifi")
    password = get_env("wifi_pwd")
    MQTT_USER = get_env("mqtt_user")
    MQTT_PASSWORD = get_env("mqtt_password")
    
    if not all([ssid, password, MQTT_USER, MQTT_PASSWORD]):
        raise ValueError("Missing required environment variables")
except Exception as e:
    print(f"Environment configuration error: {e}")
    machine.reset()

WIDTH = 128  # oled display width
HEIGHT = 64  # oled display height

# I2C/OLED config (can be overridden via env.json on device)
try:
    I2C_BUS = int(get_env("i2c_bus") or 1)  # 0 or 1. Default: 1 (GP2=SDA, GP3=SCL)
except Exception:
    I2C_BUS = 1
try:
    I2C_SDA = int(get_env("i2c_sda") or 2)  # Default GP2 for I2C1
except Exception:
    I2C_SDA = 2
try:
    I2C_SCL = int(get_env("i2c_scl") or 3)  # Default GP3 for I2C1
except Exception:
    I2C_SCL = 3
try:
    I2C_FREQ = int(get_env("i2c_freq") or 400000)
except Exception:
    I2C_FREQ = 400000
try:
    OLED_ADDR = int(get_env("oled_addr"), 0) if get_env("oled_addr") else 0x3C
except Exception:
    OLED_ADDR = 0x3C

# Time/NTP configuration (optional via env.json)
try:
    NTP_SERVER = get_env("ntp_server") or "pool.ntp.org"
except Exception:
    NTP_SERVER = "pool.ntp.org"
try:
    TZ_OFFSET_MINUTES = int(get_env("tz_offset_minutes") or 0)  # e.g., -300 for EST (UTC-5)
except Exception:
    TZ_OFFSET_MINUTES = 0
try:
    NTP_SYNC_INTERVAL = int(get_env("ntp_sync_interval") or 3600)  # seconds; default 1 hour
except Exception:
    NTP_SYNC_INTERVAL = 3600

# Default  MQTT_BROKER to connect to
MQTT_BROKER = "broker.furyhawk.lol"
MQTT_PORT = 1883
CLIENT_ID = ubinascii.hexlify(machine.unique_id())
SUBSCRIBE_TOPIC = b"led"
PUBLISH_TOPIC_TEMP = b"temperature"
PUBLISH_TOPIC_PRESSURE = b"pressure"
PUBLISH_TOPIC_HUMIDITY = b"humidity"
PUBLISH_TOPIC_DATETIME = b"datetime"

# Configuration constants
WIFI_TIMEOUT = 30  # seconds
MQTT_KEEPALIVE = 60  # seconds
PUBLISH_INTERVAL = 180  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

# OLED burn-in prevention settings
DISPLAY_TIMEOUT = 300  # Turn off display after 5 minutes of inactivity
SCREENSAVER_INTERVAL = 600  # Show screensaver every 10 minutes
PIXEL_SHIFT_INTERVAL = 120  # Shift content every 2 minutes
MAX_PIXEL_SHIFT = 3  # Maximum pixels to shift content
BRIGHTNESS_CYCLE_INTERVAL = 60  # Cycle brightness every minute


def safe_display_operation(func, *args, **kwargs):
    """Safely execute display operations with error handling"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        print(f"Display operation failed: {e}")
        return None


class OLEDBurnInProtection:
    """Class to manage OLED burn-in prevention strategies"""
    
    def __init__(self, oled, width=WIDTH, height=HEIGHT):
        self.oled = oled
        self.width = width
        self.height = height
        self.last_activity = utime.time()
        self.last_screensaver = utime.time()
        self.last_pixel_shift = utime.time()
        self.last_brightness_cycle = utime.time()
        self.pixel_shift_x = 0
        self.pixel_shift_y = 0
        self.display_on = True
        self.brightness_level = 0
        self.screensaver_active = False
        
    def update_activity(self):
        """Update last activity timestamp"""
        now = utime.time()
        self.last_activity = now
        # Any user-driven update cancels screensaver and ensures display is on
        if self.screensaver_active:
            self.screensaver_active = False
            # Push out next screensaver a bit to avoid immediate retrigger
            self.last_screensaver = now
        if not self.display_on:
            self.turn_on_display()
    
    def turn_off_display(self):
        """Turn off display to prevent burn-in"""
        if self.display_on:
            # Try to actually power off panel (or at least blank it)
            def _off():
                try:
                    if hasattr(self.oled, "poweroff"):
                        self.oled.poweroff()
                    elif hasattr(self.oled, "write_cmd"):
                        self.oled.write_cmd(0xAE)  # DISPLAYOFF
                except Exception:
                    pass
                self.oled.fill(0)
                self.oled.show()
            safe_display_operation(_off)
            self.display_on = False
            self.screensaver_active = False
            print("Display turned off for burn-in protection")
    
    def turn_on_display(self):
        """Turn on display"""
        if not self.display_on:
            def _on():
                try:
                    if hasattr(self.oled, "poweron"):
                        self.oled.poweron()
                    elif hasattr(self.oled, "write_cmd"):
                        self.oled.write_cmd(0xAF)  # DISPLAYON
                    if hasattr(self.oled, "invert"):
                        self.oled.invert(0)
                    if hasattr(self.oled, "contrast"):
                        self.oled.contrast(255)
                except Exception:
                    pass
            safe_display_operation(_on)
            self.display_on = True
            self.screensaver_active = False
            print("Display turned on")
    
    def show_screensaver(self):
        """Show animated screensaver pattern"""
        if not self.display_on:
            return
            
        def _screensaver():
            self.oled.fill(0)
            # Simple moving dot screensaver
            time_offset = int(utime.time()) % 60
            x = (time_offset * 2) % (self.width - 1)
            y = (time_offset) % (self.height - 1)
            self.oled.pixel(x, y, 1)
            
            # Add some moving lines
            for i in range(0, self.width, 20):
                line_x = (i + time_offset) % self.width
                self.oled.vline(line_x, 0, self.height, 1)
            
            self.oled.show()
        
        safe_display_operation(_screensaver)
        self.screensaver_active = True
    
    def update_pixel_shift(self):
        """Update pixel shift values for content movement"""
        current_time = utime.time()
        if current_time - self.last_pixel_shift >= PIXEL_SHIFT_INTERVAL:
            self.pixel_shift_x = (self.pixel_shift_x + 1) % (MAX_PIXEL_SHIFT * 2 + 1) - MAX_PIXEL_SHIFT
            self.pixel_shift_y = (self.pixel_shift_y + 1) % (MAX_PIXEL_SHIFT * 2 + 1) - MAX_PIXEL_SHIFT
            self.last_pixel_shift = current_time
    
    def cycle_brightness(self):
        """Cycle through different brightness levels"""
        current_time = utime.time()
        if current_time - self.last_brightness_cycle >= BRIGHTNESS_CYCLE_INTERVAL:
            # Simple brightness cycling (this is conceptual as SSD1306 has limited brightness control)
            self.brightness_level = (self.brightness_level + 1) % 3
            self.last_brightness_cycle = current_time
    
    def check_burn_in_protection(self):
        """Check and apply burn-in protection measures"""
        current_time = utime.time()
        
        # Check if display should be turned off
        if current_time - self.last_activity >= DISPLAY_TIMEOUT:
            self.turn_off_display()
            return False
        
        # Check if screensaver should be shown
        if current_time - self.last_screensaver >= SCREENSAVER_INTERVAL:
            self.show_screensaver()
            self.last_screensaver = current_time
            return False
        
        # Update pixel shift and brightness
        self.update_pixel_shift()
        self.cycle_brightness()
        
        return self.display_on and not self.screensaver_active
    
    def get_shift_offset(self):
        """Get current pixel shift offset"""
        return self.pixel_shift_x, self.pixel_shift_y


# Global burn-in protection instance
burn_in_protection = None


def clear_display(oled):
    """Clear the OLED display safely"""
    global burn_in_protection
    if not oled:
        return
    if burn_in_protection:
        burn_in_protection.update_activity()
    return safe_display_operation(lambda: oled.fill(0) or oled.show())


def display_text(oled):
    """Display default text on OLED safely with burn-in protection"""
    global burn_in_protection
    if not oled:
        return
    if burn_in_protection:
        burn_in_protection.update_activity()
        if not burn_in_protection.check_burn_in_protection():
            return
        shift_x, shift_y = burn_in_protection.get_shift_offset()
    else:
        shift_x, shift_y = 0, 0
    
    def _display():
        oled.fill_rect(0 + shift_x, 0 + shift_y, 32, 32, 1)
        oled.fill_rect(2 + shift_x, 2 + shift_y, 28, 28, 0)
        oled.vline(9 + shift_x, 8 + shift_y, 22, 1)
        oled.vline(16 + shift_x, 2 + shift_y, 22, 1)
        oled.vline(23 + shift_x, 8 + shift_y, 22, 1)
        oled.fill_rect(26 + shift_x, 24 + shift_y, 2, 4, 1)
        oled.text("MicroPython", 40 + shift_x, 0 + shift_y, 1)
        oled.text("SSD1306", 40 + shift_x, 12 + shift_y, 1)
        oled.text("OLED 128x64", 40 + shift_x, 24 + shift_y, 1)
        oled.show()
    
    return safe_display_operation(_display)


def update_display(oled):
    """Update display with default content"""
    clear_display(oled)
    display_text(oled)
    utime.sleep(1)


def display_sensor_data(oled, temp, pressure, humidity):
    """Display sensor data on OLED safely with burn-in protection"""
    global burn_in_protection
    if not oled:
        return
    if burn_in_protection:
        burn_in_protection.update_activity()
        if not burn_in_protection.check_burn_in_protection():
            return
        shift_x, shift_y = burn_in_protection.get_shift_offset()
    else:
        shift_x, shift_y = 0, 0
    
    def _display_sensor():
        oled.fill(0)
        oled.text("BME280 3.3V:", 5 + shift_x, 8 + shift_y)
        oled.text(f"Temp: {temp}", 1 + shift_x, 25 + shift_y)
        oled.text(f"Pres: {pressure}", 1 + shift_x, 35 + shift_y)
        oled.text(f"Hum: {humidity}", 1 + shift_x, 45 + shift_y)
        
        # Add timestamp to prevent static content
        timestamp = utime.time() % 100  # Last 2 digits of timestamp
        oled.text(f"T:{timestamp:02d}", 90 + shift_x, 55 + shift_y)
        
        oled.show()
    
    return safe_display_operation(_display_sensor)


def display_status(oled, status_msg):
    """Display status message on OLED with burn-in protection"""
    global burn_in_protection
    if not oled:
        return
    if burn_in_protection:
        burn_in_protection.update_activity()
        if not burn_in_protection.check_burn_in_protection():
            return
        shift_x, shift_y = burn_in_protection.get_shift_offset()
    else:
        shift_x, shift_y = 0, 0
    
    def _display_status():
        oled.fill(0)
        lines = status_msg.split('\n')
        for i, line in enumerate(lines[:4]):  # Max 4 lines
            oled.text(line[:16], 0 + shift_x, i * 12 + shift_y)  # Max 16 chars per line
        
        # Add moving indicator to prevent static display
        indicator_pos = (utime.time() % 8) * 2
        oled.pixel(int(120 + shift_x), int(indicator_pos + shift_y), 1)
        
        oled.show()
    
    return safe_display_operation(_display_status)


def display_network_info(oled, wifi_ip, mqtt_status):
    """Display network information with burn-in protection"""
    global burn_in_protection
    if not oled:
        return
    if burn_in_protection:
        burn_in_protection.update_activity()
        if not burn_in_protection.check_burn_in_protection():
            return
        shift_x, shift_y = burn_in_protection.get_shift_offset()
    else:
        shift_x, shift_y = 0, 0
    
    def _display_network():
        oled.fill(0)
        oled.text("Network Status:", 0 + shift_x, 0 + shift_y)
        oled.text(f"IP: {wifi_ip[-12:]}", 0 + shift_x, 12 + shift_y)  # Show last 12 chars of IP
        oled.text(f"MQTT: {mqtt_status}", 0 + shift_x, 24 + shift_y)
        
        # Add animated connection indicator
        time_mod = utime.time() % 4
        indicators = ["|", "/", "-", "\\"]
        oled.text(indicators[time_mod], 110 + shift_x, 36 + shift_y)
        
        oled.show()
    
    return safe_display_operation(_display_network)


# Received messages from subscriptions will be delivered to this callback
def sub_cb(topic, msg, led):
    """MQTT subscription callback with error handling"""
    try:
        print((topic, msg))
        msg_str = msg.decode()
        if msg_str == "ON":
            led.value(1)
        else:
            led.value(0)
    except Exception as e:
        print(f"Callback error: {e}")


def connect_wifi(max_retries=MAX_RETRIES):
    """Connect to WiFi with timeout and retry logic"""
    wlan = network.WLAN(network.STA_IF)
    
    for attempt in range(max_retries):
        try:
            if wlan.isconnected():
                print("WiFi already connected")
                return wlan
            
            print(f"WiFi connection attempt {attempt + 1}/{max_retries}")
            wlan.active(True)
            wlan.connect(ssid, password)
            
            # Wait for connection with timeout
            timeout = utime.time() + WIFI_TIMEOUT
            while not wlan.isconnected() and utime.time() < timeout:
                utime.sleep(1)
            
            if wlan.isconnected():
                status = wlan.ifconfig()
                print(f"WiFi connected - IP: {status[0]}")
                return wlan
            else:
                print(f"WiFi connection timeout on attempt {attempt + 1}")
                wlan.active(False)
                utime.sleep(RETRY_DELAY)
                
        except Exception as e:
            print(f"WiFi connection error on attempt {attempt + 1}: {e}")
            wlan.active(False)
            utime.sleep(RETRY_DELAY)
    
    raise Exception("Failed to connect to WiFi after all retries")


def connect_mqtt(client_id, broker, port, user, password, max_retries=MAX_RETRIES):
    """Connect to MQTT broker with retry logic"""
    for attempt in range(max_retries):
        try:
            print(f"MQTT connection attempt {attempt + 1}/{max_retries}")
            client = MQTTClient(client_id, broker, port, user, password, keepalive=MQTT_KEEPALIVE)
            client.connect()
            print(f"Connected to MQTT broker: {broker}")
            return client
        except Exception as e:
            print(f"MQTT connection error on attempt {attempt + 1}: {e}")
            utime.sleep(RETRY_DELAY)
    
    raise Exception("Failed to connect to MQTT after all retries")


def _init_i2c(bus, sda_pin, scl_pin, freq=400000):
    """Create an I2C instance and scan for devices; returns (i2c, devices)"""
    i2c = machine.I2C(bus, sda=machine.Pin(sda_pin), scl=machine.Pin(scl_pin), freq=freq)
    devices = i2c.scan()
    print(f"I2C(bus={bus}, sda=GP{sda_pin}, scl=GP{scl_pin}, freq={freq}) scan -> {list(map(hex, devices))}")
    return i2c, devices


def initialize_hardware():
    """Initialize all hardware components with error handling"""
    global burn_in_protection
    
    try:
        # Setup built-in PICO LED
        led = machine.Pin("LED", machine.Pin.OUT)
        print("LED initialized")
        
        # Initialize I2C (with fallback)
        i2c, devices = _init_i2c(I2C_BUS, I2C_SDA, I2C_SCL, I2C_FREQ)
        if not devices:
            print("No I2C devices found on primary config; trying fallback I2C0 GP0/GP1...")
            try:
                i2c, devices = _init_i2c(0, 0, 1, I2C_FREQ)
            except Exception as e:
                print(f"Fallback I2C0 init failed: {e}")
        if not devices:
            raise Exception("No I2C devices found on any tried configuration")
        
        # Log devices
        print("I2C devices found:")
        for d in devices:
            print(f"  {hex(d)}")
        
        # Initialize OLED display with robust fallbacks (freq and address)
        oled = None
        last_error = None

        def _try_init_oled(current_i2c, devices):
            nonlocal last_error
            for addr in [OLED_ADDR, 0x3D]:
                try:
                    if addr not in devices:
                        print(f"Warning: OLED address {hex(addr)} not seen in scan; attempting anyway...")
                    utime.sleep_ms(50)
                    candidate = SSD1306_I2C(WIDTH, HEIGHT, current_i2c, addr=addr)
                    try:
                        if hasattr(candidate, "poweron"):
                            candidate.poweron()
                        if hasattr(candidate, "write_cmd"):
                            candidate.write_cmd(0xAF)  # DISPLAYON
                        if hasattr(candidate, "contrast"):
                            candidate.contrast(255)
                        if hasattr(candidate, "invert"):
                            candidate.invert(0)
                    except Exception:
                        pass
                    candidate.fill(0)
                    candidate.text("OLED init", 0, 0)
                    candidate.text(f"addr {hex(addr)}", 0, 10)
                    utime.sleep_ms(10)
                    candidate.show()
                    print(f"OLED display initialized at {hex(addr)}")
                    return candidate
                except Exception as e:
                    print(f"OLED init failed at {hex(addr)}: {e}")
                    last_error = e
            return None

        # Use existing I2C first (expects variables i2c and devices already defined above)
        try:
            oled_candidate = _try_init_oled(i2c, devices)
        except NameError:
            oled_candidate = None
        if oled_candidate:
            oled = oled_candidate
        else:
            for fallback_freq in (200000, 100000, 50000):
                try:
                    print(f"Retrying OLED init with lower I2C freq: {fallback_freq}")
                    i2c, devices = _init_i2c(I2C_BUS, I2C_SDA, I2C_SCL, fallback_freq)
                    oled = _try_init_oled(i2c, devices)
                    if oled:
                        break
                except Exception as e:
                    print(f"I2C re-init at {fallback_freq} failed: {e}")

        if oled is None:
            print(f"Failed to initialize OLED after fallbacks: {last_error}")
            print("Continuing without OLED (headless mode).")

        # Initialize burn-in protection only if OLED present
        if oled is not None:
            burn_in_protection = OLEDBurnInProtection(oled)
            print("OLED burn-in protection enabled")
        
        # Initialize BME280 sensor
        print("Available attributes in bme280 module:", dir(bme280))
        try:
            bme = bme280.BME280(i2c=i2c)
            print("BME280 sensor initialized")
        except AttributeError as e:
            print(f"BME280 AttributeError: {e}")
            print("This usually means the bme280.py file wasn't properly uploaded or has import issues")
            print("Make sure bme280.py is in the same directory as this script on the MicroPython device")
            # For now, create a dummy sensor object to prevent crashes
            print("Creating dummy sensor for testing...")
            class DummyBME280:
                def __init__(self, i2c):
                    self.i2c = i2c
                    print("Using dummy BME280 sensor")
                
                @property
                def values(self):
                    return ("25.0C", "1013.25hPa", "50.0%")
            
            bme = DummyBME280(i2c)
            print("Dummy BME280 sensor initialized - please fix the real BME280 import")
        
        # Test sensor reading
        try:
            temp, pressure, humidity = bme.values
            print(f"Sensor test - Temp: {temp}, Pressure: {pressure}, Humidity: {humidity}")
        except Exception as e:
            print(f"Sensor test failed: {e}")
            raise
        
        if oled is not None:
            update_display(oled)
        return led, oled, bme, i2c
        
    except Exception as e:
        print(f"Hardware initialization error: {e}")
        raise


def safe_sensor_reading(bme, max_retries=3):
    """Read sensor data with retry logic"""
    for attempt in range(max_retries):
        try:
            temp, pressure, humidity = bme.values
            return temp, pressure, humidity
        except Exception as e:
            print(f"Sensor reading error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                utime.sleep(1)
            else:
                raise


def mqtt_publish_safe(client, topic, data, max_retries=3):
    """Safely publish MQTT message with retries"""
    for attempt in range(max_retries):
        try:
            client.publish(topic, str(data).encode())
            return True
        except Exception as e:
            print(f"MQTT publish error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                utime.sleep(1)
            else:
                return False


def reset_with_delay(delay=10):
    """Reset the device with a countdown"""
    print(f"Resetting in {delay} seconds...")
    for i in range(delay, 0, -1):
        print(f"Reset in {i}...")
        utime.sleep(1)
    machine.reset()


def get_current_datetime():
    """Get current date and time as formatted string"""
    try:
        # Get current time in seconds since epoch (apply timezone offset)
        offset_sec = TZ_OFFSET_MINUTES * 60
        current_time = utime.time() + offset_sec

        # Convert to local time tuple (year, month, day, hour, minute, second, weekday, yearday)
        time_tuple = utime.localtime(current_time)

        # Format as readable string
        year, month, day, hour, minute, second = time_tuple[:6]
        weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        weekday = weekdays[time_tuple[6]]

        date_str = f"{year:04d}-{month:02d}-{day:02d}"
        time_str = f"{hour:02d}:{minute:02d}:{second:02d}"
        datetime_str = f"{date_str} {time_str} {weekday}"

        return datetime_str, date_str, time_str

    except Exception as e:
        print(f"Error getting datetime: {e}")
        # Return fallback values
        return "Time Error", "Date Error", "Time Error"


def sync_time(max_retries=3, retry_delay=2):
    """Synchronize RTC via NTP. Returns True on success, False otherwise."""
    if ntptime is None:
        print("NTP not available on this firmware")
        return False
    try:
        ntptime.host = NTP_SERVER
    except Exception:
        pass

    for attempt in range(max_retries):
        try:
            print(f"NTP sync attempt {attempt+1}/{max_retries} using {NTP_SERVER}")
            ntptime.settime()  # sets RTC to UTC
            # Basic sanity check: year should be reasonably current
            y = utime.localtime()[0]
            if y < 2023:
                raise Exception(f"RTC year still {y} after NTP set")
            print("Time synchronized via NTP")
            return True
        except Exception as e:
            print(f"NTP sync error: {e}")
            utime.sleep(retry_delay)
    return False


def display_datetime(oled):
    """Display current date and time on OLED with burn-in protection"""
    global burn_in_protection
    if not oled:
        return
    if burn_in_protection:
        burn_in_protection.update_activity()
        if not burn_in_protection.check_burn_in_protection():
            return
        shift_x, shift_y = burn_in_protection.get_shift_offset()
    else:
        shift_x, shift_y = 0, 0
    
    def _display_datetime():
        datetime_str, date_str, time_str = get_current_datetime()
        
        oled.fill(0)
        oled.text("Date & Time:", 0 + shift_x, 0 + shift_y)
        oled.text(date_str, 0 + shift_x, 15 + shift_y)
        oled.text(time_str, 0 + shift_x, 30 + shift_y)
        
        # Add seconds indicator for dynamic content
        seconds = utime.time() % 60
        indicator = "." * (seconds % 4 + 1)
        oled.text(indicator, 100 + shift_x, 45 + shift_y)
        
        oled.show()
    
    return safe_display_operation(_display_datetime)


def main():
    """Main application function with comprehensive error handling"""
    global burn_in_protection
    mqtt_client = None
    oled = None
    
    try:
        # Initialize hardware
        led, oled, bme, i2c = initialize_hardware()
        display_status(oled, "Hardware\nInitialized")
        
        # Connect to WiFi
        display_status(oled, "Connecting\nWiFi...")
        wlan = connect_wifi()
        wifi_ip = wlan.ifconfig()[0]
        display_status(oled, f"WiFi Connected\n{wifi_ip}")
        
        # Sync time via NTP (best effort)
        ntp_ok = sync_time()
        if ntp_ok:
            display_status(oled, "Time\nSynchronized")
        else:
            display_status(oled, "Time Sync\nSkipped/Failed")
        
        last_time_sync = utime.time()
        
        # Connect to MQTT
        display_status(oled, "Connecting\nMQTT...")
        mqtt_client = connect_mqtt(CLIENT_ID, MQTT_BROKER, MQTT_PORT, MQTT_USER, MQTT_PASSWORD)
        mqtt_client.set_callback(lambda *args: sub_cb(*args, led=led))
        mqtt_client.subscribe(SUBSCRIBE_TOPIC)
        display_status(oled, "MQTT\nConnected")
        
        print(f"Connected to MQTT Broker: {MQTT_BROKER}")
        print("Waiting for messages and publishing sensor data...")
        
        # Main loop variables
        last_publish = utime.time() - PUBLISH_INTERVAL
        last_display_update = utime.time()
        display_rotation_interval = 30  # Rotate display content every 30 seconds
        display_mode = 0  # 0: sensor data, 1: network info, 2: datetime, 3: status
        
        while True:
            current_time = utime.time()
            
            # Check WiFi connection
            if not wlan.isconnected():
                print("WiFi disconnected, attempting reconnection...")
                display_status(oled, "WiFi\nReconnecting...")
                wlan = connect_wifi()
                wifi_ip = wlan.ifconfig()[0]
                # Reconnect MQTT after WiFi reconnection
                if mqtt_client:
                    try:
                        mqtt_client.disconnect()
                    except Exception:
                        pass
                mqtt_client = connect_mqtt(CLIENT_ID, MQTT_BROKER, MQTT_PORT, MQTT_USER, MQTT_PASSWORD)
                mqtt_client.set_callback(lambda *args: sub_cb(*args, led=led))
                mqtt_client.subscribe(SUBSCRIBE_TOPIC)
                display_status(oled, "Reconnected")
                # Re-sync time after network recovery
                try:
                    if sync_time():
                        display_status(oled, "Time\nSynchronized")
                        last_time_sync = utime.time()
                except Exception as _:
                    pass
            
            # Check for MQTT messages
            try:
                mqtt_client.check_msg()
            except Exception as e:
                print(f"MQTT check_msg error: {e}")
                # Try to reconnect MQTT
                try:
                    mqtt_client.disconnect()
                except Exception:
                    pass
                mqtt_client = connect_mqtt(CLIENT_ID, MQTT_BROKER, MQTT_PORT, MQTT_USER, MQTT_PASSWORD)
                mqtt_client.set_callback(lambda *args: sub_cb(*args, led=led))
                mqtt_client.subscribe(SUBSCRIBE_TOPIC)
            
            # Publish sensor data periodically
            if (current_time - last_publish) >= PUBLISH_INTERVAL:
                try:
                    print("Reading sensors and publishing data...")
                    temp, pressure, humidity = safe_sensor_reading(bme)
                    datetime_str, date_str, time_str = get_current_datetime()
                    
                    # Publish data
                    publish_success = all([
                        mqtt_publish_safe(mqtt_client, PUBLISH_TOPIC_TEMP, temp),
                        mqtt_publish_safe(mqtt_client, PUBLISH_TOPIC_PRESSURE, pressure),
                        mqtt_publish_safe(mqtt_client, PUBLISH_TOPIC_HUMIDITY, humidity),
                        mqtt_publish_safe(mqtt_client, PUBLISH_TOPIC_DATETIME, datetime_str)
                    ])
                    
                    if publish_success:
                        print(f"Published: T={temp}, P={pressure}, H={humidity}, DT={datetime_str}")
                        last_publish = current_time
                    else:
                        print("Failed to publish some sensor data")
                        
                except Exception as e:
                    print(f"Sensor reading/publishing error: {e}")
            
            # Rotate display content to prevent burn-in
            if (current_time - last_display_update) >= display_rotation_interval:
                try:
                    if burn_in_protection and burn_in_protection.check_burn_in_protection():
                        if display_mode == 0:  # Sensor data
                            temp, pressure, humidity = safe_sensor_reading(bme)
                            display_sensor_data(oled, temp, pressure, humidity)
                        elif display_mode == 1:  # Network info
                            mqtt_status = "Connected" if mqtt_client else "Disconnected"
                            display_network_info(oled, wifi_ip, mqtt_status)
                        elif display_mode == 2:  # Date and time
                            display_datetime(oled)
                        else:  # Status info
                            uptime = int(current_time) % 86400  # Uptime in seconds (mod 24h)
                            display_status(oled, f"Uptime: {uptime}s\nMode: {display_mode}")
                        
                        display_mode = (display_mode + 1) % 4
                        last_display_update = current_time
                        
                except Exception as e:
                    print(f"Display update error: {e}")
            
            # Apply burn-in protection measures
            if burn_in_protection:
                burn_in_protection.check_burn_in_protection()
            
            # Periodic NTP re-sync
            try:
                if (current_time - last_time_sync) >= NTP_SYNC_INTERVAL and wlan.isconnected():
                    if sync_time():
                        last_time_sync = current_time
            except Exception as _:
                pass

            # Free up memory periodically
            if current_time % 300 == 0:  # Every 5 minutes
                import gc
                gc.collect()
            
            utime.sleep(10)
            
    except KeyboardInterrupt:
        # Re-raise KeyboardInterrupt to allow Ctrl-C to exit
        print("Program interrupted by user")
        if mqtt_client:
            try:
                mqtt_client.disconnect()
            except Exception:
                pass
        if oled and burn_in_protection:
            display_status(oled, "Stopped")
            burn_in_protection.turn_off_display()
        raise  # Re-raise to ensure the program exits
        
    except Exception as e:
        print(f"Main loop error: {e}")
        if oled and burn_in_protection:
            display_status(oled, f"Error:\n{str(e)[:20]}")
            utime.sleep(3)
            burn_in_protection.turn_off_display()
        if mqtt_client:
            try:
                mqtt_client.disconnect()
            except Exception:
                pass
        raise


if __name__ == "__main__":
    try:
        while True:
            try:
                main()
            except KeyboardInterrupt:
                # Only allow Ctrl-C to break and exit
                print("Program terminated by user (Ctrl-C)")
                break
            except Exception as e:
                # For any other exception, log it but continue running
                print(f"Non-fatal error occurred: {e}")
                print("Continuing program... Press Ctrl-C to exit.")
                utime.sleep(5)  # Brief pause before restarting
    except KeyboardInterrupt:
        # Catch any KeyboardInterrupt that might escape the inner try-except
        print("Program terminated by user (Ctrl-C)")
    
    print("Program ended")
