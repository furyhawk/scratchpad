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
ROTATION = 0  # 0, 90, 180, 270
BAUDRATE = 24_000_000  # You can reduce if you see noise / instability


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


gradient_tile = build_gradient(DISPLAY_WIDTH, DISPLAY_HEIGHT)
main_group.append(gradient_tile)


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

	# Tiny sleep yields to USB & avoids 100% busy loop; adjust as needed
	time.sleep(0.001)

