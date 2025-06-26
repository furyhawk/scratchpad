#include "input_system.h"

static PInputDevice g_ptInputDevices;

void InputDeviceRegister(PInputDevice ptInputDevice)
{
	ptInputDevice->pNext = g_ptInputDevices;
	g_ptInputDevices = ptInputDevice;
}

void InitInputDevices(void)
{
	PInputDevice pDev = g_ptInputDevices;

	while(pDev)
	{
		pDev->DeviceInit();
		pDev = pDev->pNext;
	}
}