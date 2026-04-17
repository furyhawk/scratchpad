import time
from machine import Pin
from WS2812 import LEDController

# Initialize RGB LED control pins
led_ctrl = LEDController(brightness=20)

def gradient_effect():
    """ Realize RGB gradient effect (blue → red → green → blue cycle) """
    while True:
        # Red → Green Gradient
        for i in range(led_ctrl.brightness):
            led_ctrl.show2((led_ctrl.brightness - i, i, 0))
            time.sleep_ms(50)

        # Green → Blue Gradient
        for i in range(led_ctrl.brightness):
            led_ctrl.show2((0, led_ctrl.brightness - i, i))
            time.sleep_ms(50)
            
        # Blue → Red Gradient
        for i in range(led_ctrl.brightness):
            led_ctrl.show2((i, 0, led_ctrl.brightness - i))
            time.sleep_ms(50)

# Start gradient effect
gradient_effect()

