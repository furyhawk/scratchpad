idf_component_register(
    SRCS "ssd1327.c"
    INCLUDE_DIRS "include"
    REQUIRES esp_driver_i2c esp_driver_gpio esp_timer
)
