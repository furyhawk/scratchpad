#include <stdio.h>
#include "LCD_Driver.h"
#define VCCSTATE SH1106_SWITCHCAPVCC


char buffer[1024];

void LCD_Write_Command(char cmd) 
{
    DEV_Digital_Write(DEV_DC_PIN, LOW);
    DEV_SPI_WriteByte(cmd);
}

static void LCD_Reset(void)
{
    DEV_Digital_Write(DEV_RST_PIN, 1);
	DEV_Delay_ms(200);
	DEV_Digital_Write(DEV_RST_PIN, 0);
	DEV_Delay_ms(200);
	DEV_Digital_Write(DEV_RST_PIN, 1);
	DEV_Delay_ms(200);
}

void SH1106_begin()
{
    LCD_Reset();
    LCD_Write_Command(0xAE);//--turn off oled panel
    LCD_Write_Command(0x02);//---set low column address
    LCD_Write_Command(0x10);//---set high column address
    LCD_Write_Command(0x40);//--set start line address  Set Mapping RAM Display Start Line (0x00~0x3F)
    LCD_Write_Command(0x81);//--set contrast control register
    LCD_Write_Command(0xA0);//--Set SEG/Column Mapping     
    LCD_Write_Command(0xC0);//Set COM/Row Scan Direction   
    LCD_Write_Command(0xA6);//--set normal display
    LCD_Write_Command(0xA8);//--set multiplex ratio(1 to 64)
    LCD_Write_Command(0x3F);//--1/64 duty
    LCD_Write_Command(0xD3);//-set display offset    Shift Mapping RAM Counter (0x00~0x3F)
    LCD_Write_Command(0x00);//-not offset
    LCD_Write_Command(0xd5);//--set display clock divide ratio/oscillator frequency
    LCD_Write_Command(0x80);//--set divide ratio, Set Clock as 100 Frames/Sec
    LCD_Write_Command(0xD9);//--set pre-charge period
    LCD_Write_Command(0xF1);//Set Pre-Charge as 15 Clocks & Discharge as 1 Clock
    LCD_Write_Command(0xDA);//--set com pins hardware configuration
    LCD_Write_Command(0x12);
    LCD_Write_Command(0xDB);//--set vcomh
    LCD_Write_Command(0x40);//Set VCOM Deselect Level
    LCD_Write_Command(0x20);//-Set Page Addressing Mode (0x00/0x01/0x02)
    LCD_Write_Command(0x02);//
    LCD_Write_Command(0xA4);// Disable Entire Display On (0xa4/0xa5)
    LCD_Write_Command(0xA6);// Disable Inverse Display On (0xa6/a7) 
    LCD_Write_Command(0xAF);//--turn on oled panel
}
void SH1106_clear()
{
    int i;
    for(i = 0; i < sizeof(buffer); i++)
    {
        buffer[i] = 0;
    }
}
void SH1106_pixel(int x, int y, char color)
{
    if(x > WIDTH || y > HEIGHT)return ;
    if(color)
        buffer[x+(y/8)*WIDTH] |= 1<<(y%8);
    else
        buffer[x+(y/8)*WIDTH] &= ~(1<<(y%8));
}

void SH1106_display()
{
    uint8_t page;
    char *pBuf = (char *)buffer;
    
    for (page = 0; page < 8; page++) {  
        /* set page address */
        LCD_Write_Command(0xB0 + page);
        /* set low column address */
        LCD_Write_Command(0x02); 
        /* set high column address */
        LCD_Write_Command(0x10); 
        /* write data */
        DEV_Digital_Write(DEV_DC_PIN, HIGH);
        for(int i=0;i<WIDTH; i++)
            DEV_SPI_WriteByte(pBuf[i]); 
        pBuf += WIDTH;
    }
}
