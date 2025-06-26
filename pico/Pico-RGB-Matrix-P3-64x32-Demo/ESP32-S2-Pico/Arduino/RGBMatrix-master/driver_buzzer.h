#ifndef __BUZZER_H
#define __BUZZER_H

#include "RGBMatrixConfig.h"

#if defined CONFIG_SUPPORT_PICO
#include "pico/stdlib.h"
#define BUZZER     27
#define BUZZERON()    gpio_put(BUZZER, 1)
#define BUZZEROFF()   gpio_put(BUZZER, 0)
#elif defined CONFIG_SUPPORT_ESP32S2
#include "driver/gpio.h"
#define BUZZER     GPIO_NUM_7
#define BUZZERON()    gpio_set_level(BUZZER, 1)
#define BUZZEROFF()   gpio_set_level(BUZZER, 0)
#endif

void buzzerInit(void);


#endif
