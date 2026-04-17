import time
import urandom
from WS2812 import LEDController



# create controller using default brightness from WS2812 (now scaled to 30%)
led = LEDController()
W = led.width
H = led.height


def _scale_color(r, g, b):
    bmax = led.brightness
    return (r * bmax // 255, g * bmax // 255, b * bmax // 255)


def wheel(pos):
    pos &= 255
    if pos < 85:
        return _scale_color(255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return _scale_color(0, 255 - pos * 3, pos * 3)
    pos -= 170
    return _scale_color(pos * 3, 0, 255 - pos * 3)


# Basic animations

def rainbow_cycle(duration=5, speed=50):
    end = time.ticks_add(time.ticks_ms(), int(duration * 1000))
    t = 0
    while time.ticks_diff(end, time.ticks_ms()) > 0:
        for x in range(W):
            for y in range(H):
                i = (x * H + y)
                color = wheel((i * 8 + t) & 255)
                led.set_pixel(x, y, color)
        led.show()
        t = (t + 1) & 255
        time.sleep_ms(speed)


def sparkle(duration=5, density=6):
    end = time.ticks_add(time.ticks_ms(), int(duration * 1000))
    for x in range(W):
        for y in range(H):
            led.set_pixel(x, y, (0, 0, 0))
    while time.ticks_diff(end, time.ticks_ms()) > 0:
        for i in range(density):
            r = urandom.getrandbits(8)
            g = urandom.getrandbits(8)
            b = urandom.getrandbits(8)
            x = urandom.getrandbits(8) % W
            y = urandom.getrandbits(8) % H
            led.set_pixel(x, y, _scale_color(r, g, b))
        led.show()
        time.sleep_ms(80)
        for _ in range(density // 2):
            x = urandom.getrandbits(8) % W
            y = urandom.getrandbits(8) % H
            led.set_pixel(x, y, (0, 0, 0))


def rain(duration=6):
    end = time.ticks_add(time.ticks_ms(), int(duration * 1000))
    cols = [0] * W
    colors = [wheel(urandom.getrandbits(8)) for _ in range(W)]
    while time.ticks_diff(end, time.ticks_ms()) > 0:
        for x in range(W):
            cols[x] += 1
            if cols[x] > H + (urandom.getrandbits(8) % 6):
                cols[x] = 0
                colors[x] = wheel(urandom.getrandbits(8))
        led.clear()
        for x in range(W):
            for y in range(min(cols[x], H)):
                r, g, b = colors[x]
                led.set_pixel(x, H - 1 - y, (r, g, b))
        led.show()
        time.sleep_ms(120)


def chase(duration=5, color=None):
    if color is None:
        color = wheel(urandom.getrandbits(8))
    end = time.ticks_add(time.ticks_ms(), int(duration * 1000))
    pos = 0
    while time.ticks_diff(end, time.ticks_ms()) > 0:
        led.clear()
        for i in range(6):
            x = (pos + i) % W
            for y in range(H):
                led.set_pixel(x, y, color)
        led.show()
        pos = (pos + 1) % W
        time.sleep_ms(120)


def checkerboard(duration=5):
    end = time.ticks_add(time.ticks_ms(), int(duration * 1000))
    c1 = wheel(urandom.getrandbits(8))
    c2 = wheel(urandom.getrandbits(8))
    flip = False
    while time.ticks_diff(end, time.ticks_ms()) > 0:
        for x in range(W):
            for y in range(H):
                if ((x + y) % 2 == (1 if flip else 0)):
                    led.set_pixel(x, y, c1)
                else:
                    led.set_pixel(x, y, c2)
        led.show()
        flip = not flip
        time.sleep_ms(400)


# New animations

def fade_all(duration=5, steps=40):
    end = time.ticks_add(time.ticks_ms(), int(duration * 1000))
    target = wheel(urandom.getrandbits(8))
    while time.ticks_diff(end, time.ticks_ms()) > 0:
        # fade in
        for s in range(steps):
            frac = s * 1.0 / (steps - 1)
            r = int(target[0] * frac)
            g = int(target[1] * frac)
            b = int(target[2] * frac)
            for x in range(W):
                for y in range(H):
                    led.set_pixel(x, y, (r, g, b))
            led.show()
            time.sleep_ms(int((time.ticks_diff(end, time.ticks_ms()) / 1000) * 0.02) if time.ticks_diff(end, time.ticks_ms())>0 else 10)
        # fade out
        for s in range(steps - 1, -1, -1):
            frac = s * 1.0 / (steps - 1)
            r = int(target[0] * frac)
            g = int(target[1] * frac)
            b = int(target[2] * frac)
            for x in range(W):
                for y in range(H):
                    led.set_pixel(x, y, (r, g, b))
            led.show()
            time.sleep_ms(15)


def snake(duration=6):
    end = time.ticks_add(time.ticks_ms(), int(duration * 1000))
    path = []
    for x in range(W):
        col = list(range(H)) if x % 2 == 0 else list(range(H - 1, -1, -1))
        for y in col:
            path.append((x, y))
    pos = 0
    color = wheel(urandom.getrandbits(8))
    length = max(3, H // 2)
    while time.ticks_diff(end, time.ticks_ms()) > 0:
        led.clear()
        for i in range(length):
            idx = (pos + i) % len(path)
            x, y = path[idx]
            led.set_pixel(x, y, color)
        led.show()
        pos = (pos + 1) % len(path)
        time.sleep_ms(90)


def spiral(duration=6):
    # simple outward spiral fill
    end = time.ticks_add(time.ticks_ms(), int(duration * 1000))
    color = wheel(urandom.getrandbits(8))
    x0 = 0
    x1 = W - 1
    y0 = 0
    y1 = H - 1
    while time.ticks_diff(end, time.ticks_ms()) > 0:
        led.clear()
        cx = x0
        cy = y0
        while x0 <= x1 and y0 <= y1:
            for x in range(x0, x1 + 1):
                led.set_pixel(x, y0, color)
            for y in range(y0 + 1, y1 + 1):
                led.set_pixel(x1, y, color)
            if y0 < y1:
                for x in range(x1 - 1, x0 - 1, -1):
                    led.set_pixel(x, y1, color)
            if x0 < x1:
                for y in range(y1 - 1, y0, -1):
                    led.set_pixel(x0, y, color)
            led.show()
            time.sleep_ms(120)
            x0 += 1
            x1 -= 1
            y0 += 1
            y1 -= 1
        # reset bounds for next loop
        x0 = 0
        x1 = W - 1
        y0 = 0
        y1 = H - 1
        time.sleep_ms(80)


def static_noise(duration=5, density=80):
    end = time.ticks_add(time.ticks_ms(), int(duration * 1000))
    while time.ticks_diff(end, time.ticks_ms()) > 0:
        for _ in range(density):
            r = urandom.getrandbits(8)
            g = urandom.getrandbits(8)
            b = urandom.getrandbits(8)
            x = urandom.getrandbits(8) % W
            y = urandom.getrandbits(8) % H
            led.set_pixel(x, y, _scale_color(r, g, b))
        led.show()
        time.sleep_ms(40)
        # fade out a random subset
        for _ in range(density // 3):
            x = urandom.getrandbits(8) % W
            y = urandom.getrandbits(8) % H
            led.set_pixel(x, y, (0, 0, 0))


def color_burst(duration=5, burst_steps=8):
    end = time.ticks_add(time.ticks_ms(), int(duration * 1000))
    while time.ticks_diff(end, time.ticks_ms()) > 0:
        cx = urandom.getrandbits(8) % W
        cy = urandom.getrandbits(8) % H
        base = wheel(urandom.getrandbits(8))
        for r in range(burst_steps):
            for x in range(W):
                for y in range(H):
                    if abs(x - cx) + abs(y - cy) == r:
                        led.set_pixel(x, y, base)
            led.show()
            time.sleep_ms(60)
            if time.ticks_diff(end, time.ticks_ms()) <= 0:
                break


def twinkle_field(duration=6, density=10):
    end = time.ticks_add(time.ticks_ms(), int(duration * 1000))
    while time.ticks_diff(end, time.ticks_ms()) > 0:
        picks = []
        for _ in range(density):
            x = urandom.getrandbits(8) % W
            y = urandom.getrandbits(8) % H
            c = wheel(urandom.getrandbits(8))
            led.set_pixel(x, y, c)
            picks.append((x, y))
        led.show()
        time.sleep_ms(120)
        # gentle fade of picked pixels
        for x, y in picks:
            led.set_pixel(x, y, (0, 0, 0))
        led.show()
        time.sleep_ms(80)


def tornado(duration=6, width=3):
    end = time.ticks_add(time.ticks_ms(), int(duration * 1000))
    step = 0
    while time.ticks_diff(end, time.ticks_ms()) > 0:
        led.clear()
        color = wheel(urandom.getrandbits(8))
        for y in range(H):
            x = (step + y) % W
            for w in range(width):
                led.set_pixel((x + w) % W, y, color)
        led.show()
        step = (step + 1) % W
        time.sleep_ms(70)


ANIMATIONS = [
    rainbow_cycle,
    sparkle,
    rain,
    chase,
    checkerboard,
    fade_all,
    snake,
    spiral,
    static_noise,
    color_burst,
    twinkle_field,
    tornado,
]


def pick_rand(max_v):
    return urandom.getrandbits(8) % max_v


def run_random_loop():
    try:
        while True:
            anim = ANIMATIONS[pick_rand(len(ANIMATIONS))]
            dur = 3 + (pick_rand(6))  # 3..8 seconds
            if anim is chase and (pick_rand(2) == 0):
                c = wheel(pick_rand(256))
                anim(dur, color=c)
            else:
                anim(dur)
            led.clear()
            led.show()
            time.sleep_ms(300)
    except KeyboardInterrupt:
        led.clear()
        led.show()

if __name__ == '__main__':
    run_random_loop()
