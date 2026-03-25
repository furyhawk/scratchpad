#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/pio.h"
#include "hardware/clocks.h"
#include "ws2812.pio.h"

// Number of RGB lights
#define NUM_LEDS 25
// RGB light maximum brightness
#define MAX_LUM  20 

uint32_t urgb_u32(uint8_t red, uint8_t green, uint8_t blue)
{
    uint32_t mask = (red << 24) | (green << 16) | (blue << 8);
    return mask;
}
void put_pixel(uint32_t pixel_grb)
{
    pio_sm_put_blocking(pio0, 0, pixel_grb);
}

// Send the same color to all RGB lights
void show_color(uint32_t color) {
    for (int i = 0; i < NUM_LEDS; ++i) {
        put_pixel(color);
    }
}

int main() {
    stdio_init_all();
    sleep_ms(500);

    printf("WS2812 Test - All LEDs same color\n");

    PIO pio = pio0;
    int sm = 0;
    uint offset = pio_add_program(pio, &ws2812_program);

    // Outputting on Pin(16)
    ws2812_program_init(pio, sm, offset, 16, 800000, false);

    while (true) {
        // Blue -> Red Gradient
        for (int i = 0; i <= MAX_LUM; ++i) {
            uint8_t r = i;
            uint8_t g = 0;
            uint8_t b = MAX_LUM - i;
            // R=i, G=0, B=MAX_LUM -i
            show_color(urgb_u32(r, g, b));
            sleep_ms(20);
        }

        // Red -> Green Gradient
        for (int i = 0; i <= MAX_LUM; ++i) {
            uint8_t r = MAX_LUM - i;
            uint8_t g = i;
            uint8_t b = 0;
            // R=MAX_LUM -i, G=i,B=0
            show_color(urgb_u32(r, g, b));
            sleep_ms(20);
        }

        // Green -> Blue Gradient
        for (int i = 0; i <= MAX_LUM; ++i) {
            uint8_t r = 0;
            uint8_t g = MAX_LUM - i;
            uint8_t b = i;
            // R=0, G=MAX_LUM -i, B=i
            show_color(urgb_u32(r, g, b));
            sleep_ms(20);
        }
    }
}
