/*****************************************************************************
* | File        :   LCD_Test.h
* | Author      :   Waveshare team
* | Function    :   test Demo
* | Info        :
*----------------
* |	This version:   V1.0
* | Date        :   2024-07-08
* | Info        :   
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:

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
#
******************************************************************************/
#ifndef _LVGL_EXAMPLE_H_
#define _LVGL_EXAMPLE_H_


#include <stdio.h>
#include <stdlib.h>
#include "pico/stdlib.h"
#include "pico/util/datetime.h"
#include "DEV_Config.h"
#include "lvgl.h"

/*LVGL objects*/
typedef struct {
    lv_obj_t *scr[4];     // Used to store different screens
    lv_obj_t *cur;        // Cursor
    lv_obj_t *btn;        // Button
    lv_obj_t *label;      // Label
    lv_obj_t *sw_1;       // Switch 1
    lv_obj_t *sw_2;       // Switch 2
    uint16_t click_num;   // Number of button clicks
    uint16_t KEY_now;     // Current state of the button
    uint16_t KEY_old;     // Button Previous State
} lvgl_data_struct;

typedef void (*LCD_SetWindowsFunc)(uint16_t, uint16_t, uint16_t, uint16_t);

void LVGL_Init(void);
void handle_key_press(lvgl_data_struct *dat);
void switch_to_next_screen(lv_obj_t *scr[]);

#endif
