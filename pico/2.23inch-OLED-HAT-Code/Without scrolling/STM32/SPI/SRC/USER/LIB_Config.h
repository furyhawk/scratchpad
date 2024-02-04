/**
  ******************************************************************************
  * @file    LIB_Config.h
  * @author  Waveshare Team
  * @version 
  * @date    31-Jule-2019
  * @brief     This file provides configurations for low layer hardware libraries.
  ******************************************************************************
  * @attention
  *
  * THE PRESENT FIRMWARE WHICH IS FOR GUIDANCE ONLY AIMS AT PROVIDING CUSTOMERS
  * WITH CODING INFORMATION REGARDING THEIR PRODUCTS IN ORDER FOR THEM TO SAVE
  * TIME. AS A RESULT, WAVESHARE SHALL NOT BE HELD LIABLE FOR ANY
  * DIRECT, INDIRECT OR CONSEQUENTIAL DAMAGES WITH RESPECT TO ANY CLAIMS ARISING*
  * FROM THE CONTENT OF SUCH FIRMWARE AND/OR THE USE MADE BY CUSTOMERS OF THE
  * CODING INFORMATION CONTAINED HEREIN IN CONNECTION WITH THEIR PRODUCTS.
  *
  ******************************************************************************
  */

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef _USE_LIB_CONFIG_H_
#define _USE_LIB_CONFIG_H_
//Macro Definition

/* Includes ------------------------------------------------------------------*/
#include "MacroAndConst.h"


/* Exported types ------------------------------------------------------------*/
/* Exported constants --------------------------------------------------------*/
/* Exported macro ------------------------------------------------------------*/

//Config
#include "Config.h"
/*------------------------------------------------------------------------------------------------------*/

//delay
#include "delay.h"

/*------------------------------------------------------------------------------------------------------*/
//SPI
#include "SPI.h"

/*------------------------------------------------------------------------------------------------------*/
//SSD1305
#include "SSD1305.h"
#include "Fonts.h"

#define INTERFACE_4WIRE_SPI     //4-wire SPI 
//#define INTERFACE_IIC         //I2C

#define SSD1305_CS_PIN          GPIO_Pin_12
#define SSD1305_CLK_PIN         GPIO_Pin_13
#define SSD1305_DIN_PIN         GPIO_Pin_15
#define SSD1305_RES_PIN         GPIO_Pin_2
#define SSD1305_DC_PIN          GPIO_Pin_6

#define SSD1305_CS_GPIO         GPIOB
#define SSD1305_CLK_GPIO        GPIOB
#define SSD1305_DIN_GPIO        GPIOB
#define SSD1305_RES_GPIO        GPIOC
#define SSD1305_DC_GPIO         GPIOC 

#define __SSD1305_CS_SET()      GPIO_WriteBit(SSD1305_CS_GPIO, SSD1305_CS_PIN, Bit_SET)
#define __SSD1305_CS_CLR()      GPIO_WriteBit(SSD1305_CS_GPIO, SSD1305_CS_PIN, Bit_RESET)

#define __SSD1305_RES_SET()     GPIO_WriteBit(SSD1305_RES_GPIO, SSD1305_RES_PIN, Bit_SET)
#define __SSD1305_RES_CLR()     GPIO_WriteBit(SSD1305_RES_GPIO, SSD1305_RES_PIN, Bit_RESET)

#define __SSD1305_DC_SET()      GPIO_WriteBit(SSD1305_DC_GPIO, SSD1305_DC_PIN, Bit_SET)
#define __SSD1305_DC_CLR()      GPIO_WriteBit(SSD1305_DC_GPIO, SSD1305_DC_PIN, Bit_RESET)

#define __SSD1305_CLK_SET()     GPIO_WriteBit(SSD1305_CLK_GPIO, SSD1305_CLK_PIN, Bit_SET)
#define __SSD1305_CLK_CLR()     GPIO_WriteBit(SSD1305_CLK_GPIO, SSD1305_CLK_PIN, Bit_RESET)

#define __SSD1305_DIN_SET()     GPIO_WriteBit(SSD1305_DIN_GPIO, SSD1305_DIN_PIN, Bit_SET)
#define __SSD1305_DIN_CLR()     GPIO_WriteBit(SSD1305_DIN_GPIO, SSD1305_DIN_PIN, Bit_RESET)

#define __SSD1305_WRITE_BYTE(DATA) spi_read_write_byte(SPI2, DATA)
/*------------------------------------------------------------------------------------------------------*/
//I2C
#include "IIC.h"

#define IIC_SCL_PIN         GPIO_Pin_13
#define IIC_SDA_PIN         GPIO_Pin_15

#define IIC_SCL_GPIO        GPIOB
#define IIC_SDA_GPIO        GPIOB

#define __IIC_SCL_SET()     GPIO_WriteBit(IIC_SCL_GPIO, IIC_SCL_PIN, Bit_SET)
#define __IIC_SCL_CLR()     GPIO_WriteBit(IIC_SCL_GPIO, IIC_SCL_PIN, Bit_RESET)

#define __IIC_SDA_SET()		GPIO_WriteBit(IIC_SDA_GPIO, IIC_SDA_PIN, Bit_SET)
#define __IIC_SDA_CLR()     GPIO_WriteBit(IIC_SDA_GPIO, IIC_SDA_PIN, Bit_RESET)

#define __IIC_SDA_IN()     	do { \
								GPIO_InitTypeDef tGPIO; \
								tGPIO.GPIO_Pin = IIC_SDA_PIN; \
								tGPIO.GPIO_Speed = GPIO_Speed_50MHz; \
								tGPIO.GPIO_Mode = GPIO_Mode_IPU; \
								GPIO_Init(IIC_SDA_GPIO, &tGPIO); \
							}while(0)				

#define __IIC_SDA_OUT() 	do { \
								GPIO_InitTypeDef tGPIO; \
								tGPIO.GPIO_Pin = IIC_SDA_PIN; \
								tGPIO.GPIO_Speed = GPIO_Speed_50MHz; \
								tGPIO.GPIO_Mode = GPIO_Mode_Out_PP; \
								GPIO_Init(IIC_SDA_GPIO, &tGPIO); \
							}while(0)   


#define __IIC_SDA_READ()    GPIO_ReadInputDataBit(IIC_SDA_GPIO, IIC_SDA_PIN)
/*------------------------------------------------------------------------------------------------------*/

/* Exported functions ------------------------------------------------------- */


#endif

/*-------------------------------END OF FILE-------------------------------*/

