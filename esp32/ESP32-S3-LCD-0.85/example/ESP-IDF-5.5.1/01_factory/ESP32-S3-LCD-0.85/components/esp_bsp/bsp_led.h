#ifndef __BSP_LED_H_
#define __BSP_LED_H_

#include "led_strip.h"

#define WS2812_GPIO       48      
#define WS2812_LED_COUNT  8       
#define WS2812_MAX_BRIGHTNESS 255 

extern led_strip_handle_t ws2812_strip;
extern SemaphoreHandle_t led_effect_semaphore;
extern bool led_effect_running;

void ws2812_init(void);

void ws2812_set_led(uint8_t index, uint8_t r, uint8_t g, uint8_t b, uint8_t brightness);

void ws2812_effect_task(void *arg);

void bsp_led_set_all(uint8_t r, uint8_t g, uint8_t b, uint8_t brightness);

void bsp_led_clear(void);

void led_effect_task(void *arg);

#endif