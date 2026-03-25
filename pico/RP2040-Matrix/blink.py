import time
from machine import Pin
import rp2

# Number of RGB lights
NUM_LEDS = 25 
# RGB light maximum brightness
MAX_LUM = 20

@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
def ws2812():
    T1 = 2
    T2 = 5
    T3 = 3
    wrap_target()
    label("bitloop")
    out(x, 1).side(0)[T3 - 1]
    jmp(not_x, "do_zero").side(1)[T1 - 1]
    jmp("bitloop").side(1)[T2 - 1]
    label("do_zero")
    nop().side(0)[T2 - 1]
    wrap()

# Create the StateMachine with the ws2812 program, outputting on Pin(16).
sm = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=Pin(16))
sm.active(1)

# Initialize the color array (the color of each LED)
led_colors = [(0, 0, 0)] * NUM_LEDS

# Color gradient function
def update_leds():
    for color in led_colors:
        r, g, b = color
        rgb = (r << 24) | (g << 16) | (b << 8)
        sm.put(rgb)

# Gradient loop
while True:
    # Blue -> Red Gradient
    for i in range(MAX_LUM):
        for led in range(NUM_LEDS):
            # R=i, G=0, B=MAX_LUM -i
            led_colors[led] = (i, 0, MAX_LUM - i)  
        update_leds()
        time.sleep_ms(20)

    # Red -> Green Gradient
    for i in range(MAX_LUM):
        for led in range(NUM_LEDS):
            # R=MAX_LUM -i, G=i,B=0
            led_colors[led] = (MAX_LUM - i, i, 0)  
        update_leds()
        time.sleep_ms(20)

    # Green -> Blue Gradient
    for i in range(MAX_LUM):
        for led in range(NUM_LEDS):
            # R=0, G=MAX_LUM -i, B=i
            led_colors[led] = (0, MAX_LUM - i, i)  
        update_leds()
        time.sleep_ms(20)
        