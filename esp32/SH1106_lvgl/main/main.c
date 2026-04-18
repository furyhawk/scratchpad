#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include "esp_timer.h"
#include "lvgl.h"
#include "sdkconfig.h"
#include "ssd1327.h"
#include "ssd1306.h"

#if CONFIG_BLINK_DISPLAY_SSD1327
#define OLED_WIDTH CONFIG_BLINK_SSD1327_WIDTH
#define OLED_HEIGHT CONFIG_BLINK_SSD1327_HEIGHT
#else
#define OLED_WIDTH 128
#if CONFIG_SSD1306_128x32
#define OLED_HEIGHT 32
#else
#define OLED_HEIGHT 64
#endif
#endif

#define LVGL_DRAW_BUF_LINES 12
#define LVGL_TASK_STACK_SIZE 6144
#define LVGL_TASK_PRIORITY 5

#if CONFIG_BLINK_DISPLAY_SSD1327
static ssd1327_t s_oled1327;
static uint8_t s_oled1327_buffer[OLED_WIDTH * OLED_HEIGHT / 2];
#else
static SSD1306_t s_oled;
static uint8_t s_oled_buffer[OLED_WIDTH * OLED_HEIGHT / 8];
#endif
static uint8_t s_lvgl_buf[OLED_WIDTH * LVGL_DRAW_BUF_LINES * sizeof(uint16_t)];

static lv_obj_t * s_root;
static lv_obj_t * s_label;
static lv_obj_t * s_bar;
static lv_obj_t * s_hint;
static lv_obj_t * s_dot;

static int s_shift_index;
static int s_burnin_tick;
static bool s_invert;
static int s_dot_x;
static int s_dot_y;
static int s_dot_dx = 1;
static int s_dot_dy = 1;

static const int8_t s_shift_pattern[][2] = {
	{0, 0}, {1, 0}, {1, 1}, {0, 1}, {-1, 1}, {-1, 0}, {-1, -1}, {0, -1}, {1, -1}
};

static inline bool pixel_on_from_rgb565(uint16_t c)
{
	return c != 0;
}

#if !CONFIG_BLINK_DISPLAY_SSD1327
static void oled_set_pixel(int32_t x, int32_t y, bool on)
{
	if (x < 0 || x >= OLED_WIDTH || y < 0 || y >= OLED_HEIGHT) {
		return;
	}

	uint32_t index = (uint32_t)x + ((uint32_t)y / 8U) * OLED_WIDTH;
	uint8_t bit = (uint8_t)(1U << (y & 0x7));
	if (on) {
		s_oled_buffer[index] |= bit;
	} else {
		s_oled_buffer[index] &= (uint8_t)~bit;
	}
}
#endif

#if CONFIG_BLINK_DISPLAY_SSD1327
static uint8_t rgb565_to_gray4(uint16_t c)
{
	uint8_t r = (uint8_t)((c >> 11) & 0x1F);
	uint8_t g = (uint8_t)((c >> 5) & 0x3F);
	uint8_t b = (uint8_t)(c & 0x1F);

	uint16_t r8 = (uint16_t)(r * 255U / 31U);
	uint16_t g8 = (uint16_t)(g * 255U / 63U);
	uint16_t b8 = (uint16_t)(b * 255U / 31U);
	uint16_t y = (uint16_t)((r8 * 30U + g8 * 59U + b8 * 11U) / 100U);
	return (uint8_t)(y >> 4);
}

static void ssd1327_set_pixel_gray4(int32_t x, int32_t y, uint8_t gray4)
{
	if (x < 0 || x >= OLED_WIDTH || y < 0 || y >= OLED_HEIGHT) {
		return;
	}

	uint32_t pixel_index = (uint32_t)y * (uint32_t)OLED_WIDTH + (uint32_t)x;
	uint32_t byte_index = pixel_index >> 1;
	if ((pixel_index & 1U) == 0U) {
		s_oled1327_buffer[byte_index] = (uint8_t)((s_oled1327_buffer[byte_index] & 0x0F) | (gray4 << 4));
	} else {
		s_oled1327_buffer[byte_index] = (uint8_t)((s_oled1327_buffer[byte_index] & 0xF0) | (gray4 & 0x0F));
	}
}
#endif

static void lvgl_flush_cb(lv_display_t * disp, const lv_area_t * area, uint8_t * px_map)
{
	int32_t width = lv_area_get_width(area);
	int32_t height = lv_area_get_height(area);
	const uint16_t * rgb565 = (const uint16_t *)px_map;

	#if CONFIG_BLINK_DISPLAY_SSD1327
	for (int32_t y = 0; y < height; y++) {
		for (int32_t x = 0; x < width; x++) {
			uint16_t c = rgb565[y * width + x];
			ssd1327_set_pixel_gray4(area->x1 + x, area->y1 + y, rgb565_to_gray4(c));
		}
	}
	ESP_ERROR_CHECK(ssd1327_flush_4bit(&s_oled1327, s_oled1327_buffer, sizeof(s_oled1327_buffer)));
	#else
	for (int32_t y = 0; y < height; y++) {
		for (int32_t x = 0; x < width; x++) {
			uint16_t c = rgb565[y * width + x];
			oled_set_pixel(area->x1 + x, area->y1 + y, pixel_on_from_rgb565(c));
		}
	}

	ssd1306_set_buffer(&s_oled, s_oled_buffer);
	ssd1306_show_buffer(&s_oled);
	#endif
	lv_display_flush_ready(disp);
}

static void lvgl_tick_cb(void * arg)
{
	(void)arg;
	lv_tick_inc(2);
}

static void apply_theme(bool invert)
{
	lv_obj_t * scr = lv_screen_active();
	lv_color_t bg = invert ? lv_color_hex(0xFFFFFF) : lv_color_hex(0x000000);
	lv_color_t fg = invert ? lv_color_hex(0x000000) : lv_color_hex(0xFFFFFF);

	lv_obj_set_style_bg_color(scr, bg, 0);
	lv_obj_set_style_bg_opa(scr, LV_OPA_COVER, 0);
	lv_obj_set_style_text_color(s_label, fg, 0);
	lv_obj_set_style_text_color(s_hint, fg, 0);
	lv_obj_set_style_bg_color(s_dot, fg, 0);
	lv_obj_set_style_bg_opa(s_dot, LV_OPA_COVER, 0);
	lv_obj_set_style_bg_color(s_bar, bg, LV_PART_MAIN);
	lv_obj_set_style_border_color(s_bar, fg, LV_PART_MAIN);
	lv_obj_set_style_border_width(s_bar, 1, LV_PART_MAIN);
	lv_obj_set_style_bg_color(s_bar, fg, LV_PART_INDICATOR);
}

static void ui_timer_cb(lv_timer_t * timer)
{
	(void)timer;
	static int value = 0;
	static int dir = 1;
	char text[32];

	value += dir * 5;
	if (value >= 100) {
		value = 100;
		dir = -1;
	} else if (value <= 0) {
		value = 0;
		dir = 1;
	}

	lv_bar_set_value(s_bar, value, LV_ANIM_OFF);
	snprintf(text, sizeof(text), "LVGL Demo %3d%%", value);
	lv_label_set_text(s_label, text);

	s_burnin_tick++;
	s_shift_index = (s_shift_index + 1) % (int)(sizeof(s_shift_pattern) / sizeof(s_shift_pattern[0]));
	lv_obj_set_pos(s_root, s_shift_pattern[s_shift_index][0], s_shift_pattern[s_shift_index][1]);

	if ((s_burnin_tick % 40) == 0) {
		s_invert = !s_invert;
		apply_theme(s_invert);
	}

	int max_x = OLED_WIDTH - 3;
	int max_y = OLED_HEIGHT - 3;
	s_dot_x += s_dot_dx;
	s_dot_y += s_dot_dy;
	if (s_dot_x <= 0 || s_dot_x >= max_x) {
		s_dot_dx = -s_dot_dx;
		s_dot_x += s_dot_dx;
	}
	if (s_dot_y <= 0 || s_dot_y >= max_y) {
		s_dot_dy = -s_dot_dy;
		s_dot_y += s_dot_dy;
	}
	lv_obj_set_pos(s_dot, s_dot_x, s_dot_y);
}

static void init_oled(void)
{
#if CONFIG_BLINK_DISPLAY_SSD1327
	// Map menuconfig I2C address choice to actual address
#if CONFIG_BLINK_SSD1327_I2C_ADDR_3C
	const uint8_t ssd1327_i2c_addr = 0x3C;
#else
	const uint8_t ssd1327_i2c_addr = 0x3D;
#endif

	// Map menuconfig I2C port number to port enum
#if CONFIG_BLINK_SSD1327_I2C_PORT == 0
	const i2c_port_t ssd1327_i2c_port = I2C_NUM_0;
#else
	const i2c_port_t ssd1327_i2c_port = I2C_NUM_1;
#endif

	ESP_ERROR_CHECK(ssd1327_init(&s_oled1327,
							 OLED_WIDTH,
							 OLED_HEIGHT,
							 CONFIG_SDA_GPIO,
							 CONFIG_SCL_GPIO,
							 CONFIG_RESET_GPIO,
							 ssd1327_i2c_addr,
							 ssd1327_i2c_port));
	memset(s_oled1327_buffer, 0, sizeof(s_oled1327_buffer));
	ESP_ERROR_CHECK(ssd1327_flush_4bit(&s_oled1327, s_oled1327_buffer, sizeof(s_oled1327_buffer)));
#else
#if CONFIG_I2C_INTERFACE
	i2c_master_init(&s_oled, CONFIG_SDA_GPIO, CONFIG_SCL_GPIO, CONFIG_RESET_GPIO);
#elif CONFIG_SPI_INTERFACE
	spi_master_init(&s_oled, CONFIG_MOSI_GPIO, CONFIG_SCLK_GPIO, CONFIG_CS_GPIO, CONFIG_DC_GPIO, CONFIG_RESET_GPIO);
#else
#error "Select I2C or SPI interface for ssd1306 in menuconfig"
#endif

	ssd1306_init(&s_oled, OLED_WIDTH, OLED_HEIGHT);
	memset(s_oled_buffer, 0, sizeof(s_oled_buffer));
	ssd1306_set_buffer(&s_oled, s_oled_buffer);
	ssd1306_show_buffer(&s_oled);
#endif
}

static void create_demo_ui(void)
{
	lv_obj_t * scr = lv_screen_active();

	s_root = lv_obj_create(scr);
	lv_obj_remove_style_all(s_root);
	lv_obj_set_size(s_root, OLED_WIDTH, OLED_HEIGHT);
	lv_obj_set_pos(s_root, 0, 0);

	s_label = lv_label_create(s_root);
	lv_label_set_text(s_label, "LVGL Demo 0%");
	lv_obj_align(s_label, LV_ALIGN_TOP_MID, 0, 2);

	s_bar = lv_bar_create(s_root);
	lv_obj_set_size(s_bar, OLED_WIDTH - 12, 14);
	lv_obj_align(s_bar, LV_ALIGN_BOTTOM_MID, 0, -4);
	lv_bar_set_range(s_bar, 0, 100);
	lv_bar_set_value(s_bar, 0, LV_ANIM_OFF);

	s_hint = lv_label_create(s_root);
#if CONFIG_BLINK_DISPLAY_SSD1327
	lv_label_set_text(s_hint, "SSD1327 cfg + LVGL");
#else
	lv_label_set_text(s_hint, "SH1106 + LVGL");
#endif
	lv_obj_align(s_hint, LV_ALIGN_CENTER, 0, -4);

	s_dot = lv_obj_create(s_root);
	lv_obj_remove_style_all(s_dot);
	lv_obj_set_size(s_dot, 3, 3);
	s_dot_x = OLED_WIDTH / 2;
	s_dot_y = OLED_HEIGHT / 2;
	lv_obj_set_pos(s_dot, s_dot_x, s_dot_y);

	s_invert = false;
	apply_theme(s_invert);

	lv_timer_create(ui_timer_cb, 200, NULL);
}

static void lvgl_task(void * arg)
{
	(void)arg;
	while (1) {
		lv_timer_handler();
		vTaskDelay(pdMS_TO_TICKS(10));
	}
}

void app_main(void)
{
	#if CONFIG_BLINK_DISPLAY_SSD1327
	printf("LVGL %d.%d.%d with SSD1327\n", LVGL_VERSION_MAJOR, LVGL_VERSION_MINOR, LVGL_VERSION_PATCH);
	#else
	printf("LVGL %d.%d.%d with SH1106\n", LVGL_VERSION_MAJOR, LVGL_VERSION_MINOR, LVGL_VERSION_PATCH);
	#endif

	init_oled();
	lv_init();

	lv_display_t * disp = lv_display_create(OLED_WIDTH, OLED_HEIGHT);
	lv_display_set_color_format(disp, LV_COLOR_FORMAT_RGB565);
	lv_display_set_flush_cb(disp, lvgl_flush_cb);
	lv_display_set_buffers(disp, s_lvgl_buf, NULL, sizeof(s_lvgl_buf), LV_DISPLAY_RENDER_MODE_PARTIAL);

	const esp_timer_create_args_t tick_timer_args = {
		.callback = lvgl_tick_cb,
		.name = "lvgl_tick"
	};
	esp_timer_handle_t tick_timer;
	ESP_ERROR_CHECK(esp_timer_create(&tick_timer_args, &tick_timer));
	ESP_ERROR_CHECK(esp_timer_start_periodic(tick_timer, 2000));

	create_demo_ui();

	configASSERT(xTaskCreate(lvgl_task,
						 "lvgl_task",
						 LVGL_TASK_STACK_SIZE,
						 NULL,
						 LVGL_TASK_PRIORITY,
						 NULL) == pdPASS);

	vTaskDelete(NULL);
}