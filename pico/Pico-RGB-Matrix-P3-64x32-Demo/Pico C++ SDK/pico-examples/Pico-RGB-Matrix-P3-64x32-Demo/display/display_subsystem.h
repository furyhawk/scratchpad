#ifndef __DISPLAY_SUBSYSTEM_H
#define __DISPLAY_SUBSYSTEM_H
#include "driver_RGBMatrix.h"
#include "RGBMatrix_device.h"
#include "driver_ds3231.h"
#include <cstring>

#define ENGLISH 0
#define CHINESE 1

void displayDateTimePage(PDisplayDevice displayDevice,PRTC_tm pt_RTC_tm,uint8_t *temp);
void displaySettingPage(PDisplayDevice displayDevice,uint8_t Select_setting_options);
void displaySetTimePage(PDisplayDevice displayDevice,uint8_t set_hour_temp,uint8_t set_min_temp,uint8_t set_sec_temp,int8_t selectedTimeOption);
void displaySetDatePage(PDisplayDevice displayDevice,uint16_t set_year_temp,uint8_t set_mon_temp,uint8_t set_mday_temp,int8_t selectedTimeOption);
void displaySetLanguagePage(PDisplayDevice displayDevice,uint8_t LanguageFlag);
void displayAutoLightBeepOnOffPage(PDisplayDevice displayDevice,uint8_t Select_setting_options,uint8_t autoLightFlag,uint8_t BeepFlag);
uint8_t LunarCalendar(uint16_t year,uint16_t month,uint16_t day);

uint8_t get_month_date(uint16_t year_temp,uint8_t month_temp);
uint8_t get_weekday(uint16_t year_cnt,uint8_t month_cnt,uint8_t date_cnt);
void LED_Matrix_clear(PDisplayDevice displayDevice,uint8_t color);
#endif
