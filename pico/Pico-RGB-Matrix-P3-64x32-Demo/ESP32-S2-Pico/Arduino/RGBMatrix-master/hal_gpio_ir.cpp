#include "hal_gpio_ir.h"
#include "driver_ir.h"
#include "RGBMatrixConfig.h"

void HAL_GPIOIRInit(void)
{
#if defined CONFIG_SUPPORT_PICO
	picoIRGpioInit();
#elif defined CONFIG_SUPPORT_ESP32S2
	esp32S2IRGpioInit();
#endif 
}

