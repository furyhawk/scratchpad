/*****************************************************************************
* | File      	:   LCD_1in47.c
* | Author      :   Waveshare team
* | Function    :   Hardware underlying interface
* | Info        :
*                Used to shield the underlying layers of each master 
*                and enhance portability
*----------------
* |	This version:   V1.0
* | Date        :   2025-03-13
* | Info        :   Basic version
*
******************************************************************************/
#ifndef __LCD_1IN47_H
#define __LCD_1IN47_H

#include "DEV_Config.h"
#include <stdint.h>

#include <stdlib.h>     //itoa()
#include <stdio.h>

#define LCD_1IN47_HEIGHT 320
#define LCD_1IN47_WIDTH  172

#define HORIZONTAL 0
#define VERTICAL   1

#define LCD_1IN47_SetBacklight(Value) ; 

#define WHITE         0xFFFF
#define BLACK		  0x0000
#define BLUE 		  0x001F
#define BRED 	      0XF81F
#define GRED 		  0XFFE0
#define GBLUE		  0X07FF
#define RED  		  0xF800
#define MAGENTA		  0xF81F
#define GREEN		  0x07E0
#define CYAN 		  0x7FFF
#define YELLOW		  0xFFE0
#define BROWN		  0XBC40
#define BRRED		  0XFC07
#define GRAY 	      0X8430
#define DARKBLUE	  0X01CF
#define LIGHTBLUE	  0X7D7C
#define GRAYBLUE      0X5458
#define LIGHTGREEN    0X841F
#define LGRAY 		  0XC618
#define LGRAYBLUE     0XA651
#define LBBLUE        0X2B12

typedef struct{
    uint16_t WIDTH;
    uint16_t HEIGHT;
    uint8_t SCAN_DIR;
}LCD_1IN47_ATTRIBUTES;
extern LCD_1IN47_ATTRIBUTES LCD_1IN47;

/********************************************************************************
function:	
			Macro definition variable name
********************************************************************************/
void LCD_1IN47_Init(uint8_t Scan_dir);
void LCD_1IN47_Clear(uint16_t Color);
void LCD_1IN47_Display(uint16_t *Image);
void LCD_1IN47_DisplayWindows(uint16_t Xstart, uint16_t Ystart, uint16_t Xend, uint16_t Yend, uint16_t *Image);
void LCD_1IN47_DisplayPoint(uint16_t X, uint16_t Y, uint16_t Color);
void LCD_1IN47_SetWindows(uint16_t Xstart, uint16_t Ystart, uint16_t Xend, uint16_t Yend);
void Handler_1IN47_LCD(int signo);
#endif
