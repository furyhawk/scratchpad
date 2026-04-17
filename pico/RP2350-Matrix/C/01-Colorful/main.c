/*****************************************************************************
* | File      	:   main.c
* | Author      :   Waveshare Team
* | Function    :   RGB LED gradient color
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
int main() {
    if(DEV_Module_Init()!=0){
        return -1;
    }
    WS2812_init();

    while (true) {
        /* Red -> Green Gradient */
        for (int i = 0; i <= led_ctrl.brightness; ++i) {
            uint8_t r = led_ctrl.brightness - i;
            uint8_t g = i;
            uint8_t b = 0;
            WS2812_show2(r, g, b);
            DEV_Delay_ms(50);
        }

        /* Green -> Blue Gradient */
        for (int i = 0; i <= led_ctrl.brightness; ++i) {
            uint8_t r = 0;
            uint8_t g = led_ctrl.brightness - i;
            uint8_t b = i;
            WS2812_show2(r, g, b);
            DEV_Delay_ms(50);
        }

        /* Blue -> Red Gradient */
        for (int i = 0; i <= led_ctrl.brightness; ++i) {
            uint8_t r = i;
            uint8_t g = 0;
            uint8_t b = led_ctrl.brightness - i;
            WS2812_show2(r, g, b);
            DEV_Delay_ms(50);
        }
    }
}
