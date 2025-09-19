#include <stdio.h>
#include "user_app.h"
#include "lvgl.h"
#include "esp_timer.h"
#include "esp_log.h"
#include "esp_log.h"
#include "esp_system.h"
#include "user_config.h"
#include "gui_guider.h"
#include "esp_io_expander_tca9554.h"
#include "user_audio_bsp.h"
#include "lcd_bl_pwm_bsp.h"

lv_ui src_ui;
static EventGroupHandle_t lvgl_button_groups;
static uint8_t *audio_ptr = NULL;
esp_io_expander_handle_t io_expander = NULL;
static bool is_Music = true;

static void audio_Test_Callback(lv_event_t *e)
{
	assert(audio_ptr);
	lv_event_code_t code = lv_event_get_code(e);
  	lv_ui *ui = (lv_ui *)e->user_data;
  	lv_obj_t * module = e->current_target;
  	switch (code)
  	{
  	  case LV_EVENT_CLICKED:
  	  {
  	    if(module == ui->screen_btn_1)
  	    {
			xEventGroupSetBits(lvgl_button_groups,0x01);
  	    }
		if(module == ui->screen_btn_2)
		{
			xEventGroupSetBits(lvgl_button_groups,0x02);
		}
		if(module == ui->screen_btn_3)
		{
			is_Music = true;
			xEventGroupSetBits(lvgl_button_groups,0x04);
		}
		if(module == ui->screen_btn_4)
		{
			is_Music = false;
		}
  	    break;
  	  }
  	  default:
  	    break;
  	}
}

void i2s_audio_Test(void *arg)
{
	lv_ui *ui = (lv_ui *)arg;

	for(;;)
	{
		EventBits_t even = xEventGroupWaitBits(lvgl_button_groups,0x00ffffff,pdTRUE,pdFALSE,pdMS_TO_TICKS(8 * 1000));
		if(even & 0x01)
		{
			lv_label_set_text(ui->screen_label_2, "正在录音");
			lv_label_set_text(ui->screen_label_3, "Recording...");

			audio_playback_read(audio_ptr,192 * 1000);
			lv_label_set_text(ui->screen_label_2, "录音完成");
			lv_label_set_text(ui->screen_label_3, "Rec Done");
		}
		else if(even & 0x02)
		{
			lv_label_set_text(ui->screen_label_2, "正在播放");
			lv_label_set_text(ui->screen_label_3, "Playing...");
			audio_playback_write(audio_ptr,192 * 1000);
			lv_label_set_text(ui->screen_label_2, "播放完成");
			lv_label_set_text(ui->screen_label_3, "Play Done");
		}
		else if(even & 0x04)
		{
			lv_label_set_text(ui->screen_label_2, "正在播放音乐");
			lv_label_set_text(ui->screen_label_3, "Play Music");
			audio_playback_set_vol(90);
			uint32_t bytes_sizt;
			size_t bytes_write = 0;
			uint8_t *data_ptr = i2s_get_handle(&bytes_sizt);
			while (bytes_write < bytes_sizt)
            {
                audio_playback_write(data_ptr, 256);
                data_ptr += 256;
                bytes_write += 256;
				if(!is_Music)
				break;
            }
			audio_playback_set_vol(100);
			lv_label_set_text(ui->screen_label_2, "播放完成");
			lv_label_set_text(ui->screen_label_3, "Play Done");
		}
		else
		{
			lv_label_set_text(ui->screen_label_2, "等待操作");
			lv_label_set_text(ui->screen_label_3, "Idle");
		}
	}
}

static void tca9554_init(void)
{
  	i2c_master_bus_handle_t tca9554_i2c_bus_ = NULL;
  	ESP_ERROR_CHECK(i2c_master_get_bus_handle(0,&tca9554_i2c_bus_));
  	esp_io_expander_new_i2c_tca9554(tca9554_i2c_bus_, ESP_IO_EXPANDER_I2C_TCA9554_ADDRESS_000, &io_expander);
	esp_io_expander_set_dir(io_expander, IO_EXPANDER_PIN_NUM_7, IO_EXPANDER_OUTPUT);
  	esp_io_expander_set_level(io_expander, IO_EXPANDER_PIN_NUM_7, 1);
}

void user_app_init(void)
{
	lvgl_button_groups = xEventGroupCreate();
	audio_ptr = (uint8_t *)heap_caps_malloc(288 * 1000 * sizeof(uint8_t), MALLOC_CAP_SPIRAM);
	setup_ui(&src_ui);
	lv_label_set_text(src_ui.screen_label_2, "等待操作");
	lv_label_set_text(src_ui.screen_label_3, "Idle");
  	lcd_bl_pwm_bsp_init(LCD_PWM_MODE_255);
	user_audio_bsp_init();
	audio_play_init();
	tca9554_init();
  	
	xTaskCreatePinnedToCore(i2s_audio_Test, "i2s_audio_Test", 4 * 1024, &src_ui, 3, NULL,1);                           //audio        
	/*even add*/
  	lv_obj_add_event_cb(src_ui.screen_btn_1, audio_Test_Callback, LV_EVENT_ALL, &src_ui); 
	lv_obj_add_event_cb(src_ui.screen_btn_2, audio_Test_Callback, LV_EVENT_ALL, &src_ui);
	lv_obj_add_event_cb(src_ui.screen_btn_3, audio_Test_Callback, LV_EVENT_ALL, &src_ui);
	lv_obj_add_event_cb(src_ui.screen_btn_4, audio_Test_Callback, LV_EVENT_ALL, &src_ui);
}
