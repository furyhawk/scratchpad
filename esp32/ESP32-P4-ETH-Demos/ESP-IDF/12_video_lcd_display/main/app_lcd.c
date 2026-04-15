/*
 * SPDX-FileCopyrightText: 2024 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: CC0-1.0
 */
#include "esp_ldo_regulator.h"
#include "esp_lcd_mipi_dsi.h"
#include "esp_lcd_panel_ops.h"
#include "esp_log.h"
#include "esp_system.h"
#include "app_lcd.h"
#include "driver/gpio.h"
static const char *TAG = "app_lcd";

static esp_lcd_dsi_bus_handle_t mipi_dsi_bus;
static esp_lcd_panel_io_handle_t mipi_dbi_io;
static esp_lcd_panel_handle_t display_handle;

esp_err_t app_lcd_init(esp_lcd_panel_handle_t *panel_handle)
{

    bsp_lcd_handles_t lcd_panels = {0};
    bsp_display_new_with_handles(NULL, &lcd_panels);
    bsp_display_backlight_on();

    mipi_dsi_bus = lcd_panels.mipi_dsi_bus;
    mipi_dbi_io = lcd_panels.io;
    display_handle = lcd_panels.panel;

    *panel_handle = display_handle;

    return ESP_OK;
}
