import time
import math
import random
from machine import Pin
import rp2

# 5x5 LED matrix geometry
WIDTH = 5
HEIGHT = 5
NUM_LEDS = WIDTH * HEIGHT

# Toggle mapping mode for matrix wiring.
# False: row-major   index = y * WIDTH + x
# True : serpentine  odd rows are reversed
SERPENTINE = False

# Keep power/heat reasonable on RP2040 + WS2812 strips
MIN_LUM = 1
MAX_LUM = 8

# Animation speed controls (lower = slower)
BREATH_SPEED = 0.055
SWEEP_SPEED = 0.06
FRAME_DELAY_MS = 20
MODE_SECONDS = 8


@rp2.asm_pio(
    sideset_init=rp2.PIO.OUT_LOW,
    out_shiftdir=rp2.PIO.SHIFT_LEFT,
    autopull=True,
    pull_thresh=24
)
def ws2812():
    t1 = 2
    t2 = 5
    t3 = 3
    wrap_target()
    label("bitloop")
    out(x, 1).side(0)[t3 - 1]
    jmp(not_x, "do_zero").side(1)[t1 - 1]
    jmp("bitloop").side(1)[t2 - 1]
    label("do_zero")
    nop().side(0)[t2 - 1]
    wrap()


# Create the StateMachine with the ws2812 program, outputting on Pin(16)
sm = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=Pin(16))
sm.active(1)

# GRB tuple per LED
led_colors = [(0, 0, 0)] * NUM_LEDS


def hsv_to_rgb(h, s, v):
    """Convert HSV (0..1) to RGB (0..255)."""
    h = h % 1.0
    i = int(h * 6.0)
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - f * s)
    t = v * (1.0 - (1.0 - f) * s)

    i = i % 6
    if i == 0:
        r, g, b = v, t, p
    elif i == 1:
        r, g, b = q, v, p
    elif i == 2:
        r, g, b = p, v, t
    elif i == 3:
        r, g, b = p, q, v
    elif i == 4:
        r, g, b = t, p, v
    else:
        r, g, b = v, p, q

    return int(r * 255), int(g * 255), int(b * 255)


def write_leds():
    for r, g, b in led_colors:
        sm.put((r << 24) | (g << 16) | (b << 8))


def lum_scale(v255, lum):
    """Scale 0..255 channel by current luminance 0..MAX_LUM."""
    return (v255 * lum) // 255


def set_pixel_xy(x, y, rgb):
    i = xy_to_index(x, y)
    if i is None:
        return
    led_colors[i] = rgb


def clear_leds():
    for i in range(NUM_LEDS):
        led_colors[i] = (0, 0, 0)


def apply_breath(base_lum, strength=1.0):
    """Scale the full frame by breathing luminance."""
    scale = max(MIN_LUM, int(base_lum * strength))
    for i in range(NUM_LEDS):
        r, g, b = led_colors[i]
        led_colors[i] = (
            lum_scale(r, scale),
            lum_scale(g, scale),
            lum_scale(b, scale),
        )


def render_mode_hypnotic(t, lum):
    for y in range(HEIGHT):
        for x in range(WIDTH):
            # Blend x/y so color flows diagonally across the matrix.
            pos = (x + y) / (WIDTH + HEIGHT - 2)
            # Bias hue space toward red so red appears longer per cycle.
            base_hue = (pos + t * SWEEP_SPEED) % 1.0
            hue = (base_hue * 0.82) % 1.0
            r, g, b = hsv_to_rgb(hue, 1.0, 1.0)

            # Add subtle secondary wave for a liquid/hypnotic feel.
            wave = (math.sin((x * 0.8) + (y * 0.6) + t * 0.12) + 1.0) * 0.5
            local_lum = int(MIN_LUM + wave * (lum - MIN_LUM))
            if local_lum < 2:
                local_lum = 2

            set_pixel_xy(
                x,
                y,
                (
                    lum_scale(r, local_lum),
                    lum_scale(g, local_lum),
                    lum_scale(b, local_lum),
                ),
            )


def render_mode_plasma(t, lum):
    w = max(1, WIDTH - 1)
    h = max(1, HEIGHT - 1)
    for y in range(HEIGHT):
        for x in range(WIDTH):
            xf = x / w
            yf = y / h
            v = (
                math.sin((xf * 5.8) + t * 0.11)
                + math.sin((yf * 6.2) - t * 0.09)
                + math.sin(((xf + yf) * 4.6) + t * 0.07)
            )
            hue = ((v + 3.0) / 6.0) * 0.82
            sat = 0.95
            val = 1.0
            r, g, b = hsv_to_rgb(hue, sat, val)
            set_pixel_xy(
                x,
                y,
                (
                    lum_scale(r, lum),
                    lum_scale(g, lum),
                    lum_scale(b, lum),
                ),
            )


def render_mode_radar(t, lum):
    cx = (WIDTH - 1) / 2.0
    cy = (HEIGHT - 1) / 2.0
    angle = t * 0.11
    beam_x = math.cos(angle)
    beam_y = math.sin(angle)
    for y in range(HEIGHT):
        for x in range(WIDTH):
            dx = x - cx
            dy = y - cy
            mag = math.sqrt(dx * dx + dy * dy) + 1e-6
            ndx = dx / mag
            ndy = dy / mag
            align = ndx * beam_x + ndy * beam_y
            trail = max(0.0, align)
            dist = min(1.0, mag / (max(WIDTH, HEIGHT) / 1.6))
            intensity = trail * (1.0 - dist * 0.45)

            hue = (0.34 + 0.07 * (1.0 - dist) + 0.03 * math.sin(t * 0.08)) % 1.0
            r, g, b = hsv_to_rgb(hue, 1.0, intensity)
            set_pixel_xy(
                x,
                y,
                (
                    lum_scale(r, lum),
                    lum_scale(g, lum),
                    lum_scale(b, lum),
                ),
            )


def render_mode_twinkle(t, lum):
    # Gentle frame fade for trailing twinkles.
    for i in range(NUM_LEDS):
        r, g, b = led_colors[i]
        led_colors[i] = (
            (r * 7) // 10,
            (g * 7) // 10,
            (b * 7) // 10,
        )

    # Spawn a couple of sparkles each frame.
    for _ in range(2):
        x = random.randrange(WIDTH)
        y = random.randrange(HEIGHT)
        hue = random.random() * 0.82
        r, g, b = hsv_to_rgb(hue, 0.65, 1.0)
        set_pixel_xy(
            x,
            y,
            (
                lum_scale(r, lum),
                lum_scale(g, lum),
                lum_scale(b, lum),
            ),
        )


def render_mode_ripple(t, lum):
    cx = (WIDTH - 1) / 2.0
    cy = (HEIGHT - 1) / 2.0
    for y in range(HEIGHT):
        for x in range(WIDTH):
            dx = x - cx
            dy = y - cy
            dist = math.sqrt(dx * dx + dy * dy)
            phase = (dist * 1.9) - (t * 0.17)
            wave = (math.sin(phase) + 1.0) * 0.5
            hue = ((0.02 + dist * 0.08 + t * 0.01) % 1.0) * 0.82
            r, g, b = hsv_to_rgb(hue, 1.0, wave)
            set_pixel_xy(
                x,
                y,
                (
                    lum_scale(r, lum),
                    lum_scale(g, lum),
                    lum_scale(b, lum),
                ),
            )


def xy_to_index(x, y):
    """Map matrix coordinates to linear LED index."""
    if not (0 <= x < WIDTH and 0 <= y < HEIGHT):
        return None

    if SERPENTINE and (y % 2 == 1):
        x = (WIDTH - 1) - x

    return y * WIDTH + x


t = 0.0
while True:
    # Breath from MIN_LUM..MAX_LUM using smooth sinusoid
    breath = (math.sin(t * BREATH_SPEED) + 1.0) * 0.5
    lum = int(MIN_LUM + breath * (MAX_LUM - MIN_LUM))

    mode = int((t * FRAME_DELAY_MS) // (MODE_SECONDS * 1000)) % 5
    if mode == 0:
        render_mode_hypnotic(t, lum)
    elif mode == 1:
        render_mode_plasma(t, lum)
    elif mode == 2:
        render_mode_radar(t, lum)
    elif mode == 3:
        render_mode_twinkle(t, max(2, lum))
    else:
        render_mode_ripple(t, lum)

    write_leds()
    time.sleep_ms(FRAME_DELAY_MS)
    t += 1.0
