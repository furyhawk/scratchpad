#ifndef __DRIVER_IR_H
#define __DRIVER_IR_H
#include "RGBMatrixConfig.h"
#include  <stdio.h>

#define UP_KEYVAL   0x40
#define DOWN_KEYVAL 0x19
#define MENU_KEYVAL 0x47
#define EXIT_KEYVAL 0x45

#if defined CONFIG_SUPPORT_PICO
#include <stdio.h>
#include "pico/stdlib.h"

#elif defined CONFIG_SUPPORT_ESP32S2

#include <stdio.h>
#include <stdlib.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include "driver/rmt.h"
#define CLK_DIV           100
#define TICK_10_US        (80000000 / CLK_DIV / 100000)
#define GPIO_NUM_IR GPIO_NUM_8
#define RMT_CHANNEL RMT_CHANNEL_0

void esp32S2IRGpioInit(void);
rmt_item32_t* IRrecvReadIR(void);


#endif



#endif

