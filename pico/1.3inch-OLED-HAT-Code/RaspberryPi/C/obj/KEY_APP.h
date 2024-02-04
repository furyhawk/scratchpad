/*****************************************************************************
* | File      	:   DEV_Config.c
* | Author      :   Waveshare team
* | Function    :   Hardware underlying interface
* | Info        :
*                Used to shield the underlying layers of each master 
*                and enhance portability
*----------------
* |	This version:   V1.0
* | Date        :   2018-01-11
* | Info        :   Basic version
*
******************************************************************************/
#ifndef _KEY_APP_H_
#define _KEY_APP_H_

#include "DEV_Config.h"
#include "KEY_APP.h"

#define DisString_EN  GUI_DisString_EN
#define DrawRectangle  GUI_DrawRectangle
#define Font_KEY  Font12
#define Font_Offset  2

#define CLEAR  OLED_Clear


#define WORD_COLOR WHITE
#define BACK_COLOR FONT_BACKGROUND

#define WIDTH  132 
#define HEIGHT  64

void KEY_Listen(void);





#endif