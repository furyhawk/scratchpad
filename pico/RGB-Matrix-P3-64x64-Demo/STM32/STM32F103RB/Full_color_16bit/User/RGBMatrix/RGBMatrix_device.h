/*****************************************************************************
* | File      	:   RGBMatrix_device.h
* | Author      :   Waveshare team
* | Function    :   Hardware underlying interface
* | Info        :
*                Used to shield the underlying layers of each master 
*                and enhance portability
*----------------
* |	This version:   V1.0
* | Date        :   2023-10-21
* | Info        :

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
******************************************************************************/
#ifndef _DEV_CONFIG_H_
#define _DEV_CONFIG_H_

#include "stm32f1xx_hal.h"
#include "main.h"
#include "usart.h"
#include "tim.h"
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include "fonts.h"

#define UBYTE   uint8_t
#define UWORD   uint16_t
#define UDOUBLE uint32_t

#include "GUI_Paint.h"


#define HUB75_MIN_PERIOD 24 //这里是定时器周期 最小24us,可以自己调整，过高可能会出现闪烁

typedef struct {

  UWORD *BlackImage;              ///< Per-bitplane RGB data for matrix
  uint16_t timer_Period;        ///< Bitplane 0 timer period
  uint16_t min_Period;            ///< Plane 0 timer period for ~250Hz
	
  uint16_t width;                ///< Matrix chain width only in bits
	uint16_t height;
	
  uint16_t all_width;            ///< Matrix chain width*tiling in bits
  uint8_t address_size;       ///< 地址引脚数量

  uint16_t column_select;           ///< Addressable row pairs
  int8_t tile;                   ///< Vertical tiling repetitions
  
  uint8_t plane;        ///< Current bitplane (changes in ISR)
  uint8_t row;          ///< Current scanline (changes in ISR)	
	
	uint8_t bitDepth; //颜色位深

} HUB75_port;

extern HUB75_port RGB_Matrix;


void DWT_Init(void);
void DWT_Delay(uint32_t us);
void HUB75E_DelayUs(int us);
	
void HUB75_Init(uint8_t width,uint8_t address_size,uint8_t bitDepth);
void HUB75_show(void);
uint16_t Wheel(uint8_t WheelPos);


#endif
