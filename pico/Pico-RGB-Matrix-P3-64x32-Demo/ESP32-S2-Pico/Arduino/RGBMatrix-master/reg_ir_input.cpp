#include "reg_ir_input.h"
#include "hal_gpio_ir.h"
#include "input_system.h"

static int GPIOIRInit(void)
{
	HAL_GPIOIRInit();
	return 0;
}

static int yfGetInputEvent(PInputEvent ptInputEvent)
{
	return 0;
}

static struct InputDevice *empty;

static InputDevice g_tIRDevice = {
	(char *)"ir_control",
	yfGetInputEvent,
	GPIOIRInit,
	empty,
};


void AddIRInputDevice(void)
{
	InputDeviceRegister(&g_tIRDevice);
}