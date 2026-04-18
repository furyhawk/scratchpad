#pragma once

#include <stddef.h>
#include <stdint.h>

#include "driver/gpio.h"
#include "driver/i2c_master.h"
#include "esp_err.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    i2c_master_bus_handle_t bus;
    i2c_master_dev_handle_t dev;
    uint8_t address;
    int width;
    int height;
} ssd1327_t;

esp_err_t ssd1327_init(ssd1327_t *handle,
                       int width,
                       int height,
                       gpio_num_t sda,
                       gpio_num_t scl,
                       gpio_num_t reset,
                       uint8_t i2c_address,
                       i2c_port_num_t port);

esp_err_t ssd1327_flush_4bit(ssd1327_t *handle, const uint8_t *buffer, size_t len);

#ifdef __cplusplus
}
#endif
