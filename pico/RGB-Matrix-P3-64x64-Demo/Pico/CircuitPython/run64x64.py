import board
import displayio
import framebufferio
import rgbmatrix
from digitalio import DigitalInOut,Direction
import adafruit_display_text.label
import terminalio
from adafruit_bitmap_font import bitmap_font
import time
from math import sin
import os

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
    date_label.y = DISPLAY.height // 2 - 6
    time_label.y = DISPLAY.height // 2 + 10

    # Center horizontally based on bounding box width
    date_label.x = max(0, (DISPLAY.width - date_label.bounding_box[2]) // 2)
    time_label.x = max(0, (DISPLAY.width - time_label.bounding_box[2]) // 2)

    group.append(date_label)
    group.append(time_label)
    DISPLAY.root_group = group

    last_date = None
    last_sec = None
    while True:
        try:
            tm = time.localtime()
            y, mo, d, hh, mm, ss = tm[0], tm[1], tm[2], tm[3], tm[4], tm[5]

            date_text = f"{y:04d}-{mo:02d}-{d:02d}"
            if date_text != last_date:
                date_label.text = date_text
                date_label.x = max(0, (DISPLAY.width - date_label.bounding_box[2]) // 2)
                last_date = date_text

            if ss != last_sec:
                time_text = f"{hh:02d}:{mm:02d}:{ss:02d}"
                time_label.text = time_text
                time_label.x = max(0, (DISPLAY.width - time_label.bounding_box[2]) // 2)
                last_sec = ss
        except Exception:
            # If time/localtime fails, keep previous display
            pass

        time.sleep(0.1)

if __name__ == '__main__':
    # Try Wi‑Fi connect once at startup (safe no-op on non‑Wi‑Fi boards)
    ok, info = connect_wifi_from_env()
    if ok:
        print("Wi‑Fi connected:", info)
    else:
        print("Wi‑Fi not connected:", info)

    # Attempt to sync RTC from NTP if Wi‑Fi available. Optional TZ offset via env:
    # CIRCUITPY_TZ_OFFSET or TZ_OFFSET (hours, e.g., -7 for PDT)
    tz_env = os.getenv("CIRCUITPY_TZ_OFFSET") or os.getenv("TZ_OFFSET")
    try:
        tz_offset = float(tz_env) if tz_env is not None else 0.0
    except Exception:
        tz_offset = 0.0
    ok_ntp, ntp_info = sync_datetime_via_ntp(tz_offset_hours=int(tz_offset))
    if ok_ntp:
        print("RTC synced via NTP:", ntp_info)
    else:
        print("RTC not synced:", ntp_info)

    # Run the date/time display instead of demo test modes
    run_datetime_display()



