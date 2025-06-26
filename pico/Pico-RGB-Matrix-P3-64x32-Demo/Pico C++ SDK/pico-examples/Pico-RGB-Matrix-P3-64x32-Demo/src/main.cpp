#include "reg_gpio_key.h"
#include "driver_buzzer.h"
#include "input_event_buffer.h"
#include "hal_gpio_key.h"
#include "RGBMatrix_device.h"
#include "font.h"
#include "driver_RGBMatrix.h"
#include "driver_ds3231.h"
#include "driver_adc.h"
#include "display_subsystem.h"

#include "stdio.h"
#include"time.h"
bool timer_screen_refresh_cb(struct repeating_timer *t);
bool timer_get_time_cb(struct repeating_timer *t);
bool timer_autolight_cb(struct repeating_timer *t);

void addInputDevices(void);
void checkInputEvent(void);

void pagingFunction(void);
void Event_handler(void);
void K0_MENU_OPERATION(void);
void K1_DOWN_OPERATION(void);
void K2_UP_OPERATION(void);
void K2_PRESS_OPERATION(void);


RTC_tm gt_RTC_tm = {0,22,15,4,18,01,2024};
struct repeating_timer timer_screen_refresh_handle;
struct repeating_timer timer_get_time_handle;
struct repeating_timer timer_autolight_handle;
PDisplayDevice displayDevice;
uint8_t temp ;

InputEvent event;

#if CN

uint8_t LanguageFlag = CHINESE;

#elif  EN

uint8_t LanguageFlag = ENGLISH;

#endif

int8_t pageIdNumber = 0;
uint8_t selectSettingOptions = 1;
uint8_t set_hour_temp,set_min_temp,set_sec_temp;
uint16_t set_year_temp;
uint8_t set_mon_temp,set_mday_temp;
int8_t enterTimeSettingFlag = 1,selectedTimeOption = 0;
uint8_t BeepFlag=1,autoLightFlag = 0;
uint16_t autoLightCount = 0;
uint8_t AlarmFlag = 0;
uint16_t BeepCount = 0;
uint8_t systemStartupFlag = 1;
uint16_t adc_value;
extern uint8_t UpdateVideoMemory;

int main(void)
{
  add_repeating_timer_us(1000, timer_screen_refresh_cb, NULL, &timer_screen_refresh_handle);
  add_repeating_timer_us(1000*1000, timer_get_time_cb, NULL, &timer_get_time_handle);
  add_repeating_timer_us(140, timer_autolight_cb, NULL, &timer_autolight_handle);
	displayDevice = GetDisplayDevice();
	addInputDevices();
	InitInputDevices();
	buzzerInit();
	displayDevice->Init();
  InitDs3231();
  ds3231_set_time(&gt_RTC_tm);
  adc_Init();
	while(1)
	{
    if(systemStartupFlag == 1)//The default page after system startup
		{
			ds3231_get_temp_integer(&temp);
			ds3231_get_time(&gt_RTC_tm);
			displayDateTimePage(displayDevice,&gt_RTC_tm,&temp);
			systemStartupFlag = 0;
		}
		checkInputEvent();
		Event_handler();
		if(AlarmFlag == 1)//Keystroke sound is enabled
		{
			BeepCount ++;
			if(BeepCount == 100)
			{
			BUZZEROFF();
			AlarmFlag = 0;
			BeepCount = 0;
			}
		}
		sleep_ms(1);
	}

	return 0;
}

bool timer_screen_refresh_cb(struct repeating_timer *t)
{
  displayDevice->Flush(displayDevice);
  return true;
}

bool timer_get_time_cb(struct repeating_timer *t)
{ 
  if(pageIdNumber == 0)//UpdateTime
  {
    ds3231_get_temp_integer(&temp);
    ds3231_get_time(&gt_RTC_tm);
    displayDateTimePage(displayDevice,&gt_RTC_tm,&temp);
  }

  if(autoLightFlag == 1)
  {
    adc_value = adc_read();
  }
  return true;
}

bool  timer_autolight_cb(struct repeating_timer *t)
{
  if(autoLightFlag == 1 && UpdateVideoMemory == 0)
  {
    if(adc_value > 2000)
    {
      autoLightCount ++;
      if(autoLightCount  == 3)
      {
        OE_LOW;
        autoLightCount = 0;
      }
      else
      {
        OE_HIGH;
      }
      
    }
    else
    {
      OE_LOW;
    }
  }
  return true;
}

void pagingFunction(void)
{
  if(pageIdNumber == 1)
  {
    displaySettingPage(displayDevice,selectSettingOptions);
  }
  else if(pageIdNumber == 2)
  {
    if(selectSettingOptions == 1)
    {
      if(enterTimeSettingFlag == 1)
      {
        enterTimeSettingFlag = 0;
        ds3231_get_time(&gt_RTC_tm);
        set_hour_temp = gt_RTC_tm.tm_hour;
        set_min_temp = gt_RTC_tm.tm_min;
        set_sec_temp = gt_RTC_tm.tm_sec;
      }
      displaySetTimePage(displayDevice,set_hour_temp,set_min_temp,set_sec_temp,selectedTimeOption);
    }
    else if(selectSettingOptions == 2)
    {
      if(enterTimeSettingFlag == 1)
      {
        enterTimeSettingFlag = 0;
        ds3231_get_time(&gt_RTC_tm);
        set_year_temp = gt_RTC_tm.tm_year;
        set_mon_temp = gt_RTC_tm.tm_mon;
        set_mday_temp = gt_RTC_tm.tm_mday;
      }
      displaySetDatePage(displayDevice,set_year_temp,set_mon_temp,set_mday_temp,selectedTimeOption);
    }
    else if(selectSettingOptions == 3 || selectSettingOptions == 4)
    {
      displayAutoLightBeepOnOffPage(displayDevice,selectSettingOptions,autoLightFlag,BeepFlag);
    }
    else if(selectSettingOptions == 5)
    {
      displaySetLanguagePage(displayDevice,LanguageFlag);
    }
  }
}

void Event_handler(void)
{
  if(GetInputEvent(&event) == 0)
  {
    if(event.eType == INPUT_EVENT_TYPE_KEY)
    {
      if(event.iKey == KEY0_MENU)//Toggle page keys
      {
        K0_MENU_OPERATION();
      }
      else if(event.iKey == KEY1_DOWN)//Minus sign button
      {
        K1_DOWN_OPERATION();
      }
      else if(event.iKey == KEY2_UP)//With long press exit function
      {
        if(event.iPressure > 300)//Long press
        {
          K2_PRESS_OPERATION();
        }
        else //Plus sign button
        { 
          K2_UP_OPERATION();
        }
      }
    }
    pagingFunction();
    if(BeepFlag == 1)//Turn on the buzzer
    {
      BUZZERON();
      AlarmFlag = 1;
    }
  }
}

void K0_MENU_OPERATION(void)
{
  if(pageIdNumber == 2)
  {
    if(selectSettingOptions == 1 || selectSettingOptions == 2)
    {
      selectedTimeOption ++;
      if(selectedTimeOption > 2)
        selectedTimeOption = 0;
    }
  }
  pageIdNumber ++;
  if(pageIdNumber > 2)
  {
    pageIdNumber = 2;
  }   
}

void K1_DOWN_OPERATION(void) 
{
  if(pageIdNumber == 1)
  {
    selectSettingOptions --;
    if(selectSettingOptions == 0)
      selectSettingOptions = 5;
  }
  if(pageIdNumber == 2)
  {
    if(selectSettingOptions == 1)
    {
      if(selectedTimeOption == 0)
      {
        set_hour_temp --;
        if(set_hour_temp == 255)
        {
          set_hour_temp = 23;
        }
      }
      else if(selectedTimeOption == 1)
      {
        set_min_temp --;
        if(set_min_temp == 255)
        {
          set_min_temp = 59;
        }
      }
      else if(selectedTimeOption == 2)
      {
        set_sec_temp --;
        if(set_sec_temp == 255)
        {
          set_sec_temp = 59;
        }
      }
    }
    else if(selectSettingOptions == 2)
    {
      if(selectedTimeOption == 0)
      {
        set_year_temp --;
        if(set_year_temp < 2000)
        {
          set_year_temp = 2099;
        }
        if(set_mday_temp > get_month_date(set_year_temp,set_mon_temp))
        {
          set_mday_temp = get_month_date(set_year_temp,set_mon_temp);
        }
      }
      else if(selectedTimeOption == 1)
      {
        set_mon_temp --;
        if(set_mon_temp == 0)
        {
          set_mon_temp = 12;
        }
        if(set_mday_temp > get_month_date(set_year_temp,set_mon_temp))
        {
          set_mday_temp = get_month_date(set_year_temp,set_mon_temp);
        }
      }
      else if(selectedTimeOption == 2)
      {
        set_mday_temp --;
        if(set_mday_temp == 0)
        {
          set_mday_temp = get_month_date(set_year_temp,set_mon_temp);
        }
      }
    }
    else if(selectSettingOptions == 3)
    {
      autoLightFlag = !autoLightFlag;
    }
    else if(selectSettingOptions == 4)
    {
      BeepFlag = !BeepFlag;
    }
    else if(selectSettingOptions == 5)
    {
      LanguageFlag = !LanguageFlag;
    }
  }
}

void K2_UP_OPERATION(void)
{
  if(pageIdNumber == 1)
  {
    selectSettingOptions ++;
    if(selectSettingOptions > 5)
      selectSettingOptions = 1;
  }
  if(pageIdNumber == 2)
  {
    if(selectSettingOptions == 1)
    {
      if(selectedTimeOption == 0)
      {
        set_hour_temp ++;
        if(set_hour_temp == 24)
        {
          set_hour_temp = 0;
        }
      }
      else if(selectedTimeOption == 1)
      {
        set_min_temp ++;
        if(set_min_temp == 60)
        {
          set_min_temp = 0;
        }
      }
      else if(selectedTimeOption == 2)
      {
        set_sec_temp ++;
        if(set_sec_temp == 60)
        {
          set_sec_temp = 0;
        }
      }
    }
    else if(selectSettingOptions == 2)
    {
      if(selectedTimeOption == 0)
      {
        set_year_temp ++;
        if(set_year_temp == 2100)
        {
          set_year_temp = 2000;
        }
        if(set_mday_temp > get_month_date(set_year_temp,set_mon_temp))
        {
          set_mday_temp = get_month_date(set_year_temp,set_mon_temp);
        }
      }
      else if(selectedTimeOption == 1)
      {
        set_mon_temp ++;
        if(set_mon_temp == 13)
        {
          set_mon_temp = 1;
        }
        if(set_mday_temp > get_month_date(set_year_temp,set_mon_temp))
        {
          set_mday_temp = get_month_date(set_year_temp,set_mon_temp);
        }
      }
      else if(selectedTimeOption == 2)
      {
        set_mday_temp ++;
        if(set_mday_temp > get_month_date(set_year_temp,set_mon_temp))
        {
          set_mday_temp = 1;
        }
      }
    }
    else if(selectSettingOptions == 3)
    {
      autoLightFlag = !autoLightFlag;
    }
    else if(selectSettingOptions == 4)
    {
      BeepFlag = !BeepFlag;
    }
    else if(selectSettingOptions == 5)
    {
      LanguageFlag = !LanguageFlag;
    }
  }
}

void K2_PRESS_OPERATION(void)
{
  if(pageIdNumber == 1)
  {
    ds3231_get_time(&gt_RTC_tm);
    displayDateTimePage(displayDevice,&gt_RTC_tm,&temp);
  }
  if(pageIdNumber == 2 && (selectSettingOptions == 1 || selectSettingOptions == 2))
  {
    selectedTimeOption = 0;
    enterTimeSettingFlag = 1;
    if(selectSettingOptions == 1)
    {
      ds3231_set_sec(set_sec_temp);
      ds3231_set_min(set_min_temp);
      ds3231_set_hour(set_hour_temp);
    }
    if(selectSettingOptions == 2)
    {
      ds3231_set_mday(set_mday_temp);
      ds3231_set_mon(set_mon_temp);
      ds3231_set_year(set_year_temp);
      ds3231_set_wday(get_weekday(set_year_temp,set_mon_temp,set_mday_temp));
    }
  }
  pageIdNumber --;
  if(pageIdNumber < 0)
  {
    pageIdNumber = 0;
  }
}


void addInputDevices(void)
{
	AddInputDeviceGpioKey();
}

void checkInputEvent(void)
{
	HAL_whichKeyPress();
}