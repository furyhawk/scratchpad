#ifndef __DRIVER_DS3231_H
#define __DRIVER_DS3231_H
#include <stdio.h>
#include "RGBMatrixConfig.h"
#if defined CONFIG_SUPPORT_PICO

#include "hardware/i2c.h"
#include "pico/stdlib.h"
#define SDA 6
#define SCL 7
#define I2C_PORT i2c1

#elif defined CONFIG_SUPPORT_ESP32S2
#include "driver/i2c.h"
#define DS3231_I2C_NUM (1)
#define SDA_PIN GPIO_NUM_14
#define SCA_PIN GPIO_NUM_15

#endif

#define DS3231_ADDRESS 0x68
#define WRITE 0
#define READ 1




#define DS3231_CTRL_OSCILLATOR    0x80
#define DS3231_CTRL_SQUAREWAVE_BB 0x40
#define DS3231_CTRL_TEMPCONV      0x20


#define DS3231_ADDR_TIME    0x00
#define DS3231_ADDR_CONTROL 0x0e
#define DS3231_ADDR_STATUS  0x0f
#define DS3231_ADDR_AGING   0x10
#define DS3231_ADDR_TEMP    0x11

#define DS3231_12HOUR_FLAG  0x40
#define DS3231_12HOUR_MASK  0x1f
#define DS3231_PM_FLAG      0x20
#define DS3231_MONTH_MASK   0x1f

#define DS3231_ADDR_TIME_SEC    0x00
#define DS3231_ADDR_TIME_MIN    0x01
#define DS3231_ADDR_TIME_HOUR   0x02
#define DS3231_ADDR_TIME_WDAY   0x03
#define DS3231_ADDR_TIME_MDAY   0x04
#define DS3231_ADDR_TIME_MON    0x05
#define DS3231_ADDR_TIME_YEAR   0x06

typedef struct RTC_tm{
	uint8_t tm_sec;
	uint8_t tm_min;
	uint8_t tm_hour;
	uint8_t tm_wday;
	uint8_t tm_mday;
	uint8_t tm_mon;
	uint16_t tm_year;
}RTC_tm,*PRTC_tm;

void InitDs3231(void);
void ds3231_get_time(PRTC_tm time);
void ds3231_set_time(PRTC_tm time);
void ds3231_get_temp_integer(uint8_t *temp);
void ds3231_set_sec(uint8_t sec_temp);
void ds3231_set_min(uint8_t min_temp);
void ds3231_set_hour(uint8_t hour_temp);
void ds3231_set_wday(uint8_t wday_temp);
void ds3231_set_mday(uint8_t mday_temp);
void ds3231_set_mon(uint8_t mon_temp);
void ds3231_set_year(uint16_t year_temp);



#endif
