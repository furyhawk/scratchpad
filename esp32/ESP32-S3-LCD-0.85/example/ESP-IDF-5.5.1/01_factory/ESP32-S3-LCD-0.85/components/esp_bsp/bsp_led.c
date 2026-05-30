#include "bsp_led.h"
#include "esp_log.h"
#include "esp_err.h"

#define TAG  "WS2812"

typedef enum {
    LED_EFFECT_FULL_COLOR = 0, 
    LED_EFFECT_WATER_FLOW,    
    LED_EFFECT_RUNNING_HORSE, 
    LED_EFFECT_MAX             
} led_effect_type_t;

led_strip_handle_t ws2812_strip = NULL;

SemaphoreHandle_t led_effect_semaphore;

bool led_effect_running = false;

void ws2812_init(void)
{
    led_strip_config_t strip_config = {
        .strip_gpio_num = WS2812_GPIO,
        .max_leds = WS2812_LED_COUNT,
        .color_component_format = LED_STRIP_COLOR_COMPONENT_FMT_GRB,
        .led_model = LED_MODEL_WS2812,
        .flags.invert_out = false,
    };

    led_strip_rmt_config_t rmt_config = {
        .resolution_hz = 10 * 1000 * 1000, 
    };

    esp_err_t err = led_strip_new_rmt_device(&strip_config, &rmt_config, &ws2812_strip);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "WS2812 init fail: %s", esp_err_to_name(err));
        return;
    }

    led_strip_clear(ws2812_strip);
    ESP_LOGI(TAG, "WS2812 init success");
}

void ws2812_set_led(uint8_t index, uint8_t r, uint8_t g, uint8_t b, uint8_t brightness)
{
    if (index >= WS2812_LED_COUNT) return;

    r = (r * brightness) / WS2812_MAX_BRIGHTNESS;
    g = (g * brightness) / WS2812_MAX_BRIGHTNESS;
    b = (b * brightness) / WS2812_MAX_BRIGHTNESS;

    led_strip_set_pixel(ws2812_strip, index, g, r, b);
    led_strip_refresh(ws2812_strip);
}

void ws2812_effect_task(void *arg)
{
    uint8_t current_led = 0;
    while (1) {
        led_strip_clear(ws2812_strip);
        ws2812_set_led(current_led, 255, 0, 0, WS2812_MAX_BRIGHTNESS / 2);
        current_led = (current_led + 1) % WS2812_LED_COUNT;
        vTaskDelay(pdMS_TO_TICKS(300));
    }
    vTaskDelete(NULL);
}

void bsp_led_set_all(uint8_t r, uint8_t g, uint8_t b, uint8_t brightness)
{
    if (ws2812_strip == NULL) {
        ESP_LOGE(TAG, "WS2812 strip not initialized!");
        return;
    }

    r = (r * brightness) / WS2812_MAX_BRIGHTNESS;
    g = (g * brightness) / WS2812_MAX_BRIGHTNESS;
    b = (b * brightness) / WS2812_MAX_BRIGHTNESS;

    for (int i = 0; i < WS2812_LED_COUNT; i++) {
        led_strip_set_pixel(ws2812_strip, i, g, r, b); 
    }
    led_strip_refresh(ws2812_strip);
}

void bsp_led_clear(void)
{
    if (ws2812_strip == NULL) {
        ESP_LOGE(TAG, "WS2812 strip not initialized!");
        return;
    }
    
    for (int i = 0; i < WS2812_LED_COUNT; i++) {
        led_strip_set_pixel(ws2812_strip, i, 0, 0, 0);
    }
    led_strip_refresh(ws2812_strip);
}

void led_effect_task(void *arg)
{
    static uint8_t color_idx = 0;
    while (1)
    {
        if (xSemaphoreTake(led_effect_semaphore, portMAX_DELAY) == pdTRUE)
        {
            while (led_effect_running)
            {
                color_idx = (color_idx + 1) % 4;
                switch (color_idx)
                {
                    case 0: bsp_led_set_all(0, 255, 0, 128); break;  
                    case 1: bsp_led_set_all(0, 0, 255, 128); break;  
                    case 2: bsp_led_set_all(255, 255, 0, 128); break;  
                    case 3: bsp_led_set_all(255, 0, 255, 128); break;  
                }
                vTaskDelay(pdMS_TO_TICKS(300));
            }
            bsp_led_clear();
        }
    }
    vTaskDelete(NULL);
}