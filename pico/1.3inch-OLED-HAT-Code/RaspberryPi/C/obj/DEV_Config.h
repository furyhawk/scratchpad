#ifndef _DEV_CONFIG_H_
#define _DEV_CONFIG_H_
/***********************************************************************************************************************
			------------------------------------------------------------------------
			|\\\																///|
			|\\\					Hardware interface							///|
			------------------------------------------------------------------------
***********************************************************************************************************************/
#ifdef USE_BCM2835_LIB
    #include <bcm2835.h>
#elif USE_WIRINGPI_LIB
    #include <wiringPi.h>
    #include <wiringPiSPI.h>
#elif USE_DEV_LIB
    #include <lgpio.h>
    #define LFLAGS 0
    #define NUM_MAXBUF  4
    
#endif

#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <unistd.h>
#include "Debug.h"


#define USE_SPI 1
#define USE_IIC 0
#define IIC_CMD        0X00
#define IIC_RAM        0X40


/**
 * data
**/
#define UBYTE   uint8_t
#define UWORD   uint16_t
#define UDOUBLE uint32_t

//OLED
//#define SPI_MOSI 10
//#define SPI_SCK  11
//#define I2C_SCL 3
//#define I2C_SDA 2
#define OLED_CS         8
#define OLED_RST        25
#define OLED_DC         24

#define OLED_CS_0      DEV_Digital_Write(OLED_CS,0)
#define OLED_CS_1      DEV_Digital_Write(OLED_CS,1)

#define OLED_RST_0      DEV_Digital_Write(OLED_RST,0)
#define OLED_RST_1      DEV_Digital_Write(OLED_RST,1)
#define OLED_RST_RD     DEV_Digital_Read(OLED_RST)

#define OLED_DC_0       DEV_Digital_Write(OLED_DC,0)
#define OLED_DC_1       DEV_Digital_Write(OLED_DC,1)

//KEY
#define KEY_UP_PIN      6
#define KEY_DOWN_PIN    19
#define KEY_LEFT_PIN    5
#define KEY_RIGHT_PIN   26
#define KEY_PRESS_PIN   13
#define KEY1_PIN        21
#define KEY2_PIN        20
#define KEY3_PIN        16

#define KEY_UP_RD       DEV_Digital_Read(KEY_UP_PIN)
#define KEY_DOWN_RD     DEV_Digital_Read(KEY_DOWN_PIN)
#define KEY_LEFT_RD     DEV_Digital_Read(KEY_LEFT_PIN)
#define KEY_RIGHT_RD    DEV_Digital_Read(KEY_RIGHT_PIN)
#define KEY_PRESS_RD    DEV_Digital_Read(KEY_PRESS_PIN)
#define KEY1_RD         DEV_Digital_Read(KEY1_PIN)
#define KEY2_RD         DEV_Digital_Read(KEY2_PIN)
#define KEY3_RD         DEV_Digital_Read(KEY3_PIN)
/*------------------------------------------------------------------------------------------------------*/


uint8_t DEV_ModuleInit(void);
void    DEV_ModuleExit(void);

void I2C_Write_Byte(uint8_t value, uint8_t Cmd);

void DEV_GPIO_Mode(UWORD Pin, UWORD Mode);
void DEV_Digital_Write(UWORD Pin, UBYTE Value);
UBYTE DEV_Digital_Read(UWORD Pin);
void DEV_Delay_ms(UDOUBLE xms);

void DEV_SPI_WriteByte(UBYTE Value);
void DEV_SPI_Write_nByte(uint8_t *pData, uint32_t Len);



#endif