# scratchpad

Test ground for assorted experiments and device scripts.

## SSD1351 OLED Monitor + BME280 (Pico, CircuitPython)

The file `pico/ssd1351/monitor.py` drives a 128×128 SSD1351 OLED over SPI and shows a demo UI with shapes, a moving sprite, FPS, and optional BME280 environmental data. It includes a simple on‑screen menu (buttons on GP14/GP15).

### Wiring

SSD1351 (SPI0):
- VCC -> 3V3
- GND -> GND
- SCK (CLK) -> GP18
- MOSI (DIN) -> GP19
- CS -> GP17
- DC -> GP16
- RST -> GP20 (or tie to RUN/3V3 with pull‑up)

BME280 (SPI1):
- VIN -> 3V3
- GND -> GND
- SCK -> GP10
- MOSI -> GP11
- MISO -> GP12
- CS -> GP13

Buttons (optional):
- Next -> GP14 to GND (internal pull‑up)
- Select -> GP15 to GND (internal pull‑up)

Note: Using separate SPI buses avoids conflicts with the display.

### Required libraries on CIRCUITPY/lib

- adafruit_ssd1351.mpy
- adafruit_bme280.mpy
- adafruit_bus_device/ (folder)
- adafruit_display_text/
- adafruit_display_shapes/

Use the matching CircuitPython Library Bundle for your board/firmware version.

### Configuration

Configuration constants are at the top of `monitor.py`:
- `BME280_USE_SPI = True` (default). If you prefer I2C, set to `False` and wire to SDA/SCL.
- SPI1 pins for BME280: `BME280_SCK_PIN=GP10`, `BME280_MOSI_PIN=GP11`, `BME280_MISO_PIN=GP12`, `BME280_CS_PIN=GP13`.
- `BME280_SPI_BAUDRATE = 2_000_000`.
- If using I2C, set `BME280_ADDRESS` (0x76 or 0x77) and optionally `BME280_I2C_FREQUENCY`.
- `BME280_SAMPLE_INTERVAL_S` controls sensor update rate.

### Usage

1) Copy `pico/ssd1351/monitor.py` to the CIRCUITPY drive and rename it to `code.py` (or run as `monitor.py` from another `code.py`).
2) Copy the required libraries to `/lib` on CIRCUITPY.
3) Reset the Pico.

On screen:
- Demo shapes and sprite animate; FPS shown at bottom right.
- If BME280 is detected, a cyan line shows `T:xx.xC H:yy.y% P:zzzz.zhPa`.
- Buttons: Next (GP14) cycles menu items; Select (GP15) activates. You can toggle Shapes, Sprite, Info, Sensor, and cycle background modes.

### Troubleshooting

- If sensor reads `Sensor: error` or `--`, check wiring and CS pin, and ensure `adafruit_bme280.mpy` is installed.
- If your BME280 uses I2C only, set `BME280_USE_SPI = False` and wire to `SDA`/`SCL`; set `BME280_ADDRESS` accordingly.
- If the display doesn’t show anything, verify SPI0 pins and that `adafruit_ssd1351.mpy` is installed.
- VS Code lint warnings about `board`/`displayio` are expected on desktop—they resolve on-device.

## RGB 64x64 Matrix (CircuitPython)

The file `pico/RGB-Matrix-P3-64x64-Demo/Pico/CircuitPython/run64x64.py` drives a 64×64 RGB LED matrix from a Raspberry Pi Pico using CircuitPython.

It includes several modes:

- Date/Time clock with night dimming and pixel shift
- Marquee text (from `message.txt` or config)
- Image slideshow (BMPs in `/images`)
- MQTT environment display (T/P/H)
- Combined Date/Time + MQTT display (new)

### Configure via config.json

Create `config.json` on the CIRCUITPY drive to choose the default mode and tweak behavior. Example:

```json
{
	"default_mode": "both",
	"enable_ntp": true,
	"tz_offset": 0,
	"brightness_day": 0.3,
	"brightness_night": 0.1,
	"dim_start_hour": 18,
	"dim_end_hour": 7,
	"pixel_shift_interval": 15,
	"pixel_shift_range": 24,
	"screensaver_interval": 600,
	"screensaver_duration": 30
}
```

Supported `default_mode` values:

- `auto` (marquee if `message.txt` exists, else clock)
- `marquee`
- `slideshow`
- `env`, `mqtt`, `mqtt_env` (MQTT T/P/H only)
- `clock_env`, `datetime_env`, `clock_mqtt`, `datetime_mqtt`, `both` (combined Date/Time + MQTT)

### Wi‑Fi and NTP

Place Wi‑Fi credentials in `settings.toml` on the CIRCUITPY drive:

```
CIRCUITPY_WIFI_SSID="your-ssid"
CIRCUITPY_WIFI_PASSWORD="your-password"
```

NTP time sync is attempted on boot when `enable_ntp` is true. Optional `tz_offset` can shift hours from UTC.

### MQTT settings

Set MQTT broker settings as environment variables in `settings.toml` as well (CircuitPython exposes them via `os.getenv`):

```
MQTT_BROKER="test.mosquitto.org"
MQTT_PORT="1883"     # 8883 for TLS
MQTT_TLS="false"
MQTT_USERNAME=""
MQTT_PASSWORD=""
```

The program subscribes to these topics:

- `temperature`
- `pressure`
- `humidity`

Publish numeric values to see updates on the display.

### Buttons and burn‑in prevention

- Button A (GP14): start a short screensaver (moving box)
- Button B (GP15): cycle brightness levels
- Pixel shifting, night dimming, and periodic screensaver help reduce burn‑in.

