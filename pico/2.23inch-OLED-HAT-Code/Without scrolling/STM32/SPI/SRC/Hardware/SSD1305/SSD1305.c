/**
  ******************************************************************************
  * @file    SSD1305.c 
  * @author  Waveshare Team
  * @version 
  * @date    31-Jule-2019
  * @brief   This file includes the OLED driver for SSD1305 display moudle
  ******************************************************************************
  * @attention
  *
  * THE PRESENT FIRMWARE WHICH IS FOR GUIDANCE ONLY AIMS AT PROVIDING CUSTOMERS
  * WITH CODING INFORMATION REGARDING THEIR PRODUCTS IN ORDER FOR THEM TO SAVE
  * TIME. AS A RESULT, WAVESHARE SHALL NOT BE HELD LIABLE FOR ANY
  * DIRECT, INDIRECT OR CONSEQUENTIAL DAMAGES WITH RESPECT TO ANY CLAIMS ARISING
  * FROM THE CONTENT OF SUCH FIRMWARE AND/OR THE USE MADE BY CUSTOMERS OF THE
  * CODING INFORMATION CONTAINED HEREIN IN CONNECTION WITH THEIR PRODUCTS.
  *
  ******************************************************************************
  */

/* Includes ------------------------------------------------------------------*/
#include "LIB_Config.h"
#include "SSD1305.h"
#include "Fonts.h"

/* Private typedef -----------------------------------------------------------*/
/* Private define ------------------------------------------------------------*/
#define SSD1305_CMD    0
#define SSD1305_DAT    1

#define SSD1305_WIDTH    128
#define SSD1305_HEIGHT   32
							
/* Private variables ---------------------------------------------------------*/
static uint8_t s_chDispalyBuffer[128][4];

/* Private function prototypes -----------------------------------------------*/
/* Private functions ---------------------------------------------------------*/


/**
  * @brief  Writes an byte to the display data ram or the command register
  *         
  * @param  chData: Data to be writen to the display data ram or the command register
  * @param chCmd:  
  *                           0: Writes to the command register
  *                           1: Writes to the display data ram
  * @retval None
**/
static void ssd1305_write_byte(uint8_t chData, uint8_t chCmd) 
{
#ifdef INTERFACE_4WIRE_SPI
	
	__SSD1305_CS_CLR();
	
	if (chCmd) {
		__SSD1305_DC_SET();
	} else {
		__SSD1305_DC_CLR();
	}	
	__SSD1305_WRITE_BYTE(chData);
	
	__SSD1305_DC_SET();
	__SSD1305_CS_SET();
	
#elif defined(INTERFACE_IIC)
	
	iic_start();
	iic_write_byte(0x78);
	iic_wait_for_ack();
	if (chCmd) {
		iic_write_byte(0x40);
		iic_wait_for_ack();
	} else {
		iic_write_byte(0x00);
		iic_wait_for_ack();
	}
	iic_write_byte(chData);
	iic_wait_for_ack();
	
	iic_stop();
	
#endif
}   	  

/**
  * @brief  OLED turns on 
  *         
  * @param  None
  *         
  * @retval None
**/ 
void ssd1305_display_on(void)
{
	ssd1305_write_byte(0x8D, SSD1305_CMD);  
	ssd1305_write_byte(0x14, SSD1305_CMD);  
	ssd1305_write_byte(0xAF, SSD1305_CMD);  
}
   
/**
  * @brief  OLED turns off
  *         
  * @param  None
  *         
  * @retval  None
**/
void ssd1305_display_off(void)
{
	ssd1305_write_byte(0x8D, SSD1305_CMD);  
	ssd1305_write_byte(0x10, SSD1305_CMD); 
	ssd1305_write_byte(0xAE, SSD1305_CMD);  
}

/**
  * @brief  Refreshs the graphic ram
  *         
  * @param  None
  *         
  * @retval  None
**/

void ssd1305_refresh_gram(void)
{
	uint8_t i, j;
	
	for (i = 0; i < 4; i ++) {  
		ssd1305_write_byte(0xB0 + i, SSD1305_CMD);   
		ssd1305_write_byte(0x04, SSD1305_CMD); 
		ssd1305_write_byte(0x10, SSD1305_CMD);    
		for (j = 0; j < 128; j ++) {
			ssd1305_write_byte(s_chDispalyBuffer[j][i], SSD1305_DAT); 
		}
	}   
}


/**
  * @brief   Clears the screen
  *         
  * @param  None
  *         
  * @retval  None
**/

void ssd1305_clear_screen(uint8_t chFill)  
{ 
	uint8_t i, j;
	
	for (i = 0; i < 4; i ++) {
		ssd1305_write_byte(0xB0 + i, SSD1305_CMD);
		ssd1305_write_byte(0x04, SSD1305_CMD); 
		ssd1305_write_byte(0x10, SSD1305_CMD); 
		for (j = 0; j < 128; j ++) {
			s_chDispalyBuffer[j][i] = chFill;
		}
	}
	
	ssd1305_refresh_gram();
}

/**
  * @brief  Draws a piont on the screen
  *         
  * @param  chXpos: Specifies the X position
  * @param  chYpos: Specifies the Y position
  * @param  chPoint: 0: the point turns off    1: the piont turns on 
  *         
  * @retval None
**/

void ssd1305_draw_point(uint8_t chXpos, uint8_t chYpos, uint8_t chPoint)
{
	uint8_t chPos, chBx, chTemp = 0;
	
	if (chXpos > 127 || chYpos > 31) {
		return;
	}
	chPos = 7 - chYpos / 8; // 
	chBx = chYpos % 8;
	chTemp = 1 << (7 - chBx);
	
	if (chPoint) {
		s_chDispalyBuffer[chXpos][chPos] |= chTemp;
		
	} else {
		s_chDispalyBuffer[chXpos][chPos] &= ~chTemp;
	}
}
	  
/**
  * @brief  Fills a rectangle
  *         
  * @param  chXpos1: Specifies the X position 1 (X top left position)
  * @param  chYpos1: Specifies the Y position 1 (Y top left position)
  * @param  chXpos2: Specifies the X position 2 (X bottom right position)
  * @param  chYpos3: Specifies the Y position 2 (Y bottom right position)
  *         
  * @retval 
**/

void ssd1305_fill_screen(uint8_t chXpos1, uint8_t chYpos1, uint8_t chXpos2, uint8_t chYpos2, uint8_t chDot)  
{  
	uint8_t chXpos, chYpos; 
	
	for (chXpos = chXpos1; chXpos <= chXpos2; chXpos ++) {
		for (chYpos = chYpos1; chYpos <= chYpos2; chYpos ++) {
			ssd1305_draw_point(chXpos, chYpos, chDot);
		}
	}	
	
	ssd1305_refresh_gram();
}


/**
  * @brief Displays one character at the specified position    
  *         
  * @param  chXpos: Specifies the X position
  * @param  chYpos: Specifies the Y position
  * @param  chSize: 
  * @param  chMode
  * @retval 
**/
void ssd1305_display_char(uint8_t chXpos, uint8_t chYpos, uint8_t chChr, uint8_t chSize, uint8_t chMode)
{      	
	uint8_t i, j;
	uint8_t chTemp, chYpos0 = chYpos;
	
	chChr = chChr - ' ';				   
    for (i = 0; i < chSize; i ++) {   
		if (chSize == 12) {
			if (chMode) {
				chTemp = c_chFont1206[chChr][i];
			} else {
				chTemp = ~c_chFont1206[chChr][i];
			}
		} else {
			if (chMode) {
				chTemp = c_chFont1608[chChr][i];
			} else {
				chTemp = ~c_chFont1608[chChr][i];
			}
		}
		
        for (j = 0; j < 8; j ++) {
			if (chTemp & 0x80) {
				ssd1305_draw_point(chXpos, chYpos, 1);
			} else {
				ssd1305_draw_point(chXpos, chYpos, 0);
			}
			chTemp <<= 1;
			chYpos ++;
			
			if ((chYpos - chYpos0) == chSize) {
				chYpos = chYpos0;
				chXpos ++;
				break;
			}
		}  	 
    } 
}
static uint32_t pow(uint8_t m, uint8_t n)
{
	uint32_t result = 1;	 
	while(n --) result *= m;    
	return result;
}	


void ssd1305_display_num(uint8_t chXpos, uint8_t chYpos, uint32_t chNum, uint8_t chLen, uint8_t chSize)
{         	
	uint8_t i;
	uint8_t chTemp, chShow = 0;
	
	for(i = 0; i < chLen; i ++) {
		chTemp = (chNum / pow(10, chLen - i - 1)) % 10;
		if(chShow == 0 && i < (chLen - 1)) {
			if(chTemp == 0) {
				ssd1305_display_char(chXpos + (chSize / 2) * i, chYpos, ' ', chSize, 1);
				continue;
			} else {
				chShow = 1;
			}	 
		}
	 	ssd1305_display_char(chXpos + (chSize / 2) * i, chYpos, chTemp + '0', chSize, 1); 
	}
} 


/**
  * @brief  Displays a string on the screen
  *         
  * @param  chXpos: Specifies the X position
  * @param  chYpos: Specifies the Y position
  * @param  pchString: Pointer to a string to display on the screen 
  *         
  * @retval  None
**/
void ssd1305_display_string(uint8_t chXpos, uint8_t chYpos, const uint8_t *pchString, uint8_t chSize, uint8_t chMode)
{
    while (*pchString != '\0') {       
        if (chXpos > (SSD1305_WIDTH - chSize / 2)) {
			chXpos = 0;
			chYpos += chSize;
			if (chYpos > (SSD1305_HEIGHT - chSize)) {
				chYpos = chXpos = 0;
				ssd1305_clear_screen(0x00);
			}
		}
		
        ssd1305_display_char(chXpos, chYpos, *pchString, chSize, chMode);
        chXpos += chSize / 2;
        pchString ++;
    }
}

void ssd1305_draw_1616char(uint8_t chXpos, uint8_t chYpos, uint8_t chChar)
{
	uint8_t i, j;
	uint8_t chTemp = 0, chYpos0 = chYpos, chMode = 0;

	for (i = 0; i < 32; i ++) {
		chTemp = c_chFont1612[chChar - 0x30][i];
		for (j = 0; j < 8; j ++) {
			chMode = chTemp & 0x80? 1 : 0; 
			ssd1305_draw_point(chXpos, chYpos, chMode);
			chTemp <<= 1;
			chYpos ++;
			if ((chYpos - chYpos0) == 16) {
				chYpos = chYpos0;
				chXpos ++;
				break;
			}
		}
	}
}

void ssd1305_draw_3216char(uint8_t chXpos, uint8_t chYpos, uint8_t chChar)
{
	uint8_t i, j;
	uint8_t chTemp = 0, chYpos0 = chYpos, chMode = 0;

	for (i = 0; i < 64; i ++) {
		chTemp = c_chFont3216[chChar - 0x30][i];
		for (j = 0; j < 8; j ++) {
			chMode = chTemp & 0x80? 1 : 0; 
			ssd1305_draw_point(chXpos, chYpos, chMode);
			chTemp <<= 1;
			chYpos ++;
			if ((chYpos - chYpos0) == 32) {
				chYpos = chYpos0;
				chXpos ++;
				break;
			}
		}
	}
}

void ssd1305_draw_bitmap(uint8_t chXpos, uint8_t chYpos, const uint8_t *pchBmp, uint8_t chWidth, uint8_t chHeight)
{
	uint16_t i, j, byteWidth = (chWidth + 7) / 8;
	
    for(j = 0; j < chHeight; j ++){
        for(i = 0; i < chWidth; i ++ ) {
            if(*(pchBmp + j * byteWidth + i / 8) & (128 >> (i & 7))) {
                ssd1305_draw_point(chXpos + i, chYpos + j, 1);
            }
        }
    }
}



/**
  * @brief  SSd1305 initialization
  *         
  * @param  None
  *         
  * @retval None
**/
void ssd1305_init(void)
{

#ifdef INTERFACE_4WIRE_SPI	  
	__SSD1305_CS_SET();   //CS set
	__SSD1305_DC_CLR();   //D/C reset
	__SSD1305_RES_SET();  //RES set

#elif defined(INTERFACE_IIC)	  
	__SSD1305_CS_CLR();   //CS reset
	__SSD1305_DC_CLR();   //D/C reset
	__SSD1305_RES_SET();  //RES set

#endif

	ssd1305_write_byte(0xAE, SSD1305_CMD);//--turn off oled panel
	ssd1305_write_byte(0x04, SSD1305_CMD);//--Set Lower Column Start Address for Page Addressing Mode	
	ssd1305_write_byte(0x10, SSD1305_CMD);//--Set Higher Column Start Address for Page Addressing Mode
	ssd1305_write_byte(0x40, SSD1305_CMD);//---Set Display Start Line
	ssd1305_write_byte(0x81, SSD1305_CMD);//---Set Contrast Control for BANK0
	ssd1305_write_byte(0x80, SSD1305_CMD);//--Contrast control register is set
	ssd1305_write_byte(0xA1, SSD1305_CMD);//--Set Segment Re-map
	ssd1305_write_byte(0xA6, SSD1305_CMD);//--Set Normal/Inverse Display
	ssd1305_write_byte(0xA8, SSD1305_CMD);//--Set Multiplex Ratio
	ssd1305_write_byte(0x1F, SSD1305_CMD); 
	ssd1305_write_byte(0xC0, SSD1305_CMD);//--Set COM Output Scan Direction
	ssd1305_write_byte(0xD3, SSD1305_CMD);//--Set Display Offset
	ssd1305_write_byte(0x00, SSD1305_CMD);
	ssd1305_write_byte(0xD5, SSD1305_CMD);//--Set Display Clock Divide Ratio/ Oscillator Frequency
	ssd1305_write_byte(0xF0, SSD1305_CMD);
	ssd1305_write_byte(0xD8, SSD1305_CMD);//--Set Area Color Mode ON/OFF & Low Power Display Mode
	ssd1305_write_byte(0x05, SSD1305_CMD);
	ssd1305_write_byte(0xD9, SSD1305_CMD);//--Set pre-charge period
	ssd1305_write_byte(0xC2, SSD1305_CMD);
	ssd1305_write_byte(0xDA, SSD1305_CMD);//--Set COM Pins Hardware Configuration
	ssd1305_write_byte(0x12, SSD1305_CMD);
	ssd1305_write_byte(0xDB, SSD1305_CMD);//--Set VCOMH Deselect Level
	ssd1305_write_byte(0x3C, SSD1305_CMD);//--Set VCOM Deselect Level
	ssd1305_write_byte(0xAF, SSD1305_CMD);//--Normal Brightness Display ON
	
	ssd1305_clear_screen(0x00);
}

/*-------------------------------END OF FILE-------------------------------*/

