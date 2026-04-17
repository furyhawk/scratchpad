import rp2
from machine import Pin

NUM_LEDS = 64        # 8x8 matrix
WIDTH = 8            # WIDTH
HEIGHT = 8           # HIGHT
LED_BRIGHTNESS = 10  # LED Brightness MAX:255

class LEDController:
    @rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT,
                autopull=True, pull_thresh=24)
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

    def __init__(self, pin=25, num_leds=NUM_LEDS, brightness=LED_BRIGHTNESS):
        self.sm = rp2.StateMachine(0, self.ws2812, freq=8_000_000, sideset_base=Pin(pin))
        self.sm.active(1)
        self.leds = [(0,0,0)] * num_leds
        self.width = WIDTH
        self.height = HEIGHT
        self.num_leds = num_leds
        self.brightness = brightness
        
    def _pos_to_index(self, x, y):
        return self.width * x + y
    
    def set_pixel(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            index = self._pos_to_index(x, y)
            r, g, b = color
            r = min(r, self.brightness)
            g = min(g, self.brightness)
            b = min(b, self.brightness)
            self.leds[index] = (r, g, b)
    
    def clear(self):
        self.leds = [(0,0,0)] * self.num_leds
    
    def show(self):
        for i in range(self.num_leds):
            r, g, b = self.leds[i]
            rgb = (r << 24) | (g << 16) | (b << 8)
            self.sm.put(rgb)
            
    def show2(self, color):
        for i in range(self.num_leds):
            r, g, b = color
            rgb = (r << 24) | (g << 16) | (b << 8)
            self.sm.put(rgb)
            

