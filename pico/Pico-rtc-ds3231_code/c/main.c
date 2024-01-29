#include "ds3231.h"
#include <stdio.h>
#include "pico/stdlib.h"

/*
 	the first verison use i2c1(GP6,GP7),
	and the new vesion use i2c0(GP20,GP21).
	change it in ds3231/ds3231.h file
*/

extern char buf[];
extern char *week[];

int main()  
{
	int i = 0;
	stdio_init_all();
	i2c_init(I2C_PORT,100*1000);
	gpio_set_function(I2C_SDA,GPIO_FUNC_I2C);
	gpio_set_function(I2C_SCL,GPIO_FUNC_I2C);
	gpio_pull_up(I2C_SDA);
	gpio_pull_up(I2C_SCL);
    printf("DS3231 Test Program ...\n\n"); 
   	
	//ds3231SetTime(); 
    while(1)  
    {  
       	ds3231ReadTime();
		buf[0] = buf[0]&0x7F; //sec
		buf[1] = buf[1]&0x7F; //min
		buf[2] = buf[2]&0x3F; //hour
		buf[3] = buf[3]&0x07; //week
		buf[4] = buf[4]&0x3F; //day
		buf[5] = buf[5]&0x1F; //mouth
		//year/month/day
		printf("20%02x/%02x/%02x  ",buf[6],buf[5],buf[4]);
		//hour:minute/second
		printf("%02x:%02x:%02x  ",buf[2],buf[1],buf[0]);
		//weekday
		printf("%s\n",week[(unsigned char)buf[3]-1]);
		sleep_ms(1000); 
		if(buf[6]==0x00 && buf[5]==0x01 && buf[4]==0x01)
		{
			ds3231SetTime(); 
		}
	}  
	return 0;
}
