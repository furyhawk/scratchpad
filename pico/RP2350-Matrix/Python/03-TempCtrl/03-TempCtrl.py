import time
from machine import Pin, ADC
from WS2812 import LEDController

"""
RGB LED Temperature Control System
==================================
Automatically adjusts LED brightness based on onboard temperature sensor readings
to prevent overheating (max temp < 80°C). Implements multi-stage brightness control
with hysteresis for smooth transitions.

Safety Warnings:
-----------------------------------
1. INITIAL BRIGHTNESS:
   - Device boots at 100% brightness (255/255). Avoid direct eye exposure to LEDs.
   
2. POWER REQUIREMENTS:
   - Full brightness draws ~900mA. Use power supply rated ≥1A with stable 5V output.
   
3. OPERATIONAL NOTES:
   - LED surface temperature may exceed 60°C. Avoid physical contact during operation.
   - Prolonged full-brightness operation accelerates LED degradation. Limit continuous use.
"""

# Initialize the onboard temperature sensor (ADC4)
adc = ADC(4)
# Initialize RGB LED control pins
led_ctrl = LEDController()

# Brightness level configuration (temperature threshold and corresponding brightness)
BRIGHTNESS_LEVELS = [
    (0, 255),  # [01] <50°C:   100% brightness
    (50, 219), # [02] 50-55°C: 86%  brightness
    (55, 183), # [03] 55-60°C: 72%  brightness
    (60, 147), # [04] 60-65°C: 58%  brightness
    (65, 111), # [05] 65-70°C: 44%  brightness
    (70, 75),  # [06] 70-75°C: 30%  brightness
    (75, 39),  # [07] 75-78°C: 15%  brightness
    (78, 10),  # [08] >78°C:   4%   brightness
]

temp_dex = 0  # Current gear index
led_ctrl.brightness = BRIGHTNESS_LEVELS[0][1]  # Initial brightness

def read_onboard_temperature():
    raw_value = adc.read_u16()    # Read 16-bit ADC value (0-65535)
    voltage = (3.3 / 65535) * raw_value   # Convert to voltage
    temperature = 27 - (voltage - 0.706) / 0.001721  # Calculate temperature
    return round(temperature, 1)  # Keep one decimal place

while True:
    # Reserve a safe temperature, the onboard temperature cannot be greater than 80 degrees
    temp = read_onboard_temperature() + 5  
    
    # Temperature rising stage
    if temp > BRIGHTNESS_LEVELS[temp_dex+1][0]:  
        temp_dex += 1
        led_ctrl.brightness = BRIGHTNESS_LEVELS[temp_dex][1]
        continue
        
    # Temperature drop phase
    elif temp_dex > 0 and temp <= BRIGHTNESS_LEVELS[temp_dex-1][0]+1: 
        temp_dex -= 1
        led_ctrl.brightness = BRIGHTNESS_LEVELS[temp_dex][1]
    
    # Update all led_ctrl to their current brightness
    led_ctrl.show2((led_ctrl.brightness,led_ctrl.brightness,led_ctrl.brightness))
    
    # Print debug information
    print(f"Temp: {temp}°C, Level: {temp_dex+1}, Brightness: {led_ctrl.brightness*100/255}%")
    time.sleep(1)
    