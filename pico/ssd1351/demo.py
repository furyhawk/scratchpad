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

Required libraries in /lib on CIRCUITPY drive:
  adafruit_ssd1351.mpy
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
	fps_label = label.Label(terminalio.FONT, text="FPS: --", color=0xFFFFFF, x=4, y=DISPLAY_HEIGHT - 4)
	info_label = label.Label(
		terminalio.FONT,
		text="SSD1351 Demo",
		color=0xFFFF00,
		x=4,
		y=12,
	)
	text_group.append(info_label)
	text_group.append(fps_label)
else:
	fps_label = None


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
		now = time.monotonic()
		val = self.io.value  # True = released, False = pressed
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
		self.bg = Rect(0, 0, 96, 70, fill=0x000000, outline=0xFFFFFF) if Rect else None
		if self.bg:
			self.group.append(self.bg)
		self.items = [
			("Toggle Shapes", self.toggle_shapes),
			("Toggle Sprite", self.toggle_sprite),
			("Toggle Info", self.toggle_info),
			("BG Mode", self.cycle_bg),
		]
		self.index = 0
		self.labels = []
		self._build_labels()

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

	def activate(self):
		# call the bound action
		_, action = self.items[self.index]
		action()
		self._build_labels()

	# Actions
	def toggle_shapes(self):
		shapes_group.hidden = not shapes_group.hidden

	def toggle_sprite(self):
		sprite_tile.hidden = not sprite_tile.hidden

	def toggle_info(self):
		text_group.hidden = not text_group.hidden

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

	# --------- Menu interaction ---------
	if btn_next.pressed():
		menu.move(+1)
	if btn_select.pressed():
		menu.activate()

	# Tiny sleep yields to USB & avoids 100% busy loop; adjust as needed
	time.sleep(0.001)

