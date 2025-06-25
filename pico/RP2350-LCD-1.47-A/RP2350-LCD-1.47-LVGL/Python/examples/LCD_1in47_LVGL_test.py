import sys
sys.path.append('.')
sys.path.append('./examples')
import machine
import time
from machine import Pin, PWM
from LCD_1in47 import LCD_1in47
from LVGL import LVGL
from LVGL_example import WIDGETS

machine.freq(230_000_000)
    
if __name__=='__main__':
  
    print("LCD_1in47_LVGL_test Demo")
    # Init LCD
    LCD = LCD_1in47()
    LCD.set_bl_pwm(65535 * 60 // 100)
    print("Init LCD done")
    
    # Init LVGL
    LVGL(LCD=LCD)
    print("Init LVGL done")
    
    # Init WIDGETS
    WIDGETS(LCD=LCD)
    print("Init WIDGETS done")

    while True:
        time.sleep(1)







