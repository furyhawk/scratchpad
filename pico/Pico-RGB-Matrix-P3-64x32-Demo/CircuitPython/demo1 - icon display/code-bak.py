# This example implements a rainbow colored scroller, in which each letter
# has a different color. This is not possible with
# Adafruit_Circuitpython_Display_Text, where each letter in a label has the
# same color
#
# This demo also supports only ASCII characters and the built-in font.
# See the simple_scroller example for one that supports alternative fonts
# and characters, but only has a single color per label.
import time
import busio
from adafruit_ds3231 import adafruit_ds3231
from digitalio import DigitalInOut, Direction

import array

from rainbowio import colorwheel
import board
import displayio
import framebufferio
import rgbmatrix
import terminalio

bit_depth_value = 6
base_width = 64
base_height = 32
chain_across = 1
tile_down = 1
serpentine_value = True

width_value = base_width * chain_across
height_value = base_height * tile_down

displayio.release_displays()

# send register
R1 = DigitalInOut(board.GP2)
G1 = DigitalInOut(board.GP3)
B1 = DigitalInOut(board.GP4)
R2 = DigitalInOut(board.GP5)
G2 = DigitalInOut(board.GP8)
B2 = DigitalInOut(board.GP9)
CLK = DigitalInOut(board.GP11)
STB = DigitalInOut(board.GP12)
OE = DigitalInOut(board.GP13)

R1.direction = Direction.OUTPUT
G1.direction = Direction.OUTPUT
B1.direction = Direction.OUTPUT
R2.direction = Direction.OUTPUT
G2.direction = Direction.OUTPUT
B2.direction = Direction.OUTPUT
CLK.direction = Direction.OUTPUT
STB.direction = Direction.OUTPUT
OE.direction = Direction.OUTPUT

OE.value = True
STB.value = False
CLK.value = False

MaxLed = 64

c12 = [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
c13 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0]

for l in range(0, MaxLed):
    y = l % 16
    R1.value = False
    G1.value = False
    B1.value = False
    R2.value = False
    G2.value = False
    B2.value = False

    if c12[y] == 1:
        R1.value = True
        G1.value = True
        B1.value = True
        R2.value = True
        G2.value = True
        B2.value = True
    if l > (MaxLed - 12):
        STB.value = True
    else:
        STB.value = False
    CLK.value = True
    # time.sleep(0.000002)
    CLK.value = False
STB.value = False
CLK.value = False

for l in range(0, MaxLed):
    y = l % 16
    R1.value = False
    G1.value = False
    B1.value = False
    R2.value = False
    G2.value = False
    B2.value = False

    if c13[y] == 1:
        R1.value = True
        G1.value = True
        B1.value = True
        R2.value = True
        G2.value = True
        B2.value = True
    if l > (MaxLed - 13):
        STB.value = True
    else:
        STB.value = False
    CLK.value = True
    # time.sleep(0.000002)
    CLK.value = False
STB.value = False
CLK.value = False

R1.deinit()
G1.deinit()
B1.deinit()
R2.deinit()
G2.deinit()
B2.deinit()
CLK.deinit()
STB.deinit()
OE.deinit()

matrix = rgbmatrix.RGBMatrix(
    width=width_value, height=height_value, bit_depth=bit_depth_value,
    rgb_pins=[board.GP2, board.GP3, board.GP4, board.GP5, board.GP8, board.GP9],
    addr_pins=[board.GP10, board.GP16, board.GP18, board.GP20],
    clock_pin=board.GP11, latch_pin=board.GP12, output_enable_pin=board.GP13,
    tile=tile_down, serpentine=serpentine_value,
    doublebuffer=True)

display = framebufferio.FramebufferDisplay(matrix, auto_refresh=False,
                                           rotation=180)

i2c = busio.I2C(board.GP7, board.GP6)

rtc = adafruit_ds3231.DS3231(i2c)

# Create a tilegrid with a bunch of common settings
def tilegrid(palette):
    return displayio.TileGrid(
        bitmap=terminalio.FONT.bitmap, pixel_shader=palette,
        width=1, height=1, tile_width=6, tile_height=14, default_tile=32)

g = displayio.Group()

# We only use the built in font which we treat as being 7x14 pixels
linelen = (64//7)+2

# prepare the main groups
l1 = displayio.Group()
l2 = displayio.Group()
g.append(l1)
g.append(l2)
display.show(g)

l1.y = 1
l2.y = 16

# Prepare the palettes and the individual characters' tiles
sh = [displayio.Palette(2) for _ in range(linelen)]
tg1 = [tilegrid(shi) for shi in sh]
tg2 = [tilegrid(shi) for shi in sh]

# Prepare a fast map from byte values to
charmap = array.array('b', [terminalio.FONT.get_glyph(32).tile_index]) * 256
for ch in range(256):
    glyph = terminalio.FONT.get_glyph(ch)
    if glyph is not None:
        charmap[ch] = glyph.tile_index

# Set the X coordinates of each character in label 1, and add it to its group
for idx, gi in enumerate(tg1):
    gi.x = 7 * idx
    l1.append(gi)

# Set the X coordinates of each character in label 2, and add it to its group
for idx, gi in enumerate(tg2):
    gi.x = 7 * idx
    l2.append(gi)

#  These pairs of lines should be the same length
lines = [
    b"Waveshare Test",
    b"RGB LED Matrix",
]

even_lines = lines[0::2]
odd_lines = lines[1::2]

# Scroll a top text and a bottom text
def scroll(t, b):
    # Add spaces to the start and end of each label so that it goes from
    # the far right all the way off the left
    sp = b' ' * linelen
    t = sp + t + sp
    b = sp + b + sp
    maxlen = max(len(t), len(b))
    # For each whole character position...
    for i in range(maxlen-linelen):
        # Set the letter displayed at each position, and its color
        for j in range(linelen):
            sh[j][1] = colorwheel(3 * (2*i+j))
            tg1[j][0] = charmap[t[i+j]]
            tg2[j][0] = charmap[b[i+j]]
        # And then for each pixel position, move the two labels
        # and then refresh the display.
        for j in range(7):
            l1.x = -j
            l2.x = -j
            display.refresh(minimum_frames_per_second=0)

# Repeatedly scroll all the pairs of lines
'''
while True:
    for e, o in zip(even_lines, odd_lines):
        scroll(e, o)
'''

# Lookup table for names of days (nicer printing).
days = ("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday")

# pylint: disable-msg=using-constant-test
if False:  # change to True if you want to set the time!
    #                     year, mon, date, hour, min, sec, wday, yday, isdst
    t = time.struct_time((2017, 10, 29, 15, 14, 15, 0, -1, -1))
    # you must set year, mon, date, hour, min, sec and weekday
    # yearday is not supported, isdst can be set but we don't do anything with it at this time
    print(b"Setting time to:", t)  # uncomment for debugging
    rtc.datetime = t
    print()
# pylint: enable-msg=using-constant-test

while True:
    t = rtc.datetime
    print(t)
    time.sleep(1)
    print("The date is {} {}/{}/{}".format(days[int(t.tm_wday)], t.tm_mday, t.tm_mon, t.tm_year))
    print("{}:{:02}:{:02}".format(t.tm_hour, t.tm_min, t.tm_sec))
    scroll(b' Waveshare', b'Hello word!')
