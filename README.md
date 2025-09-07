# scratchpad

Test ground for assorted experiments and device scripts.

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

