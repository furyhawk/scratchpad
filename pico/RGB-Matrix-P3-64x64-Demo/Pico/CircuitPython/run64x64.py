import board
import displayio
import framebufferio
import rgbmatrix
from digitalio import DigitalInOut, Direction, Pull
import adafruit_display_text.label
import terminalio
from adafruit_bitmap_font import bitmap_font
import time
from math import sin
import os
import random
import json

bit_depth_value = 3
unit_width = 64
unit_height = 64
chain_width = 1
chain_height = 1
serpentine_value = True

width_value = unit_width*chain_width
height_value = unit_height*chain_height

displayio.release_displays()

matrix = rgbmatrix.RGBMatrix(
    width = width_value, height=height_value, bit_depth=bit_depth_value,
    rgb_pins = [board.GP2, board.GP3, board.GP4, board.GP5, board.GP8, board.GP9],
    addr_pins = [board.GP10, board.GP16, board.GP18, board.GP20, board.GP22],
    clock_pin = board.GP11, latch_pin=board.GP12, output_enable_pin=board.GP13,
    tile = chain_height, serpentine=serpentine_value,
    doublebuffer = True)

DISPLAY = framebufferio.FramebufferDisplay(matrix, auto_refresh=True,rotation=180)

now = t0 =time.monotonic_ns()
append_flag = 0

# Burn-in prevention settings (tunable)
# - Pixel shift: small periodic nudge to avoid static placement
# - Dimming window: lower brightness during night hours
# - Screensaver: occasional moving box to exercise pixels
PIXEL_SHIFT_INTERVAL_S = 15        # seconds between small shifts
PIXEL_SHIFT_RANGE = 24             # max +/- pixels to shift
NIGHT_DIM_START_HOUR = 18          # local hour to start dimming (18=6pm)
NIGHT_DIM_END_HOUR = 7             # local hour to stop dimming (7=7am)
BRIGHTNESS_DAY = 0.3               # normal brightness (0.0-1.0)
BRIGHTNESS_NIGHT = 0.1             # dimmed brightness at night
SCREENSAVER_INTERVAL_S = 600       # run screensaver every 10 minutes
SCREENSAVER_DURATION_S = 30        # run it for 30 seconds

# Optional buttons (Pico pins likely free with this matrix wiring)
BUTTON_A_PIN = getattr(board, "GP14", None)  # Next action / screensaver
BUTTON_B_PIN = getattr(board, "GP15", None)  # Toggle brightness

# Global button objects (lazy-init)
_BTN_A = None
_BTN_B = None

def _set_display_brightness(value):
    """Safely set brightness if supported by the Display or matrix."""
    try:
        if hasattr(DISPLAY, "brightness"):
            DISPLAY.brightness = max(0.0, min(1.0, float(value)))
            return True
    except Exception:
        pass
    try:
        if hasattr(matrix, "brightness"):
            matrix.brightness = max(0.0, min(1.0, float(value)))
            return True
    except Exception:
        pass
    return False

def _init_buttons():
    """Initialize buttons if pins exist and not already set."""
    global _BTN_A, _BTN_B
    try:
        if BUTTON_A_PIN and _BTN_A is None:
            _BTN_A = DigitalInOut(BUTTON_A_PIN)
            _BTN_A.direction = Direction.INPUT
            _BTN_A.pull = Pull.UP
        if BUTTON_B_PIN and _BTN_B is None:
            _BTN_B = DigitalInOut(BUTTON_B_PIN)
            _BTN_B.direction = Direction.INPUT
            _BTN_B.pull = Pull.UP
    except Exception:
        # Buttons are optional; ignore any setup errors
        _BTN_A = _BTN_B = None

def _buttons_state():
    """Return tuple (a_pressed, b_pressed) with simple level read (active low)."""
    a = (getattr(_BTN_A, "value", True) is False)
    b = (getattr(_BTN_B, "value", True) is False)
    return a, b

def _read_text_from_file(path="message.txt", max_len=256):
    try:
        if not path:
            return None
        if path and (path in os.listdir(".")):
            with open(path, "r") as f:
                s = f.read(max_len)
                s = s.strip().replace("\n", " ")
                return s or None
    except Exception:
        return None
    return None

def _parse_color(value, default=0x00FFFF):
    """Parse color from int or '#RRGGBB' string."""
    try:
        if isinstance(value, int):
            return max(0, min(0xFFFFFF, value))
        if isinstance(value, str):
            s = value.strip()
            if s.startswith("#"):
                s = s[1:]
            return int(s, 16) & 0xFFFFFF
    except Exception:
        pass
    return default

def load_config(path="config.json"):
    """Load optional config.json from CIRCUITPY root. Returns dict with defaults merged."""
    cfg = {}
    try:
        if path in os.listdir("."):
            with open(path, "r") as f:
                cfg = json.load(f) or {}
    except Exception:
        cfg = {}
    # Provide defaults and normalized values
    defaults = {
        "tz_offset": 0,
        "enable_ntp": True,
        "brightness_day": BRIGHTNESS_DAY,
        "brightness_night": BRIGHTNESS_NIGHT,
        "dim_start_hour": NIGHT_DIM_START_HOUR,
        "dim_end_hour": NIGHT_DIM_END_HOUR,
        "pixel_shift_interval": PIXEL_SHIFT_INTERVAL_S,
        "pixel_shift_range": PIXEL_SHIFT_RANGE,
        "screensaver_interval": SCREENSAVER_INTERVAL_S,
        "screensaver_duration": SCREENSAVER_DURATION_S,
        "default_mode": "auto",  # auto -> message.txt else clock
        "marquee_text": None,
        "marquee_color": "#00FFFF",
        "marquee_speed": 30,
        "image_folder": "images",
        "image_interval": 5,
    }
    out = defaults.copy()
    out.update({k: cfg.get(k, v) for k, v in defaults.items()})
    # Normalize some fields
    out["marquee_color"] = _parse_color(out.get("marquee_color"), defaults["marquee_color"] if isinstance(defaults["marquee_color"], int) else 0x00FFFF)
    try:
        out["tz_offset"] = int(float(out["tz_offset"]))
    except Exception:
        out["tz_offset"] = 0
    for k in ("brightness_day", "brightness_night"):
        try:
            out[k] = float(out[k])
        except Exception:
            out[k] = defaults[k]
    for k in ("dim_start_hour", "dim_end_hour"):
        try:
            out[k] = int(out[k]) % 24
        except Exception:
            out[k] = defaults[k]
    return out

# Wi-Fi helpers (optional): read credentials from environment and connect.
# To use, create a settings.toml on the CIRCUITPY drive with:
# CIRCUITPY_WIFI_SSID="your-ssid"
# CIRCUITPY_WIFI_PASSWORD="your-password"
# (Fallback env names WIFI_SSID/WIFI_PASSWORD are also supported.)
def _get_wifi_credentials():
    ssid = os.getenv("CIRCUITPY_WIFI_SSID") or os.getenv("WIFI_SSID")
    password = os.getenv("CIRCUITPY_WIFI_PASSWORD") or os.getenv("WIFI_PASSWORD")
    return ssid, password

def connect_wifi_from_env(timeout=15):
    try:
        import wifi  # type: ignore
    except ImportError:
        return False, "Wi-Fi module not available on this board"

    ssid, password = _get_wifi_credentials()
    if not ssid or not password:
        return False, "Wi-Fi credentials not found in settings.toml"

    # Already connected?
    try:
        if getattr(wifi.radio, "connected", False):
            return True, str(wifi.radio.ipv4_address)
    except Exception:
        pass

    start = time.monotonic()
    last_err = None
    while time.monotonic() - start < timeout:
        try:
            wifi.radio.connect(ssid, password)
            return True, str(wifi.radio.ipv4_address)
        except Exception as e:  # retry a few times within timeout
            last_err = e
            time.sleep(0.5)
    return False, repr(last_err) if last_err else "Unknown Wi-Fi error"

# Sync RTC from NTP over Wi‑Fi. Returns (ok: bool, info: str)
def sync_datetime_via_ntp(tz_offset_hours=0, server="pool.ntp.org", retries=3, timeout=5.0):
    try:
        import wifi  # type: ignore
        import socketpool  # type: ignore
        import adafruit_ntp  # type: ignore
        import rtc  # type: ignore
    except ImportError as e:
        return False, f"Required module missing for NTP sync: {e}"

    # Ensure Wi‑Fi connected (safe if already connected)
    if not getattr(wifi.radio, "connected", False):
        ok, info = connect_wifi_from_env()
        if not ok:
            return False, f"Wi‑Fi not connected: {info}"

    pool = socketpool.SocketPool(wifi.radio)
    try:
        ntp = adafruit_ntp.NTP(pool, server=server, tz_offset=tz_offset_hours, socket_timeout=timeout)
    except Exception as e:
        return False, f"Failed to init NTP: {repr(e)}"

    last_err = None
    for _ in range(max(1, int(retries))):
        try:
            t = ntp.datetime  # struct_time adjusted by tz_offset
            rtc.RTC().datetime = t
            y, mo, d, hh, mm, ss = t[0], t[1], t[2], t[3], t[4], t[5]
            return True, f"{y:04d}-{mo:02d}-{d:02d} {hh:02d}:{mm:02d}:{ss:02d}"
        except Exception as e:
            last_err = e
            time.sleep(0.5)
    return False, f"NTP sync failed: {repr(last_err)}"

# Utility: get current date/time as a formatted string (YYYY-MM-DD HH:MM:SS).
# Note: On boards without an RTC or without time sync, the year may be 1970/2000.
def get_current_datetime():
    try:
        tm = time.localtime()
        # time.localtime() in CircuitPython returns a time.struct_time indexable like a tuple
        y, mo, d, hh, mm, ss = tm[0], tm[1], tm[2], tm[3], tm[4], tm[5]
        # If RTC isn't set, many boards report a default epoch year; we still format it.
        return f"{y:04d}-{mo:02d}-{d:02d} {hh:02d}:{mm:02d}:{ss:02d}"
    except Exception as e:
        # Graceful fallback
        return "0000-00-00 00:00:00"

class RGB_Api():
    def __init__(self):
        # Instance-level display group to avoid relying on globals
        self.group = displayio.Group()

        #Set image
        self.image = 'CN.bmp'

        #Set text
        self.txt_str = "Waveshare"
        self.txt_color = 0x00ffff
        self.txt_x = 0
        self.txt_y = 32
        self.txt_font = terminalio.FONT
        self.txt_line_spacing = 0.8
        self.txt_scale = 1

        #Set scroll
        self.scroll_speed = 30

        #The following codes don't need to be set
        self.sroll_BITMAP = displayio.OnDiskBitmap(open(self.image, 'rb'))
        self.sroll_image1 = displayio.TileGrid(
                self.sroll_BITMAP,
                pixel_shader = getattr(self.sroll_BITMAP, 'pixel_shader', displayio.ColorConverter()),
                width = 1,
                height = 1,
                x = 0,
                y = 0,
                tile_width = self.sroll_BITMAP.width,
                tile_height = self.sroll_BITMAP.height)
        self.sroll_image2 = displayio.TileGrid(
                self.sroll_BITMAP,
                pixel_shader = getattr(self.sroll_BITMAP, 'pixel_shader', displayio.ColorConverter()),
                width = 1,
                height = 1,
                x = -self.sroll_BITMAP.width,
                y = -self.sroll_BITMAP.height,
                tile_width = self.sroll_BITMAP.width,
                tile_height = self.sroll_BITMAP.height)
        if self.txt_font == terminalio.FONT:
            self.txt_font = terminalio.FONT
        else:
            self.txt_font = bitmap_font.load_font(self.txt_font)
        self.sroll_text1 = adafruit_display_text.label.Label(
                self.txt_font,
                color = self.txt_color,
                line_spacing = self.txt_line_spacing,
                scale = self.txt_scale,
                text = self.txt_str)
        self.sroll_text1.x = 0
        self.sroll_text1.y = DISPLAY.height//2
        self.sroll_text2 = adafruit_display_text.label.Label(
                self.txt_font,
                color = self.txt_color,
                line_spacing = self.txt_line_spacing,
                scale = self.txt_scale,
                text = self.txt_str)
        self.sroll_text2.x = -self.sroll_text1.bounding_box[2]
        self.sroll_text2.y = DISPLAY.height//2

        self.rebound_flag = 0 #Rebound_flag
        self.sroll_object = 0

    #@brief:  Display an image in static mode
    #@param:  self
    #@retval: None
    def static_image(self):
        BITMAP = displayio.OnDiskBitmap(open(self.image, 'rb'))
        GROUP = displayio.Group()
        GROUP.append(displayio.TileGrid(
        BITMAP,
        pixel_shader = getattr(BITMAP, 'pixel_shader', displayio.ColorConverter()),
        width = 1,
        height = 1,
        tile_width = BITMAP.width,
        tile_height = BITMAP.height))

        DISPLAY.root_group = GROUP
        DISPLAY.refresh()
        while True:
            pass

    #@brief:  Display an image from left to right in horizontal mode
    #@param:  self
    #@retval: None
    def image_left_to_right_horizontal(self):
        global append_flag
        self.sroll_image2.y = 0
        x = self.sroll_image1.x + 1
        time.sleep(1/self.scroll_speed)
        if x > self.sroll_BITMAP.width:
            x = 0
        self.sroll_image1.x = x
        self.sroll_image2.x = -(self.sroll_BITMAP.width-self.sroll_image1.x)
        if append_flag == 0:
            append_flag = 1
            self.group.append(self.sroll_image1)
            self.group.append(self.sroll_image2)
            DISPLAY.root_group = self.group

    #@brief:  Display an image from right to left in horizontal mode
    #@param:  self
    #@retval: None
    def image_right_to_left_horizontal(self):
        global append_flag
        self.sroll_image2.y = 0
        x = self.sroll_image1.x - 1
        time.sleep(1/self.scroll_speed)
        if x < 0:
            x = self.sroll_BITMAP.width
        self.sroll_image1.x = x
        self.sroll_image2.x = -(self.sroll_BITMAP.width-self.sroll_image1.x)
        if append_flag == 0:
            append_flag = 1
            self.group.append(self.sroll_image1)
            self.group.append(self.sroll_image2)
            DISPLAY.root_group = self.group

    #@brief:  Display an image from up to down in vertical mode
    #@param:  self
    #@retval: None
    def image_up_to_down_vertical(self):
        global append_flag
        self.sroll_image2.x = 0
        y = self.sroll_image1.y + 1
        time.sleep(1/self.scroll_speed)
        if y > self.sroll_BITMAP.height:
            y = 0
        self.sroll_image1.y = y
        self.sroll_image2.y = -(self.sroll_BITMAP.height-self.sroll_image1.y)
        if append_flag == 0:
            append_flag = 1
            self.group.append(self.sroll_image1)
            self.group.append(self.sroll_image2)
            DISPLAY.root_group = self.group

    #@brief:  Display an image from down to up in vertical mode
    #@param:  self
    #@retval: None
    def image_down_to_up_vertical(self):
        global append_flag
        self.sroll_image2.x = 0
        y = self.sroll_image1.y - 1
        time.sleep(1/self.scroll_speed)
        if y < 0:
            y = self.sroll_BITMAP.height
        self.sroll_image1.y = y
        self.sroll_image2.y = -(self.sroll_BITMAP.height-self.sroll_image1.y)
        if append_flag == 0:
            append_flag = 1
            self.group.append(self.sroll_image1)
            self.group.append(self.sroll_image2)
            DISPLAY.root_group = self.group

    #@brief:  Display a text in static mode
    #@param:  self
    #@retval: None
    def static_text(self):
        TEXT = adafruit_display_text.label.Label(
            self.txt_font,
            color = self.txt_color,
            scale = self.txt_scale,
            text = self.txt_str,
            line_spacing = self.txt_line_spacing
            )
        TEXT.x = self.txt_x
        TEXT.y = self.txt_y
        GROUP = displayio.Group()
        GROUP.append(TEXT)
        DISPLAY.root_group = GROUP
        DISPLAY.refresh()
        while True:
            pass


    #@brief:  Display a text from left to right in sinusoidal scrolling mode
    #@param:  self
    #@retval: None
    def text_sin_left_to_right(self):
        global append_flag
        global now
        global t0
        T = 1/self.scroll_speed
        t_max = t0 + T
        n = 5/self.scroll_speed
        A = 7.5
        Y0 = DISPLAY.height//2
        dt = (now - t0) * 1e-9
        time.sleep(1/self.scroll_speed)
        x = self.sroll_text1.x + 1
        if x > DISPLAY.width:
            x = 0
        self.sroll_text1.x = x
        self.sroll_text2.x = -(DISPLAY.width-self.sroll_text1.x)
        y =  round(Y0 + sin(dt / n) * A)
        self.sroll_text2.y=self.sroll_text1.y = y
        while True:
            now = time.monotonic_ns()
            if now > t_max:
                break
            time.sleep((t_max - now) * 1e-9)
        t_max += T
        if append_flag == 0:
            append_flag = 1
            self.group.append(self.sroll_text1)
            self.group.append(self.sroll_text2)
            DISPLAY.root_group = self.group

    #@brief:  Display a text from right to left in sinusoidal scrolling mode
    #@param:  self
    #@retval: None
    def text_sin_right_to_left(self):
        global append_flag
        global now
        global t0
        T = 1/self.scroll_speed
        t_max = t0 + T
        n = 5/self.scroll_speed
        A = 7.5
        Y0 = DISPLAY.height//2
        dt = (now - t0) * 1e-9
        time.sleep(1/self.scroll_speed)
        x = self.sroll_text1.x - 1
        if x < 0:
            x = DISPLAY.width
        self.sroll_text1.x = x
        self.sroll_text2.x = -(DISPLAY.width-self.sroll_text1.x)
        y =  round(Y0 + sin(dt / n) * A)
        self.sroll_text2.y=self.sroll_text1.y = y
        while True:
            now = time.monotonic_ns()
            if now > t_max:
                break
            time.sleep((t_max - now) * 1e-9)
        t_max += T
        if append_flag == 0:
            append_flag = 1
            self.group.append(self.sroll_text1)
            self.group.append(self.sroll_text2)
            DISPLAY.root_group = self.group

    #@brief:  Display a text from up to down in sinusoidal scrolling mode
    #@param:  self
    #@retval: None
    def text_sin_up_to_down(self):
        global append_flag
        global now
        global t0
        T = 1/self.scroll_speed
        t_max = t0 + T
        n = 5/self.scroll_speed
        A = 5
        X0 = 6
        dt = (now - t0) * 1e-9
        time.sleep(1/self.scroll_speed)
        y = self.sroll_text1.y + 1
        if y > DISPLAY.height:
            y = 0
        self.sroll_text1.y = y
        self.sroll_text2.y = -(DISPLAY.height-self.sroll_text1.y)
        x =  round(X0 + sin(dt / n) * A)
        self.sroll_text2.x=self.sroll_text1.x = x
        while True:
            now = time.monotonic_ns()
            if now > t_max:
                break
            time.sleep((t_max - now) * 1e-9)
        t_max += T
        if append_flag == 0:
            append_flag = 1
            self.group.append(self.sroll_text1)
            self.group.append(self.sroll_text2)
            DISPLAY.root_group = self.group

    #@brief:  Display a text from down to up in sinusoidal scrolling mode
    #@param:  self
    #@retval: None
    def text_sin_down_to_up(self):
        global append_flag
        global now
        global t0
        T = 1/self.scroll_speed
        t_max = t0 + T
        n = 5/self.scroll_speed
        A = 5
        X0 = 6
        dt = (now - t0) * 1e-9
        time.sleep(1/self.scroll_speed)
        y = self.sroll_text1.y - 1
        if y < 0:
            y = DISPLAY.height
        self.sroll_text1.y = y
        self.sroll_text2.y = -(DISPLAY.height-self.sroll_text1.y)
        x =  round(X0 + sin(dt / n) * A)
        self.sroll_text2.x=self.sroll_text1.x = x
        while True:
            now = time.monotonic_ns()
            if now > t_max:
                break
            time.sleep((t_max - now) * 1e-9)
        t_max += T
        if append_flag == 0:
            append_flag = 1
            self.group.append(self.sroll_text1)
            self.group.append(self.sroll_text2)
            DISPLAY.root_group = self.group

    #@brief:  Display a text from left to right in horizontal mode
    #@param:  self
    #@retval: None
    def text_left_to_right_horizontal(self):
        global append_flag
        self.sroll_text1.y=DISPLAY.height//2
        self.sroll_text2.y=DISPLAY.height//2
        x = self.sroll_text1.x + 1
        time.sleep(1/self.scroll_speed)
        if x > DISPLAY.width:
            x = 0
        self.sroll_text1.x = x
        self.sroll_text2.x=-(DISPLAY.width-self.sroll_text1.x)
        if append_flag == 0:
            append_flag = 1
            self.group.append(self.sroll_text1)
            self.group.append(self.sroll_text2)
            DISPLAY.root_group = self.group

    #@brief:  Display a text from left to right in horizontal mode
    #@param:  self
    #@retval: None
    def text_right_to_left_horizontal(self):
        global append_flag
        self.sroll_text1.y=DISPLAY.height//2
        self.sroll_text2.y=DISPLAY.height//2
        x = self.sroll_text1.x - 1
        time.sleep(1/self.scroll_speed)
        if x < 0:
            x = DISPLAY.width
        self.sroll_text1.x = x
        self.sroll_text2.x=-(DISPLAY.width-self.sroll_text1.x)
        if append_flag == 0:
            append_flag = 1
            self.group.append(self.sroll_text1)
            self.group.append(self.sroll_text2)
            DISPLAY.root_group = self.group

    #@brief:  Display a text from up to down in vertical mode
    #@param:  self
    #@retval: None
    def text_up_to_down_vertical(self):
        global append_flag
        self.sroll_text1.x=0
        self.sroll_text2.x=0
        y = self.sroll_text1.y + 1
        time.sleep(1/self.scroll_speed)
        if y > DISPLAY.height:
            y = 0
        self.sroll_text1.y = y
        self.sroll_text2.y=-(DISPLAY.height-self.sroll_text1.y)
        if append_flag == 0:
            append_flag = 1
            self.group.append(self.sroll_text1)
            self.group.append(self.sroll_text2)
            DISPLAY.root_group = self.group

    #@brief:  Display a text from down to up in vertical mode
    #@param:  self
    #@retval: None
    def text_down_to_up_vertical(self):
        global append_flag
        self.sroll_text1.x=0
        self.sroll_text2.x=0
        y = self.sroll_text1.y - 1
        time.sleep(1/self.scroll_speed)
        if y < 0:
            y = DISPLAY.height
        self.sroll_text1.y = y
        self.sroll_text2.y=-(DISPLAY.height-self.sroll_text1.y)
        if append_flag == 0:
            append_flag = 1
            self.group.append(self.sroll_text1)
            self.group.append(self.sroll_text2)
            DISPLAY.root_group = self.group

    #@brief:  Display a text in left and right rebound mode
    #@param:  self
    #@retval: None
    def text_rebound_left_and_right(self):
        global append_flag
        self.sroll_text1.y=DISPLAY.height//2
        time.sleep(1/self.scroll_speed)
        if self.rebound_flag == 0:
            x = self.sroll_text1.x + 1
            if x > DISPLAY.width-self.sroll_text1.bounding_box[2]:
                self.rebound_flag = 1
        else :
            x = self.sroll_text1.x - 1
            if x < 0:
                self.rebound_flag = 0
        self.sroll_text1.x = x
        if append_flag == 0:
            append_flag = 1
            self.group.append(self.sroll_text1)
            DISPLAY.root_group = self.group

    #@brief:  Display a text in up and down rebound mode
    #@param:  self
    #@retval: None
    def text_rebound_up_and_down(self):
        global append_flag
        time.sleep(1/self.scroll_speed)
        if self.rebound_flag == 0:
            y = self.sroll_text1.y + 1
            if y > DISPLAY.height-8:
                self.rebound_flag = 1
        else :
            y = self.sroll_text1.y - 1
            if y < 3:
                self.rebound_flag = 0
        self.sroll_text1.y = y
        if append_flag == 0:
            append_flag = 1
            self.group.append(self.sroll_text1)
            DISPLAY.root_group = self.group

    #@brief:  Choose mode
    #@param:  The number of mode
    #@retval: None
    def test(self,mode):
        if mode == 1:
            self.static_image()
        elif mode == 2:
            self.image_left_to_right_horizontal()
        elif mode == 3:
            self.image_right_to_left_horizontal()
        elif mode == 4:
            self.image_up_to_down_vertical()
        elif mode == 5:
            self.image_down_to_up_vertical()
        elif mode == 6:
            self.static_text()
        elif mode == 7:
            self.text_sin_left_to_right()
        elif mode == 8:
            self.text_sin_right_to_left()
        elif mode == 9:
            self.text_sin_up_to_down()
        elif mode == 10:
            self.text_sin_down_to_up()
        elif mode == 11:
            self.text_left_to_right_horizontal()
        elif mode == 12:
            self.text_right_to_left_horizontal()
        elif mode == 13:
            self.text_up_to_down_vertical()
        elif mode == 14:
            self.text_down_to_up_vertical()
        elif mode == 15:
            self.text_rebound_left_and_right()
        elif mode == 16:
            self.text_rebound_up_and_down()

def run_datetime_display():
    """Render current date and time centered on the matrix and update every second."""
    # Two-line layout: YYYY-MM-DD on first line, HH:MM:SS on second line.
    group = displayio.Group()

    date_label = adafruit_display_text.label.Label(
        terminalio.FONT, color=0x00FF80, scale=1, text="0000-00-00"
    )
    time_label = adafruit_display_text.label.Label(
        terminalio.FONT, color=0x00FFFF, scale=1, text="00:00:00"
    )

    # Vertical placement around center (y is baseline)
    base_date_y = DISPLAY.height // 2 - 6
    base_time_y = DISPLAY.height // 2 + 10
    date_label.y = base_date_y
    time_label.y = base_time_y

    # Center horizontally based on bounding box width (will be recomputed on updates)
    date_label.x = max(0, (DISPLAY.width - date_label.bounding_box[2]) // 2)
    time_label.x = max(0, (DISPLAY.width - time_label.bounding_box[2]) // 2)

    group.append(date_label)
    group.append(time_label)
    DISPLAY.root_group = group

    last_date = None
    last_sec = None

    # Burn-in prevention state
    shift_dx = 0
    shift_dy = 0
    last_shift = time.monotonic()
    next_saver_at = last_shift + SCREENSAVER_INTERVAL_S

    # Apply initial brightness based on time-of-day
    try:
        h = time.localtime()[3]
        is_night = (h >= NIGHT_DIM_START_HOUR) or (h < NIGHT_DIM_END_HOUR)
        _set_display_brightness(BRIGHTNESS_NIGHT if is_night else BRIGHTNESS_DAY)
    except Exception:
        _set_display_brightness(BRIGHTNESS_DAY)

    # Optional manual brightness cycle via Button B
    _init_buttons()
    brightness_cycle = [0.05, 0.1, 0.2, 0.3, 0.5]
    b_index = 1  # start near night level
    last_b = False
    last_a = False
    while True:
        try:
            now = time.monotonic()
            tm = time.localtime()
            y, mo, d, hh, mm, ss = tm[0], tm[1], tm[2], tm[3], tm[4], tm[5]

            # Night dimming check once per loop (cheap)
            try:
                is_night = (hh >= NIGHT_DIM_START_HOUR) or (hh < NIGHT_DIM_END_HOUR)
                _set_display_brightness(BRIGHTNESS_NIGHT if is_night else BRIGHTNESS_DAY)
            except Exception:
                pass

            date_text = f"{y:04d}-{mo:02d}-{d:02d}"
            if date_text != last_date:
                date_label.text = date_text
                last_date = date_text

            if ss != last_sec:
                time_text = f"{hh:02d}:{mm:02d}:{ss:02d}"
                time_label.text = time_text
                last_sec = ss

            # Re-center based on current text widths
            date_center_x = max(0, (DISPLAY.width - date_label.bounding_box[2]) // 2)
            time_center_x = max(0, (DISPLAY.width - time_label.bounding_box[2]) // 2)

            # Pixel shift update
            if now - last_shift >= PIXEL_SHIFT_INTERVAL_S:
                # choose new small offsets, keeping text on-screen
                shift_dx = random.randint(-PIXEL_SHIFT_RANGE, PIXEL_SHIFT_RANGE)
                shift_dy = random.randint(-PIXEL_SHIFT_RANGE, PIXEL_SHIFT_RANGE)
                last_shift = now

            # Clamp X so labels stay fully visible
            date_w = date_label.bounding_box[2]
            time_w = time_label.bounding_box[2]
            date_x = min(max(0, date_center_x + shift_dx), max(0, DISPLAY.width - date_w))
            time_x = min(max(0, time_center_x + shift_dx), max(0, DISPLAY.width - time_w))

            # Clamp Y for both rows
            date_y = min(max(0, base_date_y + shift_dy), max(0, DISPLAY.height - 8))
            time_y = min(max(0, base_time_y + shift_dy), max(0, DISPLAY.height - 8))

            date_label.x = date_x
            time_label.x = time_x
            date_label.y = date_y
            time_label.y = time_y

            # Periodic screensaver to exercise pixels
            if now >= next_saver_at:
                _run_bouncing_box_screensaver(duration_s=SCREENSAVER_DURATION_S)
                next_saver_at = time.monotonic() + SCREENSAVER_INTERVAL_S

            # Buttons: A -> quick screensaver, B -> toggle brightness
            a_pressed, b_pressed = _buttons_state()
            if a_pressed and not last_a:
                _run_bouncing_box_screensaver(duration_s=10)
            if b_pressed and not last_b:
                b_index = (b_index + 1) % len(brightness_cycle)
                _set_display_brightness(brightness_cycle[b_index])
            last_a, last_b = a_pressed, b_pressed

        except Exception:
            # If time/localtime fails, keep previous display
            pass

        time.sleep(0.1)

def run_marquee_text(text=None, color=0x00FFFF, speed_px_per_sec=30):
    """Simple horizontal scrolling marquee for a single-line message."""
    message = text or _read_text_from_file() or "Hello from Pico!"
    group = displayio.Group()
    label = adafruit_display_text.label.Label(terminalio.FONT, color=color, scale=1, text=message)
    label.y = DISPLAY.height // 2
    group.append(label)
    DISPLAY.root_group = group

    # Start just off the right edge
    x = DISPLAY.width
    last = time.monotonic()
    _init_buttons()
    brightness_cycle = [0.05, 0.1, 0.2, 0.3, 0.5]
    b_index = 1
    while True:
        now = time.monotonic()
        dt = max(0.0, min(0.1, now - last))
        last = now
        dx = max(1, int(speed_px_per_sec * dt))
        x -= dx
        if x < -label.bounding_box[2]:
            x = DISPLAY.width
        label.x = x
        # Quick screensaver on Button A
        a, b = _buttons_state()
        if a:
            _run_bouncing_box_screensaver(8)
        if b:
            b_index = (b_index + 1) % len(brightness_cycle)
            _set_display_brightness(brightness_cycle[b_index])
        time.sleep(0.02)

def run_image_slideshow(folder="images", interval_s=5):
    """Cycle through BMP images in a folder. Shows static images centered.
    The folder should be in the CIRCUITPY root. Non-blocking controls: A -> saver, B -> brighten.
    """
    try:
        files = []
        if folder and (folder in os.listdir(".")):
            for name in os.listdir(folder):
                if name.lower().endswith(".bmp"):
                    files.append("{}/{}".format(folder, name))
        files.sort()
    except Exception:
        files = []

    if not files:
        # Nothing to show; fall back to marquee notice
        run_marquee_text("No BMPs in /{}".format(folder), color=0xFF4040, speed_px_per_sec=20)
        return

    idx = 0
    _init_buttons()
    brightness_cycle = [0.05, 0.1, 0.2, 0.3, 0.5]
    b_index = 1
    while True:
        try:
            path = files[idx % len(files)]
            bmp = displayio.OnDiskBitmap(open(path, "rb"))
            tg = displayio.TileGrid(bmp, pixel_shader=getattr(bmp, 'pixel_shader', displayio.ColorConverter()))
            grp = displayio.Group()
            # Center if image smaller than display
            try:
                tg.x = max(0, (DISPLAY.width - bmp.width) // 2)
                tg.y = max(0, (DISPLAY.height - bmp.height) // 2)
            except Exception:
                pass
            grp.append(tg)
            DISPLAY.root_group = grp

            start = time.monotonic()
            while time.monotonic() - start < max(1, int(interval_s)):
                a, b = _buttons_state()
                if a:
                    _run_bouncing_box_screensaver(8)
                if b:
                    b_index = (b_index + 1) % len(brightness_cycle)
                    _set_display_brightness(brightness_cycle[b_index])
                time.sleep(0.05)
        except Exception:
            # Skip bad image
            pass
        idx += 1

def _run_bouncing_box_screensaver(duration_s=20, box_w=8, box_h=8):
    """Lightweight moving box animation to exercise pixels briefly.
    Swaps the root group temporarily, then restores it.
    """
    try:
        prev_group = DISPLAY.root_group

        # 2-color bitmap (1-bit) for minimal memory use
        bmp = displayio.Bitmap(DISPLAY.width, DISPLAY.height, 2)
        pal = displayio.Palette(2)
        pal[0] = 0x000000
        pal[1] = 0x202020  # dim gray to avoid harsh full-on
        tg = displayio.TileGrid(bmp, pixel_shader=pal)
        saver_group = displayio.Group()
        saver_group.append(tg)

        DISPLAY.root_group = saver_group

        # Utility to draw/erase a box
        def draw_box(x, y, w, h, color_index):
            x0 = max(0, x)
            y0 = max(0, y)
            x1 = min(DISPLAY.width, x + w)
            y1 = min(DISPLAY.height, y + h)
            for yy in range(y0, y1):
                for xx in range(x0, x1):
                    bmp[xx, yy] = color_index

        # Motion state
        x, y = 0, 0
        dx, dy = 1, 1
        end_time = time.monotonic() + max(1, int(duration_s))

        # Temporarily bump brightness a bit to ensure visibility (optional)
        prev_brightness = getattr(DISPLAY, "brightness", None)
        try:
            _set_display_brightness(max(BRIGHTNESS_DAY, BRIGHTNESS_NIGHT))
        except Exception:
            pass

        # Animate
        while time.monotonic() < end_time:
            # Erase previous
            draw_box(x, y, box_w, box_h, 0)
            # Move
            x += dx
            y += dy
            if x <= 0 or x + box_w >= DISPLAY.width:
                dx = -dx
                x += dx
            if y <= 0 or y + box_h >= DISPLAY.height:
                dy = -dy
                y += dy
            # Draw new
            draw_box(x, y, box_w, box_h, 1)
            time.sleep(0.02)  # ~50 FPS max, but sleeps to reduce CPU

        # Restore previous group and brightness
        DISPLAY.root_group = prev_group
        if prev_brightness is not None:
            try:
                DISPLAY.brightness = prev_brightness
            except Exception:
                pass
    except Exception:
        # On any error, do nothing and return control to main display
        try:
            DISPLAY.root_group = prev_group  # type: ignore[name-defined]
        except Exception:
            pass

if __name__ == '__main__':
    # Load optional config
    cfg = load_config("config.json")

    # Override global tunables if provided
    try:
        BRIGHTNESS_DAY = float(cfg.get("brightness_day", BRIGHTNESS_DAY))
        BRIGHTNESS_NIGHT = float(cfg.get("brightness_night", BRIGHTNESS_NIGHT))
        NIGHT_DIM_START_HOUR = int(cfg.get("dim_start_hour", NIGHT_DIM_START_HOUR)) % 24
        NIGHT_DIM_END_HOUR = int(cfg.get("dim_end_hour", NIGHT_DIM_END_HOUR)) % 24
        PIXEL_SHIFT_INTERVAL_S = int(cfg.get("pixel_shift_interval", PIXEL_SHIFT_INTERVAL_S))
        PIXEL_SHIFT_RANGE = int(cfg.get("pixel_shift_range", PIXEL_SHIFT_RANGE))
        SCREENSAVER_INTERVAL_S = int(cfg.get("screensaver_interval", SCREENSAVER_INTERVAL_S))
        SCREENSAVER_DURATION_S = int(cfg.get("screensaver_duration", SCREENSAVER_DURATION_S))
    except Exception:
        pass

    # Try Wi‑Fi connect once at startup (safe no-op on non‑Wi‑Fi boards)
    ok, info = connect_wifi_from_env()
    print("Wi‑Fi connected:" if ok else "Wi‑Fi not connected:", info)

    # Attempt to sync RTC from NTP if enabled
    tz_env = os.getenv("CIRCUITPY_TZ_OFFSET") or os.getenv("TZ_OFFSET")
    tz_offset = None
    try:
        tz_offset = int(float(tz_env)) if tz_env is not None else int(cfg.get("tz_offset", 0))
    except Exception:
        tz_offset = int(cfg.get("tz_offset", 0))
    if cfg.get("enable_ntp", True):
        ok_ntp, ntp_info = sync_datetime_via_ntp(tz_offset_hours=tz_offset)
        print("RTC synced via NTP:" if ok_ntp else "RTC not synced:", ntp_info)

    # Choose mode based on config and presence of message file
    default_mode = str(cfg.get("default_mode", "auto")).lower()
    message_text = cfg.get("marquee_text") or _read_text_from_file()
    if default_mode == "marquee" or (default_mode == "auto" and message_text):
        run_marquee_text(text=message_text or "Hello!", color=cfg.get("marquee_color", 0x00FFFF), speed_px_per_sec=int(cfg.get("marquee_speed", 30)))
    elif default_mode == "slideshow":
        run_image_slideshow(folder=str(cfg.get("image_folder", "images")), interval_s=int(cfg.get("image_interval", 5)))
    else:
        # Fallback to date/time clock
        run_datetime_display()



