"""SSD1351 Demo for Raspberry Pi Pico (CircuitPython)

Features:
  * Initializes 128x128 SSD1351 OLED over SPI (FourWire)
  * Renders: gradient background, shapes, moving sprite, dynamic text (FPS & sensor placeholder)
  * Shows how to update portions of the screen efficiently

Wiring (default pin choices below – adjust if you wired differently):
  Pico  -> SSD1351
  3V3   -> VCC
  GND   -> GND
  GP18  -> SCK (CLK)
  GP19  -> MOSI (DIN)
  (MISO not used)
  GP17  -> CS
  GP16  -> DC
  GP20  -> RST (optional, else tie to run / 3V3 with pull-up)
  3V3   -> VIN / VCC

	BME280 (I2C):
	Pico  -> BME280
	3V3   -> VIN
	GND   -> GND
	SCL   -> SCL (default board.SCL)
	SDA   -> SDA (default board.SDA)

	# If you prefer SPI (requires SCK, MOSI, MISO, CS), set BME280_USE_SPI=True in config below.

Required libraries in /lib on CIRCUITPY drive:
  adafruit_ssd1351.mpy
	adafruit_bme280.mpy   (optional – for BME280 sensor)
  adafruit_bus_device/* (folder)
  adafruit_display_text/
  adafruit_display_shapes/

If you don't have them, download the matching CircuitPython bundle:
  https://circuitpython.org/libraries

You can trim features you don't need to save RAM / flash.
"""

import time
import sys
import board
import displayio
import terminalio
from math import sin, pi
from digitalio import DigitalInOut, Direction, Pull

# CircuitPython 9+: FourWire moved to 'fourwire'. Add compatibility layer.
try:
	from fourwire import FourWire  # type: ignore
except ImportError:
	try:
		from displayio import FourWire  # type: ignore
	except ImportError:
		FourWire = None  # type: ignore

try:
	# Shapes & text helpers
	from adafruit_display_text import label
	from adafruit_display_shapes.rect import Rect
	from adafruit_display_shapes.circle import Circle
except ImportError:  # Graceful fallback if shapes libs missing
	label = None  # type: ignore
	Rect = None  # type: ignore
	Circle = None  # type: ignore

try:
	import adafruit_ssd1351
except ImportError as e:  # Provide a clear runtime hint on the device
	raise RuntimeError("Missing adafruit_ssd1351 library. Copy it to /lib from the bundle.") from e

# Optional: BME280 environmental sensor (I2C)
try:
	import adafruit_bme280  # type: ignore
except ImportError:
	adafruit_bme280 = None  # type: ignore
	print("BME280 library not found; sensor disabled.", file=sys.stderr)

# Resolve BME280 class names across versions/layouts
try:
	# Most common: single-file module exposes classes at top level
	from adafruit_bme280 import Adafruit_BME280_I2C as BME280_I2C, Adafruit_BME280_SPI as BME280_SPI  # type: ignore
except Exception:
	try:
		# Newer split-package layouts
		from adafruit_bme280.advanced import Adafruit_BME280_I2C as BME280_I2C, Adafruit_BME280_SPI as BME280_SPI  # type: ignore
	except Exception:
		try:
			from adafruit_bme280.basic import Adafruit_BME280_I2C as BME280_I2C, Adafruit_BME280_SPI as BME280_SPI  # type: ignore
		except Exception:
			BME280_I2C = None  # type: ignore
			BME280_SPI = None  # type: ignore


# --------- Configuration (edit to match your wiring) ---------
PIN_CS = board.GP17
PIN_DC = board.GP16
PIN_RST = board.GP20  # Set to None if you hard-wired reset

DISPLAY_WIDTH = 128
DISPLAY_HEIGHT = 128
ROTATION = 90  # 0, 90, 180, 270
BAUDRATE = 24_000_000  # You can reduce if you see noise / instability

# Optional buttons: wire momentary buttons from pins to GND; internal pull-ups enabled
BTN_NEXT_PIN = getattr(board, "GP14", None)
BTN_SELECT_PIN = getattr(board, "GP15", None)

# Optional BME280 configuration (I2C by default)
BME280_ENABLED = True
BME280_USE_SPI = False  # use I2C since only SCL/SDA are wired
BME280_ADDRESS = 0x76  # default I2C address; common modules use 0x76 or 0x77
BME280_I2C_FREQUENCY = 100_000
BME280_SAMPLE_INTERVAL_S = 1.0

# SPI pin assignments for BME280 (used only if BME280_USE_SPI=True)
BME280_SCK_PIN = getattr(board, "GP10", None)
BME280_MOSI_PIN = getattr(board, "GP11", None)
BME280_MISO_PIN = getattr(board, "GP12", None)
BME280_CS_PIN = getattr(board, "GP13", None)
BME280_SPI_BAUDRATE = 2_000_000

# Debug: print sensor readings to USB serial console
DEBUG_SENSOR = True

# Optional: I2C pin overrides if you didn't use the board default SCL/SDA
BME280_I2C_SCL_PIN = getattr(board, "SCL", None)
BME280_I2C_SDA_PIN = getattr(board, "SDA", None)


def make_display():
	"""Initialize & return the SSD1351 display object.

	Falls back to busio.SPI if board.SPI() is not present (older CircuitPython builds).
	If you're actually running MicroPython, this file won't work as-is (no displayio); flash
	CircuitPython or request a MicroPython adaptation.
	"""
	displayio.release_displays()

	try:
		spi = board.SPI()
	except AttributeError:
		try:
			import busio  # type: ignore
		except ImportError as e:
			raise RuntimeError("SPI not available: need CircuitPython or busio module.") from e
		spi = busio.SPI(clock=board.GP18, MOSI=board.GP19)  # MISO not needed

	if hasattr(spi, "try_lock"):
		while not spi.try_lock():
			pass
		try:
			if hasattr(spi, "configure"):
				spi.configure(baudrate=BAUDRATE, phase=0, polarity=0)
		finally:
			spi.unlock()

	if FourWire is None:
		raise RuntimeError("FourWire interface not available: update CircuitPython build.")

	display_bus = FourWire(
		spi,
		command=PIN_DC,
		chip_select=PIN_CS,
		reset=PIN_RST,
		baudrate=BAUDRATE,
	)
	return adafruit_ssd1351.SSD1351(
		display_bus,
		width=DISPLAY_WIDTH,
		height=DISPLAY_HEIGHT,
		rotation=ROTATION,
	)


display = make_display()

# Root group shown on display
main_group = displayio.Group()
try:
	display.root_group = main_group
except AttributeError:
	display.show(main_group)

# Sub-groups for layering content (so we can hide/replace easily)
background_group = displayio.Group()  # index 0
main_group.append(background_group)


# --------- Gradient Background (single Bitmap + Palette) ---------
def build_gradient(width: int, height: int) -> displayio.TileGrid:
	"""Create a vertical gradient (purple -> orange) using a 64-color palette.

	Keeps memory low by reusing palette indices.
	"""
	palette_size = 64
	palette = displayio.Palette(palette_size)
	for i in range(palette_size):
		t = i / (palette_size - 1)
		# Simple gradient: start (R=40,G=0,B=80) to (R=255,G=120,B=0)
		r = int(40 + (255 - 40) * t)
		g = int(0 + (120 - 0) * t)
		b = int(80 + (0 - 80) * t)
		palette[i] = (r << 16) | (g << 8) | b

	bmp = displayio.Bitmap(width, height, palette_size)
	# Fill rows with palette index mapping by y
	for y in range(height):
		idx = int((y / (height - 1)) * (palette_size - 1))
		for x in range(width):
			bmp[x, y] = idx
	return displayio.TileGrid(bmp, pixel_shader=palette)


def make_solid_bg(color: int) -> displayio.TileGrid:
	pal = displayio.Palette(1)
	pal[0] = color & 0xFFFFFF
	bmp = displayio.Bitmap(DISPLAY_WIDTH, DISPLAY_HEIGHT, 1)
	return displayio.TileGrid(bmp, pixel_shader=pal)


def set_background(mode: str):
	# Clear previous background children
	while len(background_group) > 0:
		background_group.pop()
	if mode == "gradient":
		background_group.append(build_gradient(DISPLAY_WIDTH, DISPLAY_HEIGHT))
	elif mode == "blue":
		background_group.append(make_solid_bg(0x0033AA))
	elif mode == "black":
		background_group.append(make_solid_bg(0x000000))
	else:
		background_group.append(make_solid_bg(0x000000))


# initial background
bg_mode = "gradient"
set_background(bg_mode)


# --------- Optional BME280 Sensor Setup ---------
def init_bme280():
	"""Initialize BME280 over SPI (preferred) or I2C, if available.

	Returns a tuple (sensor, bus) where bus is SPI or I2C object; or (None, None).
	"""
	if DEBUG_SENSOR:
		print("BME280: init start (enabled=%s, lib_present=%s)" % (BME280_ENABLED, adafruit_bme280 is not None))
	if not BME280_ENABLED or adafruit_bme280 is None:
		if DEBUG_SENSOR:
			print("BME280: init skipped (disabled or library missing)")
		return None, None

	if BME280_USE_SPI and BME280_SCK_PIN and BME280_MOSI_PIN and BME280_MISO_PIN and BME280_CS_PIN:
		if DEBUG_SENSOR:
			print("BME280: attempting SPI init on SCK=%r MOSI=%r MISO=%r CS=%r" % (BME280_SCK_PIN, BME280_MOSI_PIN, BME280_MISO_PIN, BME280_CS_PIN))
		try:
			import busio  # type: ignore
			spi = busio.SPI(BME280_SCK_PIN, MOSI=BME280_MOSI_PIN, MISO=BME280_MISO_PIN)  # type: ignore
			# lock and configure if supported
			if hasattr(spi, "try_lock"):
				while not spi.try_lock():
					pass
				try:
					if hasattr(spi, "configure"):
						spi.configure(baudrate=BME280_SPI_BAUDRATE, phase=0, polarity=0)
				finally:
					spi.unlock()
			cs = DigitalInOut(BME280_CS_PIN)
			if DEBUG_SENSOR:
				print("BME280: SPI bus ready, creating sensor @ %d Hz" % BME280_SPI_BAUDRATE)
			if 'BME280_SPI' in globals() and BME280_SPI:
				sensor = BME280_SPI(spi, cs, baudrate=BME280_SPI_BAUDRATE)  # type: ignore
			else:
				raise RuntimeError("BME280_SPI class not available in adafruit_bme280 module")
			try:
				sensor.sea_level_pressure = 1013.25
			except Exception:
				pass
			if DEBUG_SENSOR:
				print("BME280: SPI sensor initialized successfully")
			return sensor, spi
		except Exception as e:
			# fall back to I2C if SPI init fails
			if DEBUG_SENSOR:
				print(f"BME280: SPI init failed -> {e!r}; falling back to I2C")

	# I2C fallback
	try:
		import busio  # type: ignore
		# Build candidate pin pairs to try, in order of preference
		candidate_pairs = [
			# User overrides (if provided)
			(BME280_I2C_SCL_PIN, BME280_I2C_SDA_PIN),
			# Board defaults (if defined on this build)
			(getattr(board, "SCL", None), getattr(board, "SDA", None)),
			# Common Pico defaults
			(getattr(board, "GP1", None), getattr(board, "GP0", None)),  # I2C0: SCL=GP1, SDA=GP0
			(getattr(board, "GP3", None), getattr(board, "GP2", None)),  # I2C1: SCL=GP3, SDA=GP2
		]

		for scl_pin, sda_pin in candidate_pairs:
			if scl_pin is None or sda_pin is None:
				continue
			if DEBUG_SENSOR:
				print("BME280: attempting I2C init on SCL=%r SDA=%r freq=%d" % (scl_pin, sda_pin, BME280_I2C_FREQUENCY))
			try:
				i2c = busio.I2C(scl_pin, sda_pin, frequency=BME280_I2C_FREQUENCY)  # type: ignore
				if DEBUG_SENSOR:
					print("BME280: I2C bus created")
				# Optional: scan the bus for visibility
				try:
					if hasattr(i2c, "try_lock"):
						while not i2c.try_lock():
							pass
						try:
							found = getattr(i2c, "scan", lambda: [])()
							if DEBUG_SENSOR:
								print("BME280: I2C scan -> %s" % (
									"[" + ", ".join("0x%02X" % a for a in found) + "]" if found else "[]"
								))
						finally:
							i2c.unlock()
				except Exception as e_scan:
					if DEBUG_SENSOR:
						print(f"BME280: I2C scan failed -> {e_scan!r}")

				# Try typical I2C addresses
				addresses = [BME280_ADDRESS]
				if 0x76 not in addresses:
					addresses.append(0x76)
				if 0x77 not in addresses:
					addresses.append(0x77)
				for addr in addresses:
					try:
						if DEBUG_SENSOR:
							print("BME280: probing I2C addr 0x%02X" % addr)
						sensor = BME280_I2C(i2c, address=addr)  # type: ignore
						try:
							sensor.sea_level_pressure = 1013.25
						except Exception:
							pass
						if DEBUG_SENSOR:
							print("BME280: I2C sensor initialized successfully at 0x%02X" % addr)
						return sensor, i2c
					except Exception as e_probe:
						if DEBUG_SENSOR:
							print("BME280: probe failed at 0x%02X -> %r" % (addr, e_probe))
			except Exception as e_bus:
				if DEBUG_SENSOR:
					print(f"BME280: I2C bus creation failed on SCL={scl_pin!r} SDA={sda_pin!r} -> {e_bus!r}")
				continue

		# If we got here, no pair worked
		if DEBUG_SENSOR:
			print("BME280: no sensor found over I2C or SPI")
		return None, None
	except Exception as e:
		if DEBUG_SENSOR:
			print(f"BME280: unexpected error during I2C init -> {e!r}")
		return None, None


# --------- Static Shapes ---------
shapes_group = displayio.Group()
main_group.append(shapes_group)

if Rect and Circle:
	# Semi-transparent effect not possible directly; layering gives contrast
	shapes_group.append(Rect(2, 2, 40, 20, fill=0x003366, outline=0xFFFFFF))
	shapes_group.append(Rect(5, 25, 30, 15, fill=0x660022, outline=0xFFFFFF))
	shapes_group.append(Circle(96, 28, 18, fill=0x009966, outline=0xFFFFFF))


# --------- Moving Sprite (small Bitmap) ---------
sprite_palette = displayio.Palette(2)
sprite_palette[0] = 0x000000  # treated as transparent logically
sprite_palette[1] = 0xFFFFFF
sprite_bitmap = displayio.Bitmap(8, 8, 2)
for y in range(8):
	for x in range(8):
		if (x - 3.5) ** 2 + (y - 3.5) ** 2 <= 10:  # circle-ish
			sprite_bitmap[x, y] = 1
		else:
			sprite_bitmap[x, y] = 0

sprite_tile = displayio.TileGrid(sprite_bitmap, pixel_shader=sprite_palette, x=60, y=64)
main_group.append(sprite_tile)


# --------- Dynamic Text ---------
text_group = displayio.Group()
main_group.append(text_group)

if label:
	# Reserve two lines at bottom: sensor (if available) and FPS
	fps_label = label.Label(terminalio.FONT, text="FPS: --", color=0xFFFFFF, x=4, y=DISPLAY_HEIGHT - 4)
	sensor_label = label.Label(terminalio.FONT, text="", color=0x00FFCC, x=4, y=DISPLAY_HEIGHT - 18)
	info_label = label.Label(
		terminalio.FONT,
		text="SSD1351 Demo",
		color=0xFFFF00,
		x=4,
		y=12,
	)
	text_group.append(info_label)
	text_group.append(sensor_label)
	text_group.append(fps_label)
else:
	fps_label = None
	sensor_label = None


# Initialize BME280 and sensor label visibility
bme_sensor, bme_i2c = init_bme280()
sensor_visible = bool(bme_sensor)
last_bme_time = 0.0
if 'sensor_label' in globals() and sensor_label:
	sensor_label.hidden = not sensor_visible
if DEBUG_SENSOR:
	if bme_sensor:
		print("BME280: initialized")
	else:
		print("BME280: not available")


# --------- Simple Menu System ---------
class Button:
	def __init__(self, pin):
		self.available = pin is not None
		if not self.available:
			self.io = None
			return
		io = DigitalInOut(pin)
		io.switch_to_input(pull=Pull.UP)
		self.io = io
		self._last = True  # pull-up idle high
		self._last_time = time.monotonic()
		self.debounce_s = 0.15

	def pressed(self) -> bool:
		if not self.available:
			return False
		io = self.io
		if io is None:
			return False
		now = time.monotonic()
		val = io.value  # True = released, False = pressed
		# detect edge: high -> low
		was_pressed = False
		if self._last and not val and (now - self._last_time) > self.debounce_s:
			was_pressed = True
			self._last_time = now
		if val != self._last:
			self._last_time = now
		self._last = val
		return was_pressed


class SimpleMenu:
	def __init__(self):
		self.group = displayio.Group(x=2, y=2)
		# menu background
		# Transparent fill so it doesn't block the view; keep an outline for readability
		self.bg = Rect(0, 0, 110, 84, fill=None, outline=0xFFFFFF) if Rect else None
		if self.bg:
			self.group.append(self.bg)
		self.items = [
			("Toggle Shapes", self.toggle_shapes),
			("Toggle Sprite", self.toggle_sprite),
			("Toggle Info", self.toggle_info),
			("Toggle Sensor", self.toggle_sensor),
			("BG Mode", self.cycle_bg),
		]
		self.index = 0
		self.labels = []
		# Auto-hide support
		self.auto_hide_s = 4.0
		self.last_interact = time.monotonic()
		self._build_labels()

	def show(self):
		self.group.hidden = False
		self.last_interact = time.monotonic()

	def hide(self):
		self.group.hidden = True

	def touch(self):
		# Record a user interaction and keep menu visible
		self.last_interact = time.monotonic()
		self.group.hidden = False

	def _build_labels(self):
		# clear old labels (keep bg at index 0 if present)
		while len(self.group) > (1 if self.bg else 0):
			self.group.pop()
		self.labels = []
		if label is None:
			return
		def _cap(s):
			# Safe capitalize for environments missing str.capitalize()
			if isinstance(s, str):
				return (s[:1].upper() + s[1:]) if s else ""
			try:
				return str(s)
			except Exception:
				return ""
		# status-aware names
		state_suffix = [
			"On" if not shapes_group.hidden else "Off",
			"On" if not sprite_tile.hidden else "Off",
			"On" if not text_group.hidden else "Off",
			"On" if 'sensor_label' in globals() and sensor_label and not sensor_label.hidden else "Off",
			_cap(bg_mode),
		]
		base_y = 12
		for i, (name, _) in enumerate(self.items):
			sel = "> " if i == self.index else "  "
			txt = f"{sel}{name}: {state_suffix[i]}" if i < len(state_suffix) else f"{sel}{name}"
			lb = label.Label(terminalio.FONT, text=txt, color=0xFFFFFF, x=4, y=base_y + i * 12)
			self.labels.append(lb)
			self.group.append(lb)

	def move(self, delta: int):
		self.index = (self.index + delta) % len(self.items)
		self._build_labels()
		self.touch()

	def activate(self):
		# call the bound action
		_, action = self.items[self.index]
		action()
		self._build_labels()
		self.touch()

	# Actions
	def toggle_shapes(self):
		shapes_group.hidden = not shapes_group.hidden

	def toggle_sprite(self):
		sprite_tile.hidden = not sprite_tile.hidden

	def toggle_info(self):
		text_group.hidden = not text_group.hidden

	def toggle_sensor(self):
		global sensor_visible
		if 'sensor_label' in globals() and sensor_label:
			sensor_visible = not sensor_visible
			sensor_label.hidden = not sensor_visible

	def cycle_bg(self):
		global bg_mode
		modes = ["gradient", "blue", "black"]
		idx = (modes.index(bg_mode) + 1) % len(modes)
		bg_mode = modes[idx]
		set_background(bg_mode)


# Initialize buttons & menu (if pins available)
btn_next = Button(BTN_NEXT_PIN)
btn_select = Button(BTN_SELECT_PIN)
menu = SimpleMenu()
main_group.append(menu.group)

# Start with menu hidden; first button press will reveal it
menu.hide()


# --------- Animation Loop ---------
print("Starting main loop. Press reset to restart.")
frame = 0
last_fps_time = time.monotonic()
frames_in_window = 0

while True:
	now = time.monotonic()
	frame += 1
	frames_in_window += 1

	# Move sprite in a Lissajous / circular path
	t = frame / 60  # ~1 second cycles if ~60fps
	radius = 30
	cx = DISPLAY_WIDTH // 2
	cy = DISPLAY_HEIGHT // 2 + 10
	sprite_tile.x = int(cx + radius * sin(2 * pi * t * 0.7)) - 4
	sprite_tile.y = int(cy + radius * sin(2 * pi * t)) - 4

	# Optional: tweak a shape's attribute for subtle animation
	if Circle and len(shapes_group) >= 3:
		# pulsate circle radius visually by slight index change (can't change radius directly)
		pass  # Keeping static; altering shape requires rebuild -> omitted to save CPU

	# Update FPS every 0.5s to reduce text redraw overhead
	if fps_label and now - last_fps_time >= 0.5:
		fps = frames_in_window / (now - last_fps_time)
		fps_label.text = f"FPS: {fps:4.1f}"
		last_fps_time = now
		frames_in_window = 0

	# --------- BME280 reading ---------
	if bme_sensor and (now - last_bme_time) >= BME280_SAMPLE_INTERVAL_S:
		try:
			T = getattr(bme_sensor, 'temperature')  # Celsius
			H = getattr(bme_sensor, 'humidity')
			P = getattr(bme_sensor, 'pressure')  # hPa
			# Console debug
			if DEBUG_SENSOR:
				print(f"BME280: T={T!r}C, H={H!r}%, P={P!r}hPa")
			# Update on-screen label only if visible and available
			if sensor_visible and sensor_label:
				if isinstance(T, (int, float)) and isinstance(H, (int, float)) and isinstance(P, (int, float)):
					sensor_label.text = f"T:{T:4.1f}C H:{H:4.1f}% P:{P:6.1f}hPa"
				else:
					sensor_label.text = "Sensor: --"
		except Exception as e:
			if DEBUG_SENSOR:
				print(f"BME280 read error: {e}")
			if sensor_visible and sensor_label:
				sensor_label.text = "Sensor: error"
		last_bme_time = now

	# --------- Menu interaction ---------
	# Show-on-first-press behavior: if hidden, the first press only reveals the menu
	next_pressed = btn_next.pressed()
	select_pressed = btn_select.pressed()
	if next_pressed or select_pressed:
		if menu.group.hidden:
			menu.show()
		else:
			if next_pressed:
				menu.move(+1)
			if select_pressed:
				menu.activate()

	# Auto-hide the menu after inactivity
	if not menu.group.hidden and (now - menu.last_interact) > menu.auto_hide_s:
		menu.hide()

	# Tiny sleep yields to USB & avoids 100% busy loop; adjust as needed
	time.sleep(0.001)

