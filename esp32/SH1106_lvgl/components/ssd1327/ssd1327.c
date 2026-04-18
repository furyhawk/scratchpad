#include "ssd1327.h"

#include <string.h>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include "esp_check.h"

#define SSD1327_CONTROL_CMD 0x00
#define SSD1327_CONTROL_DATA 0x40

#define SSD1327_CMD_SET_COL_ADDR 0x15
#define SSD1327_CMD_SET_ROW_ADDR 0x75
#define SSD1327_CMD_WRITE_RAM 0x5C
#define SSD1327_CMD_SET_CONTRAST 0x81
#define SSD1327_CMD_SET_REMAP 0xA0
#define SSD1327_CMD_SET_START_LINE 0xA1
#define SSD1327_CMD_SET_DISPLAY_OFFSET 0xA2
#define SSD1327_CMD_SET_DISPLAY_MODE_NORMAL 0xA4
#define SSD1327_CMD_SET_MUX_RATIO 0xA8
#define SSD1327_CMD_FUNC_SELECT 0xAB
#define SSD1327_CMD_DISPLAY_OFF 0xAE
#define SSD1327_CMD_DISPLAY_ON 0xAF
#define SSD1327_CMD_PHASE_LENGTH 0xB1
#define SSD1327_CMD_FRONT_CLOCK_DIV 0xB3
#define SSD1327_CMD_SET_GPIO 0xB5
#define SSD1327_CMD_SECOND_PRECHARGE 0xB6
#define SSD1327_CMD_PRECHARGE_VOLTAGE 0xBC
#define SSD1327_CMD_COM_DESELECT_LEVEL 0xBE
#define SSD1327_CMD_COMMAND_LOCK 0xFD

#define I2C_FREQ_HZ 400000
#define I2C_TIMEOUT_MS 100

static esp_err_t ssd1327_send_cmd(ssd1327_t *handle, const uint8_t *cmd, size_t len)
{
    uint8_t chunk[65];
    chunk[0] = SSD1327_CONTROL_CMD;

    size_t pos = 0;
    while (pos < len) {
        size_t n = len - pos;
        if (n > 64) {
            n = 64;
        }

        memcpy(&chunk[1], &cmd[pos], n);
        ESP_RETURN_ON_ERROR(i2c_master_transmit(handle->dev, chunk, n + 1, I2C_TIMEOUT_MS), "ssd1327", "cmd tx failed");
        pos += n;
    }

    return ESP_OK;
}

static esp_err_t ssd1327_send_data(ssd1327_t *handle, const uint8_t *data, size_t len)
{
    uint8_t chunk[65];
    chunk[0] = SSD1327_CONTROL_DATA;

    size_t pos = 0;
    while (pos < len) {
        size_t n = len - pos;
        if (n > 64) {
            n = 64;
        }

        memcpy(&chunk[1], &data[pos], n);
        ESP_RETURN_ON_ERROR(i2c_master_transmit(handle->dev, chunk, n + 1, I2C_TIMEOUT_MS), "ssd1327", "data tx failed");
        pos += n;
    }

    return ESP_OK;
}

esp_err_t ssd1327_init(ssd1327_t *handle,
                       int width,
                       int height,
                       gpio_num_t sda,
                       gpio_num_t scl,
                       gpio_num_t reset,
                       uint8_t i2c_address,
                       i2c_port_num_t port)
{
    ESP_RETURN_ON_FALSE(handle != NULL, ESP_ERR_INVALID_ARG, "ssd1327", "null handle");
    ESP_RETURN_ON_FALSE(width > 0 && height > 0, ESP_ERR_INVALID_ARG, "ssd1327", "invalid size");

    i2c_master_bus_config_t bus_cfg = {
        .clk_source = I2C_CLK_SRC_DEFAULT,
        .i2c_port = port,
        .scl_io_num = scl,
        .sda_io_num = sda,
        .glitch_ignore_cnt = 7,
        .flags.enable_internal_pullup = true,
    };

    ESP_RETURN_ON_ERROR(i2c_new_master_bus(&bus_cfg, &handle->bus), "ssd1327", "new bus failed");

    i2c_device_config_t dev_cfg = {
        .dev_addr_length = I2C_ADDR_BIT_LEN_7,
        .device_address = i2c_address,
        .scl_speed_hz = I2C_FREQ_HZ,
    };

    ESP_RETURN_ON_ERROR(i2c_master_bus_add_device(handle->bus, &dev_cfg, &handle->dev), "ssd1327", "add device failed");

    handle->address = i2c_address;
    handle->width = width;
    handle->height = height;

    if (reset >= 0) {
        gpio_reset_pin(reset);
        gpio_set_direction(reset, GPIO_MODE_OUTPUT);
        gpio_set_level(reset, 0);
        vTaskDelay(pdMS_TO_TICKS(20));
        gpio_set_level(reset, 1);
        vTaskDelay(pdMS_TO_TICKS(20));
    }

    const uint8_t init_seq[] = {
        SSD1327_CMD_COMMAND_LOCK, 0x12,
        SSD1327_CMD_DISPLAY_OFF,
        SSD1327_CMD_SET_COL_ADDR, 0x00, (uint8_t)((width / 2) - 1),
        SSD1327_CMD_SET_ROW_ADDR, 0x00, (uint8_t)(height - 1),
        SSD1327_CMD_SET_CONTRAST, 0x80,
        SSD1327_CMD_SET_REMAP, 0x51,
        SSD1327_CMD_SET_START_LINE, 0x00,
        SSD1327_CMD_SET_DISPLAY_OFFSET, 0x00,
        SSD1327_CMD_SET_DISPLAY_MODE_NORMAL,
        SSD1327_CMD_SET_MUX_RATIO, (uint8_t)(height - 1),
        SSD1327_CMD_FUNC_SELECT, 0x01,
        SSD1327_CMD_FRONT_CLOCK_DIV, 0x91,
        SSD1327_CMD_PHASE_LENGTH, 0xF1,
        SSD1327_CMD_SET_GPIO, 0x00,
        SSD1327_CMD_SECOND_PRECHARGE, 0x0F,
        SSD1327_CMD_PRECHARGE_VOLTAGE, 0x08,
        SSD1327_CMD_COM_DESELECT_LEVEL, 0x07,
        SSD1327_CMD_DISPLAY_ON,
    };

    return ssd1327_send_cmd(handle, init_seq, sizeof(init_seq));
}

esp_err_t ssd1327_flush_4bit(ssd1327_t *handle, const uint8_t *buffer, size_t len)
{
    ESP_RETURN_ON_FALSE(handle != NULL && buffer != NULL, ESP_ERR_INVALID_ARG, "ssd1327", "invalid args");

    size_t expected = (size_t)handle->width * (size_t)handle->height / 2U;
    ESP_RETURN_ON_FALSE(len >= expected, ESP_ERR_INVALID_SIZE, "ssd1327", "buffer too small");

    uint8_t addr_seq[] = {
        SSD1327_CMD_SET_COL_ADDR, 0x00, (uint8_t)((handle->width / 2) - 1),
        SSD1327_CMD_SET_ROW_ADDR, 0x00, (uint8_t)(handle->height - 1),
        SSD1327_CMD_WRITE_RAM,
    };

    ESP_RETURN_ON_ERROR(ssd1327_send_cmd(handle, addr_seq, sizeof(addr_seq)), "ssd1327", "set addr failed");
    return ssd1327_send_data(handle, buffer, expected);
}
