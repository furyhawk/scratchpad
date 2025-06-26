#ifndef __DRIVER_KEY_H
#define __DRIVER_KEY_H
#include "RGBMatrixConfig.h"
#if defined CONFIG_SUPPORT_PICO
#include <stdio.h>
#include "pico/stdlib.h"


#define     KEY0_PIN        15
#define     KEY1_PIN        19
#define     KEY2_PIN        21

#define     KEY0_STATUS     gpio_get(KEY0_PIN)
#define     KEY1_STATUS     gpio_get(KEY1_PIN)
#define     KEY2_STATUS     gpio_get(KEY2_PIN)
#elif defined CONFIG_SUPPORT_ESP32S2
#include "driver/gpio.h"
#define     KEY0_PIN        GPIO_NUM_35
#define     KEY1_PIN        GPIO_NUM_39
#define     KEY2_PIN        GPIO_NUM_41

#define     KEY0_STATUS     gpio_get_level(KEY0_PIN)
#define     KEY1_STATUS     gpio_get_level(KEY1_PIN)
#define     KEY2_STATUS     gpio_get_level(KEY2_PIN)
#endif

#define     LONGPRESS       1
#define     SHORTPRESS      0

#define     KEY0_MENU            0
#define     KEY1_DOWN            1
#define     KEY2_UP              2




void picoKeyGpioInit(void);
void esp32S2KeyGpioInit(void);
void WhichKeyPress(void);


#endif
