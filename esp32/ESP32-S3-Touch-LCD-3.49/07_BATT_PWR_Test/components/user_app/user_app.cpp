#include <stdio.h>
#include "user_app.h"
#include "lvgl.h"
#include "gui_guider.h"
#include "esp_timer.h"
#include "esp_log.h"
#include "button_bsp.h"
#include "esp_log.h"
#include "esp_system.h"
#include "user_config.h"
#include "gui_guider.h"
#include "esp_io_expander_tca9554.h"
#include "driver/gpio.h"

lv_ui src_ui;
esp_io_expander_handle_t io_expander = NULL;
static bool is_vbatpowerflag = false;


void power_Test(void *arg)
{
	if(gpio_get_level(GPIO_NUM_16))
	{
		is_vbatpowerflag = true;
	}
	vTaskDelete(NULL); 
}

static void tca9554_init(void)
{
  	i2c_master_bus_handle_t tca9554_i2c_bus_ = NULL;
  	ESP_ERROR_CHECK(i2c_master_get_bus_handle(0,&tca9554_i2c_bus_));
  	esp_io_expander_new_i2c_tca9554(tca9554_i2c_bus_, ESP_IO_EXPANDER_I2C_TCA9554_ADDRESS_000, &io_expander);
	esp_io_expander_set_dir(io_expander, IO_EXPANDER_PIN_NUM_6, IO_EXPANDER_OUTPUT);
  	esp_io_expander_set_level(io_expander, IO_EXPANDER_PIN_NUM_6, 1);
}

static void example_button_pwr_task(void* arg)
{
  	lv_ui *ui = (lv_ui *)arg;
  	for (;;)
  	{
  	  	EventBits_t even = xEventGroupWaitBits(pwr_groups,set_bit_all,pdTRUE,pdFALSE,pdMS_TO_TICKS(2 * 1000));
  	  	if(get_bit_button(even,0))
  	  	{

  	  	}
  	  	else if(get_bit_button(even,1)) //长按
  	  	{
			if(is_vbatpowerflag)
			{
				is_vbatpowerflag = false;
				esp_io_expander_set_level(io_expander, IO_EXPANDER_PIN_NUM_6, 0);
				lv_label_set_text(src_ui.screen_label_1, "OFF");
			}
  	  	}
  	  	else if(get_bit_button(even,2))
  	  	{
			if(!is_vbatpowerflag)
			{
				is_vbatpowerflag = true;
			}
  	  	}
  	}
}

void user_app_init(void)
{
	setup_ui(&src_ui);
	lv_label_set_text(src_ui.screen_label_1, "ON");
	tca9554_init();
  	button_Init();

  	xTaskCreatePinnedToCore(example_button_pwr_task, "example_button_pwr_task", 4 * 1024, &src_ui, 2, NULL,1);      //按钮事件     
	xTaskCreatePinnedToCore(power_Test, "power_Test", 4 * 1024, NULL, 3, NULL,1);                           		//audio
}