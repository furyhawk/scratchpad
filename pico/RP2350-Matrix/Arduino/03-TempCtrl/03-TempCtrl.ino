/*****************************************************************************
* | File      	:   main.c
* | Author      :   Waveshare Team
* | Function    :   RGB LED temperature control
* | Info        :
*----------------
* |	This version:   V1.0
* | Date        :   2025-07-29
* | Info        :   
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of theex Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
******************************************************************************/
#include "DEV_Config.h"
#include "WS2812.h"

/* 
 * RGB LED Temperature Control System
 * ==================================
 * Automatically adjusts LED brightness based on onboard temperature sensor readings
 * to prevent overheating (max temp < 80°C). Implements multi-stage brightness control
 * with hysteresis for smooth transitions.
 * 
 * Safety Warnings:
 * -----------------------------------
 * 1. INITIAL BRIGHTNESS:
 *    - Device boots at 100% brightness (255/255). Avoid direct eye exposure to LEDs.
 * 
 * 2. POWER REQUIREMENTS:
 *    - Full brightness draws ~900mA. Use power supply rated ≥1A with stable 5V output.
 *  
 * 3. OPERATIONAL NOTES:
 *    - LED surface temperature may exceed 60°C. Avoid physical contact during operation.
 *    - Prolonged full-brightness operation accelerates LED degradation. Limit continuous use.
 */

// Brightness gear configuration (temperature threshold, brightness value)
typedef struct {
    float temp_threshold;
    uint8_t brightness;
} BrightnessLevel;

BrightnessLevel BRIGHTNESS_LEVELS[] = {
    {0, 255},   // [01] <50°C:   100% brightness
    {50, 219},  // [02] 50-55°C: 86%  brightness
    {55, 183},  // [03] 55-60°C: 72%  brightness
    {60, 147},  // [04] 60-65°C: 58%  brightness
    {65, 111},  // [05] 65-70°C: 44%  brightness
    {70, 75},   // [06] 70-75°C: 30%  brightness
    {75, 39},   // [07] 75-78°C: 15%  brightness
    {78, 10},   // [08] >78°C:   4%   brightness
};

uint8_t temp_dex = 0;              // Current gear index
uint8_t current_brightness = 255;  // Current brightness

float read_onboard_temperature() {
    // 12-bit conversion, assume max value == ADC_VREF == 3.3 V
    const float conversionFactor = 3.3f / (1 << 12);
    float adc = (float)adc_read() * conversionFactor;
    float tempC = 27.0f - (adc - 0.706f) / 0.001721f;
    return tempC;
}

void setup() {
    if (DEV_Module_Init() != 0)
        Serial.println("GPIO Init Fail!");
    else
        Serial.println("GPIO Init successful!");
    WS2812_init();
}

void loop() {
    while(1)
    {
        // Reserve a safe temperature, the onboard temperature cannot be greater than 80 degrees
        float temp = read_onboard_temperature() + 5.0f; 

        // Temperature rising stage: check whether it is necessary to shift up
        if (temp > BRIGHTNESS_LEVELS[temp_dex+1].temp_threshold) {
            temp_dex++;
            current_brightness = BRIGHTNESS_LEVELS[temp_dex].brightness;
            continue;
        }

        // Temperature drop phase: Check if downshift is needed
        else if (temp_dex > 0 && temp <= BRIGHTNESS_LEVELS[temp_dex-1].temp_threshold + 1) {
            temp_dex--;
            current_brightness = BRIGHTNESS_LEVELS[temp_dex].brightness;
        }

        // Update all LEDs to current brightness
        WS2812_show2(current_brightness, current_brightness, current_brightness);

        // Print debug information
        Serial.printf("Temp: %.1fC, Level: %d, Brightness: %d%%\n", 
               temp, temp_dex + 1, current_brightness * 100 / 255);

        DEV_Delay_ms(1000);
    }
}
