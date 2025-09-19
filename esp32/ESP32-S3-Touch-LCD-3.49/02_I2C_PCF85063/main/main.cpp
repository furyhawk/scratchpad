#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "i2c_bsp.h"
#include "user_config.h"
#include "i2c_equipment.h"

#include "esp_io_expander_tca9554.h"

static void gpio_init(void)
{
    esp_io_expander_handle_t io_expander = NULL;
    i2c_master_bus_handle_t tca9554_i2c_bus_ = NULL;

    ESP_ERROR_CHECK(i2c_master_get_bus_handle(0,&tca9554_i2c_bus_));

  	esp_io_expander_new_i2c_tca9554(tca9554_i2c_bus_, ESP_IO_EXPANDER_I2C_TCA9554_ADDRESS_000, &io_expander);
	esp_io_expander_set_dir(io_expander, IO_EXPANDER_PIN_NUM_1, IO_EXPANDER_OUTPUT);
  	esp_io_expander_set_level(io_expander, IO_EXPANDER_PIN_NUM_1, 0);
}

extern "C" void app_main(void)
{
  	i2c_master_init();
	gpio_init();
  	i2c_rtc_setup();
  	i2c_rtc_setTime(2025,9,9,20,15,30);
  	xTaskCreatePinnedToCore(i2c_rtc_loop_task, "i2c_rtc_loop_task", 3 * 1024, NULL , 2, NULL,0); 
}
