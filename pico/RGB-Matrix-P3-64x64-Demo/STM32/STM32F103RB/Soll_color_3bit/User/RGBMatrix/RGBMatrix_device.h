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
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include "fonts.h"



#define UBYTE   uint8_t
#define UWORD   uint16_t
#define UDOUBLE uint32_t

#include "GUI_Paint.h"

#define LED_chain 2 // STM32F103RB  MAX = 3 ,There is not enough memory, the maximum cache size is 3
#define LED_Width 64 * LED_chain
#define LED_Height 64

#define SCROLL_SPEED 5 // The minimum scroll speed is not less than 5. If it is less than 5, misalignment will occur.

#define HAL_DELAY_NEWBIE 0

void DWT_Init(void);
void DWT_Delay(uint32_t us);



#define RGB_R1(value)  HAL_GPIO_WritePin(R1_GPIO_Port, R1_Pin,(value >= 1)? GPIO_PIN_SET: GPIO_PIN_RESET)
#define RGB_G1(value)  HAL_GPIO_WritePin(G1_GPIO_Port, G1_Pin,(value >= 1)? GPIO_PIN_SET: GPIO_PIN_RESET)
#define RGB_B1(value)  HAL_GPIO_WritePin(B1_GPIO_Port, B1_Pin,(value >= 1)? GPIO_PIN_SET: GPIO_PIN_RESET)

#define RGB_R2(value)  HAL_GPIO_WritePin(R2_GPIO_Port, R2_Pin,(value >= 1)? GPIO_PIN_SET: GPIO_PIN_RESET)
#define RGB_G2(value)  HAL_GPIO_WritePin(G2_GPIO_Port, G2_Pin,(value >= 1)? GPIO_PIN_SET: GPIO_PIN_RESET)
#define RGB_B2(value)  HAL_GPIO_WritePin(B2_GPIO_Port, B2_Pin,(value >= 1)? GPIO_PIN_SET: GPIO_PIN_RESET)

#define RGB_A(value)  HAL_GPIO_WritePin(A_GPIO_Port, A_Pin,(value >= 1)? GPIO_PIN_SET: GPIO_PIN_RESET)
#define RGB_B(value)  HAL_GPIO_WritePin(B_GPIO_Port, B_Pin,(value >= 1)? GPIO_PIN_SET: GPIO_PIN_RESET)
#define RGB_C(value)  HAL_GPIO_WritePin(C_GPIO_Port, C_Pin,(value >= 1)? GPIO_PIN_SET: GPIO_PIN_RESET)
#define RGB_D(value)  HAL_GPIO_WritePin(D_GPIO_Port, D_Pin,(value >= 1)? GPIO_PIN_SET: GPIO_PIN_RESET)
#define RGB_E(value)  HAL_GPIO_WritePin(E_GPIO_Port, E_Pin,(value >= 1)? GPIO_PIN_SET: GPIO_PIN_RESET)

#define RGB_CLK(value)  HAL_GPIO_WritePin(CLK_GPIO_Port, CLK_Pin,(value >= 1)? GPIO_PIN_SET: GPIO_PIN_RESET)
#define RGB_LAT(value)  HAL_GPIO_WritePin(LAT_GPIO_Port, LAT_Pin,(value >= 1)? GPIO_PIN_SET: GPIO_PIN_RESET)
#define RGB_OE(value)   HAL_GPIO_WritePin(OE_GPIO_Port, OE_Pin,(value >= 1)? GPIO_PIN_SET: GPIO_PIN_RESET)

void HUB75_Init(void);
void RGBMatrixWriteData(void);
void HUB75_Display(void);
void HUB75_Clear(void);

void scrollLeft(void);
void scrollRight(void);
void scrollUp(void);
void scrollDown(void);









#endif
