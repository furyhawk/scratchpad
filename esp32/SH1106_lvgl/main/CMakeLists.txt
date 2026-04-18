idf_component_register(SRCS "main.c"
                    INCLUDE_DIRS "."
                    REQUIRES lvgl ssd1306 ssd1327 driver esp_driver_spi esp_driver_i2c)