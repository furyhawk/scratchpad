#include "LIB_Config.h"


int main(void) 
{
	system_init();
	
	ssd1305_clear_screen(0xFF);
	delay_ms(1000);
	ssd1305_clear_screen(0x00);
	ssd1305_display_string(0, 0, "2.23inch OLED", 16, 1);
	ssd1305_refresh_gram();
	delay_ms(1000);
	ssd1305_clear_screen(0x00);

	ssd1305_draw_bitmap(0, 2, &c_chSingal816[0], 16, 8);
	ssd1305_draw_bitmap(24, 2, &c_chBluetooth88[0], 8, 8);
	ssd1305_draw_bitmap(40, 2, &c_chMsg816[0], 16, 8);
	ssd1305_draw_bitmap(64, 2, &c_chGPRS88[0], 8, 8);
	ssd1305_draw_bitmap(90, 2, &c_chAlarm88[0], 8, 8);
	ssd1305_draw_bitmap(112, 2, &c_chBat816[0], 16, 8);
	
	ssd1305_draw_1616char(0,16, '2');
	ssd1305_draw_1616char(16,16, '3');
	ssd1305_draw_1616char(32,16, ':');
	ssd1305_draw_1616char(48,16, '5');
	ssd1305_draw_1616char(64,16, '6');
	ssd1305_draw_1616char(80,16, ':');
	ssd1305_draw_1616char(96,16, '5');
	ssd1305_draw_1616char(112,16, '8');
	ssd1305_refresh_gram();
	while (1) {

	}
}

/*-------------------------------END OF FILE-------------------------------*/

