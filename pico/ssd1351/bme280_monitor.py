# pyright: reportMissingImports=false
"""Minimal BME280 monitor for SSD1351 (Raspberry Pi Pico + CircuitPython)

What it does
- Initializes a 128x128 SSD1351 OLED over SPI (FourWire)
- Reads a BME280 over I2C (default addr 0x76, fallback to 0x77)
- Displays only sensor information: Temperature (C), Humidity (%), Pressure (hPa)
- Burn‑in protection:
  - Black background
  - Text slowly bounces around the screen (like the classic DVD logo)
  - Text color changes occasionally
  - Optionally lowers brightness if the display implements it

Wiring (default pins; adjust if you wired differently)
Pico  -> SSD1351 (SPI)
3V3   -> VCC
GND   -> GND
GP18  -> SCK (CLK)
GP19  -> MOSI (DIN)
(MISO not used)
GP17  -> CS
GP16  -> DC
GP20  -> RST (optional; else tie to 3V3 via pull‑up)

BME280 (I2C)
3V3   -> VIN
GND   -> GND
GP1   -> SCL
GP0   -> SDA

Required libs in CIRCUITPY /lib
- adafruit_ssd1351.mpy
- adafruit_bme280.mpy
- adafruit_ntp.mpy  (for Wi‑Fi NTP time sync on Pico W)
- adafruit_requests.mpy (for HTTP weather fetch)
- adafruit_bus_device/*
- adafruit_display_text/

If missing, download from https://circuitpython.org/libraries

settings.toml (recommended)
    CIRCUITPY_WIFI_SSID = "YourSSID"
    CIRCUITPY_WIFI_PASSWORD = "YourPassword"
    TZ_OFFSET = "-7"            # or "+02:00", "-05:30"; hours offset from UTC
"""

import time
import sys
import random
import os

import board
import displayio
import terminalio

# FourWire location changed in CP9+
try:
    from fourwire import FourWire  # type: ignore
except ImportError:
    try:
        from displayio import FourWire  # type: ignore
    except ImportError:
        FourWire = None  # type: ignore

try:
    # display + text
    from adafruit_display_text import label
except ImportError as e:
    raise RuntimeError("Missing adafruit_display_text library. Copy it to /lib from the bundle.") from e

try:
    import adafruit_ssd1351
except ImportError as e:
    raise RuntimeError("Missing adafruit_ssd1351 library. Copy it to /lib from the bundle.") from e

# Optional: Wi‑Fi + NTP (Pico W or boards with Wi‑Fi)
try:
    import wifi  # type: ignore
    import socketpool  # type: ignore
    import rtc  # type: ignore
    import adafruit_ntp  # type: ignore
except Exception:
    wifi = None  # type: ignore
    socketpool = None  # type: ignore
    rtc = None  # type: ignore
    adafruit_ntp = None  # type: ignore

# Optional: HTTP client for weather (requires Wi‑Fi)
try:
    import ssl  # type: ignore
    import adafruit_requests  # type: ignore
except Exception:
    ssl = None  # type: ignore
    adafruit_requests = None  # type: ignore

# Optional: BME280 environmental sensor (I2C)
try:
    import adafruit_bme280  # type: ignore
except ImportError:
    adafruit_bme280 = None  # type: ignore
    print("BME280 library not found; sensor disabled.", file=sys.stderr)

# Resolve BME280 class names across possible layouts
try:
    from adafruit_bme280 import Adafruit_BME280_I2C as BME280_I2C  # type: ignore
except Exception:
    try:
        from adafruit_bme280.advanced import Adafruit_BME280_I2C as BME280_I2C  # type: ignore
    except Exception:
        try:
            from adafruit_bme280.basic import Adafruit_BME280_I2C as BME280_I2C  # type: ignore
        except Exception:
            BME280_I2C = None  # type: ignore


# ----- Configuration -----
DISPLAY_WIDTH = 128
DISPLAY_HEIGHT = 128
ROTATION = 90  # 0/90/180/270
SPI_BAUD = 24_000_000

# SSD1351 pins
PIN_CS = board.GP17
PIN_DC = board.GP16
PIN_RST = board.GP20

# BME280 (I2C)
BME280_ENABLED = True
BME280_I2C_FREQ = 100_000
BME280_ADDR = 0x76  # common: 0x76 or 0x77
BME280_SAMPLE_INTERVAL_S = 1.0

# Burn-in protection tuning
MOVE_INTERVAL_S = 0.03   # movement tick (lower = smoother; higher = fewer refreshes)
COLOR_CHANGE_EVERY_S = 30
SPEED_PX_PER_TICK = 1
MARGIN = 2
DIM_BRIGHTNESS = 0.6  # if display supports .brightness

# Network & time
WIFI_ENABLED = True
NTP_ENABLED = True
NTP_SERVER = "pool.ntp.org"
TIMEZONE_OFFSET = 0  # hours offset from UTC (e.g., -7, +1, etc.)
WIFI_CONNECT_TIMEOUT_S = 20
TIME_UPDATE_INTERVAL_S = 1.0

# Weather (Singapore)
WEATHER_ENABLED = True
WEATHER_PROVIDER = "open-meteo"  # currently only open-meteo is implemented
WEATHER_UPDATE_INTERVAL_S = 600.0  # 10 minutes
SG_LAT = 1.3521
SG_LON = 103.8198

# Debug to USB serial
DEBUG = True


def make_display():
    displayio.release_displays()
    try:
        spi = board.SPI()
    except AttributeError:
        import busio  # type: ignore
        spi = busio.SPI(clock=board.GP18, MOSI=board.GP19)  # MISO not needed

    # Best-effort SPI config
    if hasattr(spi, "try_lock"):
        while not spi.try_lock():
            pass
        try:
            if hasattr(spi, "configure"):
                spi.configure(baudrate=SPI_BAUD, phase=0, polarity=0)
        finally:
            spi.unlock()

    if FourWire is None:
        raise RuntimeError("FourWire interface not available: update CircuitPython build.")

    bus = FourWire(spi, command=PIN_DC, chip_select=PIN_CS, reset=PIN_RST, baudrate=SPI_BAUD)
    disp = adafruit_ssd1351.SSD1351(bus, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, rotation=ROTATION)

    # Lower brightness if supported (helps longevity)
    if hasattr(disp, "brightness"):
        try:
            disp.brightness = DIM_BRIGHTNESS  # type: ignore[attr-defined]
        except Exception:
            pass
    return disp


display = make_display()

# Root group
root = displayio.Group()
try:
    display.root_group = root
except AttributeError:
    display.show(root)

# Background: solid black to minimize lit pixels
bg_palette = displayio.Palette(1)
bg_palette[0] = 0x000000
bg_bitmap = displayio.Bitmap(DISPLAY_WIDTH, DISPLAY_HEIGHT, 1)
root.append(displayio.TileGrid(bg_bitmap, pixel_shader=bg_palette))

# Foreground group that we move for burn‑in protection
fg = displayio.Group(x=0, y=0)
root.append(fg)

# Sensor label (multiline for T/H/P)
sensor_label = label.Label(
    terminalio.FONT,
    text="T: --.- C\nH: --.- %\nP: ----.- hPa",
    color=0x00FFAA,
    x=0,
    y=12,
    line_spacing=1.0,
)
fg.append(sensor_label)

# Date/Time label (updated from RTC, set via NTP if available)
time_label = label.Label(
    terminalio.FONT,
    text="YYYY-MM-DD HH:MM:SS",
    color=0x00FFAA,
    x=0,
    y=52,
)
fg.append(time_label)

# Weather label (Singapore current conditions via Open‑Meteo)
weather_label = label.Label(
    terminalio.FONT,
    text="SG Wx:\nT: --.- C\nH: ---%\n--",
    color=0x00FFAA,
    x=0,
    y=92,
    line_spacing=1.0,
)
fg.append(weather_label)


# ----- Wi‑Fi + NTP helpers -----

def getenv(key, default=None):
    try:
        return os.getenv(key, default)
    except Exception:
        return default


def get_wifi_credentials():
    """Fetch Wi‑Fi credentials from settings.toml env vars or secrets.py.

    Preferred (CircuitPython 8+): settings.toml
      CIRCUITPY_WIFI_SSID = "..."
      CIRCUITPY_WIFI_PASSWORD = "..."
    Fallback: secrets.py with dict {"ssid": ..., "password": ...}
    """
    ssid = getenv("CIRCUITPY_WIFI_SSID")
    password = getenv("CIRCUITPY_WIFI_PASSWORD")
    if ssid and password:
        return ssid, password
    # Fallback to secrets.py if present
    try:
        import secrets  # type: ignore

        # Expect typical CircuitPython secrets.py containing a dict named 'secrets'
        if hasattr(secrets, "secrets"):
            s = getattr(secrets, "secrets")  # type: ignore[attr-defined]
            try:
                ssid = s.get("ssid") if hasattr(s, "get") else s["ssid"]
                password = s.get("password") if hasattr(s, "get") else s["password"]
                return ssid, password
            except Exception:
                pass
        # Fallback: attributes on module (less common)
        try:
            ssid = getattr(secrets, "ssid")
            password = getattr(secrets, "password")
            if ssid and password:
                return ssid, password
        except Exception:
            pass
        return None, None
    except Exception:
        return None, None


def connect_wifi():
    if not WIFI_ENABLED or wifi is None:
        if DEBUG:
            print("Wi‑Fi not available or disabled; skipping connect")
        return False
    ssid, password = get_wifi_credentials()
    if not ssid or not password:
        if DEBUG:
            print("Wi‑Fi credentials missing (set CIRCUITPY_WIFI_SSID/PASSWORD in settings.toml)")
        return False
    try:
        if DEBUG:
            print(f"Connecting to Wi‑Fi SSID '{ssid}' ...")
        t0 = time.monotonic()
        try:
            if hasattr(wifi.radio, "connect"):
                wifi.radio.connect(ssid, password)  # type: ignore[attr-defined]
        except Exception as e:
            if DEBUG:
                print(f"Wi‑Fi connect error: {e!r}")
            return False
        # Wait for IP or timeout
        while (time.monotonic() - t0) < WIFI_CONNECT_TIMEOUT_S:
            try:
                ip = getattr(wifi.radio, "ipv4_address", None)
                if ip:
                    if DEBUG:
                        print("Wi‑Fi connected, IP:", ip)
                    return True
            except Exception:
                pass
            time.sleep(0.25)
    except Exception as e:
        if DEBUG:
            print(f"Wi‑Fi setup failed: {e!r}")
    return False


def sync_time_ntp():
    if not NTP_ENABLED or adafruit_ntp is None or wifi is None or socketpool is None or rtc is None:
        if DEBUG:
            print("NTP not available or disabled; skipping time sync")
        return False
    try:
        pool = socketpool.SocketPool(wifi.radio)  # type: ignore[arg-type]
        ntp = adafruit_ntp.NTP(pool, server=NTP_SERVER, tz_offset=TIMEZONE_OFFSET)  # type: ignore[call-arg]
        r = rtc.RTC()
        r.datetime = ntp.datetime  # type: ignore[assignment]
        if DEBUG:
            try:
                now = time.localtime()
                print(
                    "NTP time set:",
                    "{0:04d}-{1:02d}-{2:02d} {3:02d}:{4:02d}:{5:02d}".format(
                        now[0], now[1], now[2], now[3], now[4], now[5]
                    ),
                )
            except Exception:
                print("NTP time set")
        return True
    except Exception as e:
        if DEBUG:
            print(f"NTP sync failed: {e!r}")
        return False


# ----- Weather helpers (Open‑Meteo) -----

_requests_session = None


def _ensure_requests_session():
    global _requests_session
    if _requests_session is not None:
        return _requests_session
    if wifi is None or socketpool is None or adafruit_requests is None or ssl is None:
        if DEBUG:
            missing = []
            if wifi is None:
                missing.append("wifi")
            if socketpool is None:
                missing.append("socketpool")
            if adafruit_requests is None:
                missing.append("adafruit_requests")
            if ssl is None:
                missing.append("ssl")
            print("HTTP session prerequisites missing:", ", ".join(missing))
        return None
    try:
        pool = socketpool.SocketPool(wifi.radio)  # type: ignore[arg-type]
        ctx = ssl.create_default_context()
        _requests_session = adafruit_requests.Session(pool, ctx)  # type: ignore[call-arg]
        if DEBUG:
            print("HTTP session initialized")
        return _requests_session
    except Exception as e:
        if DEBUG:
            print(f"HTTP session init failed: {e!r}")
        return None


def _wmo_code_to_text(code):
    # Minimal Open‑Meteo WMO weather code mapping
    try:
        c = int(code)
    except Exception:
        return "--"
    if c == 0:
        return "Clear"
    if c in (1, 2, 3):
        return "Cloudy"
    if c in (45, 48):
        return "Fog"
    if c in (51, 53, 55, 56, 57):
        return "Drizzle"
    if c in (61, 63, 65, 66, 67):
        return "Rain"
    if c in (71, 73, 75, 77):
        return "Snow"
    if c in (80, 81, 82):
        return "Showers"
    if c in (85, 86):
        return "SnowShw"
    if c in (95, 96, 99):
        return "Storm"
    return str(c)


def fetch_sg_weather():
    if not WEATHER_ENABLED or WEATHER_PROVIDER != "open-meteo":
        return None
    if wifi is None:
        if DEBUG:
            print("Weather fetch skipped: wifi module not available")
        return None
    sess = _ensure_requests_session()
    if sess is None:
        if DEBUG:
            print("Weather fetch skipped: HTTP session unavailable")
        return None
    try:
        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={SG_LAT:.4f}&longitude={SG_LON:.4f}"
            "&current=temperature_2m,relative_humidity_2m,weather_code"
            "&timezone=Asia%2FSingapore"
        )
        if DEBUG:
            ip = None
            try:
                ip = getattr(wifi.radio, "ipv4_address", None)
            except Exception:
                pass
            print("Fetching SG weather...", ip)
            print("URL:", url)
        resp = sess.get(url, timeout=8)  # type: ignore[attr-defined]
        try:
            status = getattr(resp, "status_code", None)
            if DEBUG:
                print("HTTP status:", status)
            data = resp.json()
        finally:
            try:
                resp.close()
            except Exception:
                pass
        if not isinstance(data, dict):
            if DEBUG:
                print("Weather JSON not a dict; type:", type(data))
            return None
        if "current" not in data:
            if DEBUG:
                print("Weather JSON missing 'current'; keys:", list(data.keys()))
            return None
        cur = data.get("current") or {}
        t = cur.get("temperature_2m")
        rh = cur.get("relative_humidity_2m")
        wc = cur.get("weather_code")
        if DEBUG and (t is None or rh is None or wc is None):
            print("Weather current fields:", {"temperature_2m": t, "relative_humidity_2m": rh, "weather_code": wc})
        return {
            "temperature": t,
            "humidity": rh,
            "wtext": _wmo_code_to_text(wc),
        }
    except Exception as e:
        if DEBUG:
            print(f"Weather fetch failed: {e!r}")
        return None


def parse_tz_offset(val):
    """Parse TZ offset strings like "-7", "+02", "+05:30", "-03:45" to float hours.
    Returns None if parsing fails.
    """
    try:
        if val is None:
            return None
        s = str(val).strip()
        if not s:
            return None
        sign = 1
        if s[0] == "+":
            s = s[1:]
        elif s[0] == "-":
            sign = -1
            s = s[1:]
        if ":" in s:
            parts = s.split(":")
            h = int(parts[0] or "0")
            m = int(parts[1] or "0")
            offset = sign * (h + (m / 60.0))
            return offset
        # plain number (int or float)
        offset = float(s)
        return sign * offset
    except Exception:
        return None


# Load TZ offset from settings.toml if provided
_tz_env = getenv("CIRCUITPY_TZ_OFFSET")
_tz_val = parse_tz_offset(_tz_env)
if _tz_val is not None:
    TIMEZONE_OFFSET = _tz_val
    if DEBUG:
        print("Using TZ_OFFSET from settings:", _tz_val)


# Attempt Wi‑Fi + NTP once at startup (non‑fatal)
wifi_ok = connect_wifi()
if wifi_ok:
    sync_time_ntp()


# ----- BME280 init -----

def init_bme280():
    if not BME280_ENABLED or adafruit_bme280 is None or BME280_I2C is None:
        if DEBUG:
            print("BME280: disabled or library unavailable")
        return None, None
    try:
        import busio  # type: ignore
    except ImportError as e:
        if DEBUG:
            print(f"BME280: busio missing -> {e!r}")
        return None, None

    # Try common pin pairs in order
    candidates = [
        (getattr(board, "SCL", None), getattr(board, "SDA", None)),
        (getattr(board, "GP1", None), getattr(board, "GP0", None)),  # I2C0
        (getattr(board, "GP3", None), getattr(board, "GP2", None)),  # I2C1
    ]
    for scl, sda in candidates:
        if scl is None or sda is None:
            continue
        try:
            i2c = busio.I2C(scl, sda, frequency=BME280_I2C_FREQ)  # type: ignore
            # Optional scan for debug
            try:
                if hasattr(i2c, "try_lock"):
                    while not i2c.try_lock():
                        pass
                    try:
                        found = getattr(i2c, "scan", lambda: [])()
                        if DEBUG:
                            print("I2C scan:", [f"0x{a:02X}" for a in found])
                    finally:
                        i2c.unlock()
            except Exception:
                pass

            # Try 0x76 then 0x77
            for addr in (BME280_ADDR, 0x77 if BME280_ADDR != 0x77 else 0x76):
                try:
                    sensor = BME280_I2C(i2c, address=addr)  # type: ignore
                    try:
                        sensor.sea_level_pressure = 1013.25
                    except Exception:
                        pass
                    if DEBUG:
                        print(f"BME280: initialized at 0x{addr:02X}")
                    return sensor, i2c
                except Exception as e:
                    if DEBUG:
                        print(f"BME280 probe 0x{addr:02X} failed: {e!r}")
        except Exception as e:
            if DEBUG:
                print(f"BME280 I2C failed on pins {scl!r},{sda!r}: {e!r}")
            continue
    if DEBUG:
        print("BME280: not found")
    return None, None


bme, i2c_bus = init_bme280()


# ----- Burn-in protection helpers -----

COLORS = [
    0x00FFAA, 0x66FF66, 0xFFFF00, 0xFFAA00, 0xFF66CC, 0xAAAAFF, 0x00DDFF, 0xFFFFFF
]

# start somewhere not in the corner
fg.x, fg.y = 10, 18
vx, vy = SPEED_PX_PER_TICK, SPEED_PX_PER_TICK
last_move = time.monotonic()
last_color_change = time.monotonic()
last_sample = 0.0
last_time_update = 0.0
last_weather_update = 0.0
frames = 0


def label_bounds(lb):
    try:
        x, y, w, h = lb.bounding_box
        return w, h
    except Exception:
        # fallback guess
        return max(32, len(lb.text) * 6), 12


def group_bounds(grp):
    """Compute union bounds of labels inside a group.
    Returns (width, height) considering each child's x/y offset.
    """
    max_w = 0
    max_h = 0
    try:
        for child in grp:
            # Only consider Label-like nodes
            if hasattr(child, "bounding_box"):
                try:
                    x, y, w, h = child.bounding_box
                    # Offset by the child's position within the group
                    cx = getattr(child, "x", 0)
                    cy = getattr(child, "y", 0)
                    x += cx
                    y += cy
                except Exception:
                    w, h = label_bounds(child)
                    x = getattr(child, "x", 0)
                    y = getattr(child, "y", 0)
                max_w = max(max_w, x + w)
                max_h = max(max_h, y + h)
    except Exception:
        # Fallback to sensor_label only
        w, h = label_bounds(sensor_label)
        max_w, max_h = w, h
    return max_w, max_h


def clamp_group_within_display(grp, margin=MARGIN):
    """Clamp a group's x/y so its bounding box stays within display bounds.

    Safe to call after any text change that can alter layout size.
    """
    try:
        w, h = group_bounds(grp)
        max_x = max(margin, DISPLAY_WIDTH - w - margin)
        max_y = max(margin, DISPLAY_HEIGHT - h - margin)
        new_x = grp.x
        new_y = grp.y
        if new_x < margin:
            new_x = margin
        elif new_x > max_x:
            new_x = max_x
        if new_y < margin:
            new_y = margin
        elif new_y > max_y:
            new_y = max_y
        if new_x != grp.x or new_y != grp.y:
            grp.x = new_x
            grp.y = new_y
            if DEBUG:
                try:
                    print("Clamped group pos:", new_x, new_y, "size:", (w, h))
                except Exception:
                    pass
    except Exception:
        pass

# Compactly stack labels vertically with a small gap and clamp the group.
def _label_size(lb):
    try:
        _, _, w, h = lb.bounding_box
        return w, h
    except Exception:
        # Fallback guess for TerminalIO font
        return max(6, 6 * len(getattr(lb, "text", ""))), 12


def relayout_labels(vgap=6):
    try:
        # Keep sensor_label at its current y; position others below it
        _, sh = _label_size(sensor_label)
        time_label.y = sensor_label.y + sh + vgap
        _, th = _label_size(time_label)
        weather_label.y = time_label.y + th + vgap
    except Exception:
        pass
    # Ensure the moving group remains in-bounds after relayout
    clamp_group_within_display(fg)

# Ensure initial layout starts in-bounds before entering loop
relayout_labels()


print("Starting BME280 monitor (burn‑in protected)")

while True:
    now = time.monotonic()

    # Sample sensor at interval
    if bme and (now - last_sample) >= BME280_SAMPLE_INTERVAL_S:
        try:
            T = float(getattr(bme, "temperature"))
            H = float(getattr(bme, "humidity"))
            P = float(getattr(bme, "pressure"))
            sensor_label.text = "T: {0:4.1f} C\nH: {1:4.1f} %\nP: {2:6.1f} hPa".format(T, H, P)
            relayout_labels()
        except Exception as e:
            if DEBUG:
                print(f"BME280 read error: {e!r}")
            sensor_label.text = "Sensor\nread\nerror"
            relayout_labels()
        last_sample = now
    elif bme is None:
        sensor_label.text = "BME280\nnot found\n--"
        relayout_labels()

    # Update date/time label from RTC every second (if RTC present)
    if (now - last_time_update) >= TIME_UPDATE_INTERVAL_S:
        try:
            t = time.localtime()
            # t: (year, mon, mday, hour, min, sec, wday, yday, isdst)
            time_label.text = (
                "{0:04d}-{1:02d}-{2:02d} {3:02d}:{4:02d}:{5:02d}".format(
                    t[0], t[1], t[2], t[3], t[4], t[5]
                )
            )
        except Exception:
            # If RTC not set or not available, keep placeholder
            pass
        last_time_update = now
        # Time string length can change; relayout and clamp
        relayout_labels()

    # Update SG weather occasionally (retry Wi‑Fi if needed)
    if WEATHER_ENABLED and (now - last_weather_update) >= WEATHER_UPDATE_INTERVAL_S:
        if not wifi_ok and WIFI_ENABLED:
            wifi_ok = connect_wifi()
            if wifi_ok and NTP_ENABLED:
                sync_time_ntp()
        if not wifi_ok:
            last_weather_update = now
            # Don't spam attempts; will retry next interval
            if DEBUG:
                print("Skip SG weather: Wi‑Fi not connected")
            continue
        w = fetch_sg_weather()
        if isinstance(w, dict) and (w.get("temperature") is not None):
            try:
                # w.get returns Unknown to the type checker; ignore type to allow runtime cast
                t = float(w.get("temperature"))  # type: ignore[arg-type]
                rh = w.get("humidity")
                rh_s = f"{int(rh)}%" if isinstance(rh, (int, float)) else "--%"
                wt = w.get("wtext") or "--"
                # Multi-line weather: compact to keep width small
                weather_label.text = "SG Wx:\nT: {0:4.1f} C\nH: {1:>3}\n{2}".format(t, rh_s, wt)
                relayout_labels()
            except Exception:
                weather_label.text = "SG Wx:\nT: --.- C\nH: ---%\n--"
                relayout_labels()
        else:
            # Keep previous, but hint offline once
            if DEBUG:
                print("SG weather unavailable; fetch result:", w)
        last_weather_update = now

    # Move the foreground group to prevent burn‑in
    if (now - last_move) >= MOVE_INTERVAL_S:
        w, h = group_bounds(fg)
        # Compute bounds with margin
        max_x = DISPLAY_WIDTH - w - MARGIN
        max_y = DISPLAY_HEIGHT - h - MARGIN
        # Bounce
        new_x = fg.x + vx
        new_y = fg.y + vy
        if new_x < MARGIN:
            new_x = MARGIN
            vx = abs(vx)
        elif new_x > max_x:
            new_x = max_x
            vx = -abs(vx)
        if new_y < MARGIN:
            new_y = MARGIN
            vy = abs(vy)
        elif new_y > max_y:
            new_y = max_y
            vy = -abs(vy)
        fg.x, fg.y = new_x, new_y
        last_move = now

    # Occasionally change color to vary lit pixels
    if (now - last_color_change) >= COLOR_CHANGE_EVERY_S:
        try:
            c = random.choice(COLORS)
            sensor_label.color = c
            time_label.color = c
            weather_label.color = c
        except Exception:
            pass
        last_color_change = now

    # Tiny sleep to yield USB & reduce refreshes
    time.sleep(1)

