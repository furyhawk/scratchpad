#include "driver_key.h"
#include "input_event_buffer.h"

#include "driver_buzzer.h"
/************************************************* *********************
  * Function name: keyGpioInit
  * Function description: Initialize the key device 
  * Input parameters: None
  * Output parameters: None
  * Return value: None
  */
#ifdef CONFIG_SUPPORT_PICO
void picoKeyGpioInit(void)
{

  gpio_init(KEY0_PIN);
  gpio_init(KEY1_PIN);
  gpio_init(KEY2_PIN);
  gpio_set_dir(KEY0_PIN,GPIO_IN);
  gpio_set_dir(KEY1_PIN, GPIO_IN);
  gpio_set_dir(KEY2_PIN, GPIO_IN);
  gpio_pull_up(KEY0_PIN);
  gpio_pull_up(KEY1_PIN);
  gpio_pull_up(KEY2_PIN);
}
#endif

#ifdef CONFIG_SUPPORT_ESP32S2
void esp32S2KeyGpioInit(void)
{
  gpio_reset_pin(KEY0_PIN);
  gpio_set_direction(KEY0_PIN,GPIO_MODE_INPUT);

  gpio_reset_pin(KEY1_PIN);
  gpio_set_direction(KEY1_PIN,GPIO_MODE_INPUT);
  
  gpio_reset_pin(KEY2_PIN);
  gpio_set_direction(KEY2_PIN,GPIO_MODE_INPUT);
  
}
#endif
/************************************************* *********************
  * Function name: keyLongPressOrShortPress
  * Function description: Determine whether the button is long pressed or short pressed
  * Input parameters: Key value
  * Return value: which Key Action
  */
int memuKey = 0;
int downKey = 0;
int upKey = 0;
#define Pressure 1
void WhichKeyPress(void)
{
  InputEvent event;

  if(!KEY0_STATUS) //KEY0
  {
    memuKey ++;
  }
  else
  {
    if(memuKey > 20 && memuKey < 500)
   {
      event.eType = INPUT_EVENT_TYPE_KEY;
      event.iKey  = KEY0_MENU;
      event.iPressure = memuKey; /*压力值*/
      PutInputEvent(&event);
    }
	
    memuKey = 0;
  }

	if(!KEY1_STATUS) //KEY1
  {
    downKey ++;
  }
  else
  {
    if(downKey > 20 && downKey < 500){
      event.eType = INPUT_EVENT_TYPE_KEY;
      event.iKey  = KEY1_DOWN;
      event.iPressure = downKey; /*压力值*/
      PutInputEvent(&event);
    }
    downKey = 0;
  }
  if(!KEY2_STATUS)
  {
    upKey ++;
  }
  else
  {
    if(upKey > 20 && upKey < 2000)
    {
      event.eType = INPUT_EVENT_TYPE_KEY;
      event.iKey  = KEY2_UP;
      event.iPressure = upKey; /*压力值*/
      PutInputEvent(&event);
    }
    upKey = 0;
  }
}