#ifndef __RGBMATRIX_DEVICE_H
#define __RGBMATRIX_DEVICE_H

#include "font.h"

typedef struct DisplayDevice{
	char *name;
	void *FBBase;
	int iXres;
	int iYres;
	int iBpp;
	void (*Init)(void);
	void (*Flush)(struct DisplayDevice *ptDev);
	int  (*SetPixel)(struct DisplayDevice *ptDev, int iX, int iY, char dis_char, uint8_t fontSize);
}DisplayDevice,*PDisplayDevice;


PDisplayDevice GetDisplayDevice(void);

#endif
