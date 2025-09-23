#include <stdio.h>
#include <cstring>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "esp_log.h"
#include "esp_err.h"
#include "driver/gpio.h"
#include "driver/i2c_master.h"
#include "sdkconfig.h"

#define TAG "main"

// PMU interrupt and I2C config
#define PMU_INPUT_PIN (gpio_num_t) CONFIG_PMU_INTERRUPT_PIN
#define PMU_INPUT_PIN_SEL (1ULL << PMU_INPUT_PIN)

#define I2C_MASTER_NUM (i2c_port_num_t) CONFIG_I2C_MASTER_PORT_NUM
#define I2C_MASTER_FREQ_HZ CONFIG_I2C_MASTER_FREQUENCY
#define I2C_MASTER_TIMEOUT_MS 1000

static i2c_master_bus_handle_t i2c_bus_handle = NULL;
static i2c_master_dev_handle_t pmu_dev_handle = NULL;
static QueueHandle_t gpio_evt_queue = NULL;

// Function declarations
extern esp_err_t pmu_init();
extern void pmu_isr_handler();

// ISR for GPIO
static void IRAM_ATTR pmu_irq_handler(void *arg) {
    uint32_t gpio_num = (uint32_t)arg;
    xQueueSendFromISR(gpio_evt_queue, &gpio_num, NULL);
}

// Array of I2C pin combinations to try for ESP32-S3
typedef struct {
    gpio_num_t sda;
    gpio_num_t scl;
    const char* description;
} i2c_pin_config_t;

static const i2c_pin_config_t i2c_pin_configs[] = {
    {GPIO_NUM_15, GPIO_NUM_14, "Original pins (SDA=15, SCL=14)"},
    {GPIO_NUM_21, GPIO_NUM_22, "Standard pins (SDA=21, SCL=22)"},  
    {GPIO_NUM_6, GPIO_NUM_7, "Alternative pins (SDA=6, SCL=7)"},
    {GPIO_NUM_8, GPIO_NUM_9, "Alternative pins (SDA=8, SCL=9)"},
    {GPIO_NUM_10, GPIO_NUM_11, "Alternative pins (SDA=10, SCL=11)"},
    {GPIO_NUM_17, GPIO_NUM_18, "Alternative pins (SDA=17, SCL=18)"},
    {GPIO_NUM_38, GPIO_NUM_39, "Alternative pins (SDA=38, SCL=39)"},
    {GPIO_NUM_35, GPIO_NUM_36, "Alternative pins (SDA=35, SCL=36)"},
    {GPIO_NUM_4, GPIO_NUM_5, "Alternative pins (SDA=4, SCL=5)"},
    {GPIO_NUM_1, GPIO_NUM_2, "Alternative pins (SDA=1, SCL=2)"},
};

#define NUM_PIN_CONFIGS (sizeof(i2c_pin_configs) / sizeof(i2c_pin_configs[0]))

// I2C init with pin testing
esp_err_t i2c_init_with_pins(gpio_num_t sda_pin, gpio_num_t scl_pin) {
    ESP_LOGI(TAG, "Trying I2C: SDA=%d, SCL=%d, Freq=%dHz", sda_pin, scl_pin, I2C_MASTER_FREQ_HZ);
    
    // Clean up previous bus if exists
    if (i2c_bus_handle != NULL) {
        if (pmu_dev_handle != NULL) {
            i2c_master_bus_rm_device(pmu_dev_handle);
            pmu_dev_handle = NULL;
        }
        i2c_del_master_bus(i2c_bus_handle);
        i2c_bus_handle = NULL;
    }
    
    i2c_master_bus_config_t bus_config = {
        .i2c_port = I2C_MASTER_NUM,
        .sda_io_num = sda_pin,
        .scl_io_num = scl_pin,
        .clk_source = I2C_CLK_SRC_DEFAULT,
        .glitch_ignore_cnt = 7,
        .intr_priority = 0,
        .trans_queue_depth = 0,
        .flags = {
            .enable_internal_pullup = 1,
            .allow_pd = 0
        }
    };

    esp_err_t ret = i2c_new_master_bus(&bus_config, &i2c_bus_handle);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to initialize I2C master bus: %s", esp_err_to_name(ret));
        return ret;
    }

    i2c_device_config_t dev_config = {
        .dev_addr_length = I2C_ADDR_BIT_LEN_7,
        .device_address = 0x34,
        .scl_speed_hz = I2C_MASTER_FREQ_HZ,
        .scl_wait_us = 0,
        .flags = {
            .disable_ack_check = 0
        }
    };

    ret = i2c_master_bus_add_device(i2c_bus_handle, &dev_config, &pmu_dev_handle);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to add PMU device to I2C bus: %s", esp_err_to_name(ret));
        return ret;
    }

    ESP_LOGI(TAG, "I2C bus and PMU device initialized successfully");
    return ESP_OK;
}

// PMU read function using new API
int pmu_register_read(uint8_t devAddr, uint8_t regAddr, uint8_t *data, uint8_t len) {
    if (pmu_dev_handle == NULL) {
        ESP_LOGE(TAG, "PMU device handle is NULL");
        return -1;
    }
    
    esp_err_t ret = i2c_master_transmit_receive(pmu_dev_handle, &regAddr, 1, data, len, I2C_MASTER_TIMEOUT_MS);
    if (ret != ESP_OK) {
        ESP_LOGD(TAG, "PMU READ FAILED! Register: 0x%02X, Error: %s", regAddr, esp_err_to_name(ret));
        return -1;
    }
    ESP_LOGD(TAG, "PMU READ OK: Register: 0x%02X, Length: %d", regAddr, len);
    return 0;
}

// PMU write function using new API
int pmu_register_write_byte(uint8_t devAddr, uint8_t regAddr, uint8_t *data, uint8_t len) {
    if (pmu_dev_handle == NULL) {
        ESP_LOGE(TAG, "PMU device handle is NULL");
        return -1;
    }
    
    uint8_t *buffer = (uint8_t *)malloc(len + 1);
    if (!buffer) {
        ESP_LOGE(TAG, "PMU WRITE: Memory allocation failed");
        return -1;
    }
    buffer[0] = regAddr;
    memcpy(&buffer[1], data, len);

    esp_err_t ret = i2c_master_transmit(pmu_dev_handle, buffer, len + 1, I2C_MASTER_TIMEOUT_MS);
    free(buffer);

    if (ret != ESP_OK) {
        ESP_LOGD(TAG, "PMU WRITE FAILED! Register: 0x%02X, Error: %s", regAddr, esp_err_to_name(ret));
        return -1;
    }
    ESP_LOGD(TAG, "PMU WRITE OK: Register: 0x%02X, Length: %d", regAddr, len);
    return 0;
}

// PMU event task
static void pmu_hander_task(void *args) {
    while (1) {
        pmu_isr_handler();
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}

extern "C" void app_main(void) {
    ESP_LOGI(TAG, "Starting I2C pin scanning for AXP2101...");
    
    bool pmu_found = false;
    
    // Try each pin configuration
    for (int i = 0; i < NUM_PIN_CONFIGS; i++) {
        ESP_LOGI(TAG, "=== Testing configuration %d: %s ===", i+1, i2c_pin_configs[i].description);
        
        esp_err_t ret = i2c_init_with_pins(i2c_pin_configs[i].sda, i2c_pin_configs[i].scl);
        if (ret == ESP_OK) {
            ESP_LOGI(TAG, "I2C initialized successfully, testing PMU...");
            
            // Try to initialize PMU
            ret = pmu_init();
            if (ret == ESP_OK) {
                ESP_LOGI(TAG, "✅ SUCCESS! PMU initialized with %s", i2c_pin_configs[i].description);
                pmu_found = true;
                break;
            } else {
                ESP_LOGW(TAG, "❌ PMU initialization failed with %s", i2c_pin_configs[i].description);
            }
        } else {
            ESP_LOGW(TAG, "❌ I2C initialization failed with %s", i2c_pin_configs[i].description);
        }
        
        vTaskDelay(pdMS_TO_TICKS(500)); // Small delay between attempts
    }
    
    if (!pmu_found) {
        ESP_LOGE(TAG, "❌ FAILED: Could not find working I2C configuration for AXP2101 PMU");
        ESP_LOGE(TAG, "Please check hardware connections and pin assignments");
        return;
    }
    
    ESP_LOGI(TAG, "🎉 PMU found and initialized successfully!");
    xTaskCreate(pmu_hander_task, "App/pwr", 4 * 1024, NULL, 10, NULL);
}