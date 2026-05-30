file(GLOB_RECURSE SRC_FILES "*.c")

idf_component_register(SRCS ${SRC_FILES}
                    INCLUDE_DIRS "."
                    REQUIRES "esp_lcd" "driver" "esp_adc" "fatfs" "nvs_flash" "lwip" "esp_wifi" "espressif__esp_codec_dev" "teriyakigod__esp_lcd_st7735"  "led_strip")
