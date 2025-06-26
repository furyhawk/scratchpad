#include "reg_gpio_key.h"
#include "hal_gpio_key.h"
#include "input_system.h"

static int GPIOKeyInit(void)
{
	HAL_GPIOKeyInit();
	return 0;
}

static int yfGetInputEvent(PInputEvent ptInputEvent)
{
	return 0;
}

struct InputDevice *empty;

static InputDevice g_tKeyDevice = {
	(char *)"gpio_key",
	yfGetInputEvent,
	GPIOKeyInit,
	empty,
};


void AddInputDeviceGpioKey(void)
{
	InputDeviceRegister(&g_tKeyDevice);
}