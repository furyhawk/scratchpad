#include "RGBMatrix_device.h"
#include "hal_RGBMatrix_device.h"
static uint8_t g_RGBMatrixFramebuffer[256]={0xff};


static void RGBMatrixDeviceInit()
{
    HAL_RGBMatrixDeviceInit();
}

static  void RGBMatrixDeviceFlush(PDisplayDevice ptDev)
{
    HAL_RGBMatrixDeviceFlush(ptDev);
}

static int RGBMatrixDeviceSetPixel(PDisplayDevice ptDev,int iX, int iY, char dis_char, uint8_t fontSize)
{
	uint8_t *Framebuffer = (uint8_t *)ptDev->FBBase;
	
	if(fontSize == DAT4X7)
	{
		fontChar4X7(Framebuffer,iX,iY,dis_char);
	}
	else if(fontSize == DAT8X10)
	{
		fontChar8X8(Framebuffer,iX,iY,dis_char);
	}
	else if(fontSize == DAT16X16)
	{
		fontChar16X16(Framebuffer,iX,iY,dis_char);
	}
    return 0;
}



static DisplayDevice g_tRGBMatrixDevice = {
	(char *)"RGBMatrix",
	g_RGBMatrixFramebuffer,
	64,
	32,
	3,
    RGBMatrixDeviceInit,
    RGBMatrixDeviceFlush,
    RGBMatrixDeviceSetPixel
};

PDisplayDevice GetDisplayDevice(void)
{
    return &g_tRGBMatrixDevice;
}