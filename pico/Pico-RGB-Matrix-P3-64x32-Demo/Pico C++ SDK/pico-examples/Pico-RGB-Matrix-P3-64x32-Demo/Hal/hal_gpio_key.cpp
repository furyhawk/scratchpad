#include "hal_gpio_key.h"
#include "driver_key.h"
#include "RGBMatrixConfig.h"

void HAL_GPIOKeyInit(void)
{
#if defined CONFIG_SUPPORT_PICO
	picoKeyGpioInit();
#elif defined CONFIG_SUPPORT_ESP32S2
	esp32S2KeyGpioInit();
#endif 
}

void HAL_whichKeyPress(void)
{
	WhichKeyPress();
}