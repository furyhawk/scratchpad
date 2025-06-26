#include "hal_RGBMatrix_device.h"
#include "RGBMatrixConfig.h"
#include "driver_RGBMatrix.h"


void HAL_RGBMatrixDeviceInit(void)
{
#if defined CONFIG_SUPPORT_PICO
	picoRGBMatrixDeviceInit();
	
#elif defined CONFIG_SUPPORT_ESP32S2
	esp32S2RGBMatrixDeviceInit();
#endif
}

void HAL_RGBMatrixDeviceFlush(PDisplayDevice ptDev)
{
	uint8_t *buf = (uint8_t *)ptDev->FBBase;
	RGBMatrixDeviceFlush(buf);
}

