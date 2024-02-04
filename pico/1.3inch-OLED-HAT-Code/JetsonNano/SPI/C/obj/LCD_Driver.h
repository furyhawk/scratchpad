#ifndef _SH1106_H_
#define _SH1106_H_

#include "DEV_Config.h"

#define WIDTH 128
#define HEIGHT 64
#define PAGES 8

void SH1106_begin();
void SH1106_display();
void SH1106_clear();
void SH1106_pixel(int x,int y,char color);

#endif
