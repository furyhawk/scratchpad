/*****************************************************************************
* | File      	:   TCS34087.c
* | Author      :   Waveshare team
* | Function    :   TCS34087 driver
* | Info        :
*                TCS34087 initialization, reading data, writing data 
                 and data processing
*----------------
* |	This version:   V1.0
* | Date        :   2019-01-16
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
#include "TCS34087.h"

TCS34087_ASTEP_Time_t IntegrationTime_t = TCS34725_INTEGRATIONTIME_2_78MS;
TCS34087Gain_t  Gain_t = TCS34087_GAIN_64X;
UBYTE Atime = 0;
RGB_Offset rgb_offset;
/******************************************************************************
function:   Write a byte to TCS34087
parameter	:
        add : Register address
        data: Written data
******************************************************************************/
static void TCS34087_WriteByte(UBYTE add, UBYTE data)
{
    //Note: remember to add this when users write their own
    //Responsible for not finding the register, 
    //refer to the data sheet Command Register CMD(Bit 7)
    DEV_I2C_WriteByte(add, data);
}

/******************************************************************************
function:   Read a byte to TCS34087
parameter	:
        add : Register address
******************************************************************************/
static UBYTE TCS34087_ReadByte(UBYTE add)
{
    return DEV_I2C_ReadByte(add);
}
/******************************************************************************
function:   Wirt a word to TCS34087
parameter	:
        add : Register address
        data: Written data
******************************************************************************/
static void TCS34087_WirtWord(UBYTE add, UWORD data)
{
    DEV_I2C_WriteWord(add,data);
}
/******************************************************************************
function:   Read a word to TCS34087
parameter	:
        add : Register address
        data: Written data
******************************************************************************/
static UWORD TCS34087_ReadWord(UBYTE add)
{
    return DEV_I2C_ReadWord(add);
}

/******************************************************************************
function:   
        TCS34087 wake up
******************************************************************************/
static void TCS34087_Enable(void)
{
    // TCS34087_WriteByte(TCS34087_ENABLE, TCS34087_ENABLE_PON);
    // DEV_Delay_ms(3);
    TCS34087_WriteByte(TCS34087_ENABLE,TCS34087_ENABLE_FDEN | TCS34087_ENABLE_PON | TCS34087_ENABLE_AEN);
    DEV_Delay_ms(3);  
}

/******************************************************************************
function:   
        TCS34087 Sleep
******************************************************************************/
void TCS34087_Disable(void)
{
    /* Turn the device off to save power */
    UBYTE reg = 0;
    reg = TCS34087_ReadByte(TCS34087_ENABLE);
    TCS34087_WriteByte(TCS34087_ENABLE, reg & ~(TCS34087_ENABLE_FDEN | TCS34087_ENABLE_PON | TCS34087_ENABLE_AEN));
}

/******************************************************************************
function:   TCS34087 Set Integration Time
parameter	:
        Atime: Sets the number of ALS/color integration steps from 1 to 256.
        time: Integration Time Reference "TCS34087.h" Enumeration Type
******************************************************************************/
void TCS34087_Set_Integration_Time(UBYTE atime,TCS34087_ASTEP_Time_t time)
{
    TCS34087_WriteByte(TCS34087_ATIME,atime);
    /* Update the timing register */
    TCS34087_WirtWord(TCS34087_ASTEP, (0xE7<<8)|time);
    Atime = atime;
    IntegrationTime_t = time;
}

/******************************************************************************
function:   TCS34087 Set gain
parameter	:
        gain: gain Reference "TCS34087.h" Enumeration Type
******************************************************************************/
void TCS34087_Set_Gain(TCS34087Gain_t gain)
{
	TCS34087_WriteByte(TCS34087_CFG1, gain); 
    Gain_t = gain;
}

/******************************************************************************
function:   TCS34087 Set gain
parameter	:
        gain: gain Reference "TCS34087.h" Enumeration Type
******************************************************************************/
void TCS34087_Set_AGC_GAIN(UBYTE FD_GAIN,UBYTE AGAIN)
{
	TCS34087_WriteByte(TCS34087_AGC_GAIN_MAX, (FD_GAIN << 4) | AGAIN); 
}
/******************************************************************************
function:   Interrupt Enable
******************************************************************************/
static void TCS34087_Interrupt_Enable()
{
    UBYTE data = 0;
    data = TCS34087_ReadByte(TCS34087_INTENAB);
    TCS34087_WriteByte(TCS34087_INTENAB, data | TCS34087_INTENAB_AIEN );
}

/******************************************************************************
function:   Interrupt Disable
******************************************************************************/
void TCS34087_Interrupt_Disable()
{
    UBYTE data = 0;
    data = TCS34087_ReadByte(TCS34087_INTENAB);
    TCS34087_WriteByte(TCS34087_INTENAB, data & (~TCS34087_INTENAB_ASIEN | TCS34087_INTENAB_AIEN | TCS34087_INTENAB_SIEN));
}

/******************************************************************************
function:   Set Interrupt Persistence register, Interrupts need to be maintained 
            for several cycles
parameter	:
    TCS34087_PER : reference "TCS34087.h"
******************************************************************************/
static void TCS34087_Set_Interrupt_Persistence_Reg(UBYTE TCS34087_PER)
{
    if(TCS34087_PER < 0x10)
        TCS34087_WriteByte(TCS34087_PERS, TCS34087_PER);
    else 
        TCS34087_WriteByte(TCS34087_PERS, TCS34087_PERS_60_CYCLE);
}

/******************************************************************************
function:   Set Interrupt Threshold
parameter	:
    Threshold_H,Threshold_L: 
    Two 16-bit interrupt threshold registers allow the user to set limits 
    below and above a desired light level. An interrupt can be generated 
    when the Clear data (CDATA) is less than the Clear interrupt low 
    threshold (AILTx) or is greater than the Clear interrupt high 
    threshold (AIHTx)(Clear is the Clear ADC Channel Data Registers)
******************************************************************************/
static void TCS34087_Set_Interrupt_Threshold(UWORD Threshold_H, UWORD Threshold_L)
{
    TCS34087_WriteByte(TCS34087_AILTL, Threshold_L & 0xff);
    TCS34087_WriteByte(TCS34087_AILTH, Threshold_L >> 8);
    TCS34087_WriteByte(TCS34087_AIHTL, Threshold_H & 0xff);
    TCS34087_WriteByte(TCS34087_AIHTH, Threshold_H >> 8);
}



/******************************************************************************
function:   set config
parameter	:
        CFG_x: corresponding Config
        data  : Written data
******************************************************************************/
void TCS34087_Config(UBYTE CFG_x,UBYTE data)
{   
    TCS34087_WriteByte(CFG_x,data);
}


void RGB_offset(UBYTE Lum)
{
    rgb_offset.C = Lum;
    rgb_offset.G_Offset =  TCS34087_G_Offset;
    rgb_offset.B_Offset =  TCS34087_B_Offset;
}

/******************************************************************************
function:   TCS34087 initialization
parameter	:
        gain: gain Reference "TCS34087.h" Enumeration Type
        it  : Integration Time Reference "TCS34087.h" Enumeration Type
******************************************************************************/
UBYTE  TCS34087_Init(void)
{
	UBYTE ID = 0;
    DEV_Set_I2CAddress(TCS34087_ADDRESS);
	ID = TCS34087_ReadByte(TCS34087_ID);
    if(ID != 0x18){
        return 1;
    }
    //Set the integration time and gain
	TCS34087_Set_Integration_Time(TCS34087_ATIME_Time41,TCS34725_INTEGRATIONTIME_2_78MS);	
    TCS34087_Set_Gain(TCS34087_GAIN_128X);
    IntegrationTime_t = TCS34725_INTEGRATIONTIME_2_78MS;
    Gain_t = TCS34087_GAIN_128X;
    TCS34087_Enable();
    //Set Interrupt
    TCS34087_Interrupt_Enable();
    TCS34087_Set_Interrupt_Threshold(0xff00, 0x00ff);
    TCS34087_Set_Interrupt_Persistence_Reg(TCS34087_PERS_2_CYCLE);
    RGB_offset(LUM_1);
	return 0;
}

/******************************************************************************
function:   TCS34087 Read RGBC data
parameter	:
     R,G,B,C: RGBC Numerical value,Is a pointer
******************************************************************************/
RGB TCS34087_Get_RGBData()
{
    RGB temp;
    temp.C = TCS34087_ReadWord(TCS34087_ADATA0L);
    temp.R = TCS34087_ReadWord(TCS34087_ADATA1L);
    temp.G = TCS34087_ReadWord(TCS34087_ADATA2L);
    temp.B = TCS34087_ReadWord(TCS34087_ADATA3L);
    temp.W = TCS34087_ReadWord(TCS34087_ADATA4L);
    temp.F = TCS34087_ReadWord(TCS34087_ADATA5L);
    // printf("C: %d  R: %d G: %d B: %d W: %d F: %d ASTATUS: %x\r\n\n",temp.C,temp.R,temp.G,temp.B,temp.W,temp.F,TCS34087_ReadByte(0x94));
    
    switch (IntegrationTime_t){
        case TCS34725_INTEGRATIONTIME_2_78US:
              break;
        case TCS34725_INTEGRATIONTIME_nMS:
              DEV_Delay_ms(0.00278*(Atime + 1));
              break;
        case TCS34725_INTEGRATIONTIME_1_67MS:
              DEV_Delay_ms(2);
              break;
        case TCS34725_INTEGRATIONTIME_2_78MS:
              DEV_Delay_ms(3);
              break;
        case TCS34725_INTEGRATIONTIME_50MS:
              DEV_Delay_ms(50);
              break;
        case TCS34725_INTEGRATIONTIME_182MS:
              DEV_Delay_ms(182);
              break;
    }
    if (temp.C == 65535)
    {
        printf("\r\nInvalid data\r\n");
        temp.R = 0;
        temp.G = 0;
        temp.B = 0;
        return temp;
    }
    else
        return temp;
}
/******************************************************************************
function:   Clear interrupt flag
******************************************************************************/
static void TCS34087_Clear_Interrupt_Flag()
{
    TCS34087_WriteByte(TCS34087_STATUS, TCS34087_STATUS_ASAT);
}
/******************************************************************************
function:   Converts the raw R/G/B values to color temperature in degrees
            Kelvin
parameter	:
     rgb    : RGBC Numerical value
******************************************************************************/
UBYTE TCS34087_GetLux_Interrupt()
{
    if(DEV_Digital_Read(INT_PIN) == 0){
        TCS34087_Clear_Interrupt_Flag();
        return 1;
    }
    return 0;
}
/******************************************************************************
function:   Converts the raw R/G/B values to color temperature in degrees
            Kelvin
parameter	:
     rgb    : RGBC Numerical value
******************************************************************************/
UWORD TCS34087_Get_ColorTemp(RGB rgb)
{
    float cct;
    UWORD r_comp,b_comp,ir;
    ir = (rgb.R + rgb.G + rgb.B > rgb.C) ? (rgb.R + rgb.G + rgb.B - rgb.C) / 2 : 0;
    r_comp = rgb.R - ir;
    b_comp = rgb.B - ir;
    cct=TCS34087_CT_Coef * (float)(b_comp) / (float)(r_comp) + TCS34087_CT_Offset;
    
    return (uint16_t)cct;
}

/******************************************************************************
function:   Converts the raw R/G/B values to lux
parameter	:
     rgb    : RGBC Numerical value
******************************************************************************/
UWORD TCS34087_Get_Lux(RGB rgb)
{
    float lux,cpl,atime_ms,Gain_temp=1;
    UWORD ir=1;
    UWORD r_comp,g_comp,b_comp;
    
    atime_ms = ((256 - IntegrationTime_t) * 2.4);
    ir = (rgb.R + rgb.G + rgb.B > rgb.C) ? (rgb.R + rgb.G + rgb.B - rgb.C) / 2 : 0;
    r_comp = rgb.R - ir;
    g_comp = rgb.G - ir;
    b_comp = rgb.B - ir;
    
    switch (Gain_t)
    {
        case TCS34087_GAIN_0_5X:
              Gain_temp = 0.5;
              break;
        case TCS34087_GAIN_1X:
              Gain_temp = 1;
              break;
        case TCS34087_GAIN_4X:
              Gain_temp = 4;
              break;
        case TCS34087_GAIN_8X:
              Gain_temp = 8;
              break;
        case TCS34087_GAIN_16X:
              Gain_temp = 16;
              break;
        case TCS34087_GAIN_64X:
              Gain_temp = 64;
              break;
        case TCS34087_GAIN_128X:
              Gain_temp = 128;
              break;
        case TCS34087_GAIN_256X:
              Gain_temp = 256;
              break;
        case TCS34087_GAIN_512X:
              Gain_temp = 512;
              break;
        case TCS34087_GAIN_1024X:
              Gain_temp = 1024;
              break;
        case TCS34087_GAIN_2048X:
              Gain_temp = 2048;
              break;
    } 
    cpl = (atime_ms * Gain_temp) / (TCS34087_GA * TCS34087_DF);

    lux = (TCS34087_R_Coef * (float)(r_comp) + TCS34087_G_Coef * \
            (float)(g_comp) +  TCS34087_B_Coef * (float)(b_comp)) / cpl;
    return (UWORD)lux;
}

/******************************************************************************
function:   Convert raw RGB values to RGB888 format
parameter	:
     rgb    : RGBC Numerical value
******************************************************************************/
UDOUBLE TCS34087_GetRGB888(RGB rgb)
{
    if(rgb_offset.C!=0)
    {
        rgb.R = (rgb.R) / rgb_offset.C;
        rgb.G = (rgb.G) / rgb_offset.C / rgb_offset.G_Offset;
        rgb.B = (rgb.B) / rgb_offset.C / rgb_offset.B_Offset;
    }   
    rgb.R = ((rgb.R > 30)? (rgb.R - 30): (rgb.R)) * 255 /225;
    rgb.G = ((rgb.G > 30)? (rgb.G - 30): (rgb.G)) * 255 /225;
    rgb.B = ((rgb.B > 30)? (rgb.B - 30): (rgb.B)) * 255 /225;
    if(rgb.R>255)
        rgb.R = 255; 
    if(rgb.G>255)
        rgb.G = 255; 
    if(rgb.B>255)
        rgb.B = 255;  
    return (rgb.R << 16) | (rgb.G << 8) | (rgb.B);
}



/******************************************************************************
function:   Convert raw RGB values to RGB565 format
parameter	:
     rgb    : RGBC Numerical value
******************************************************************************/
UWORD TCS34087_GetRGB565(RGB rgb)
{
    if(rgb_offset.C!=0)
    {
        rgb.R = (rgb.R) / rgb_offset.C;
        rgb.G = (rgb.G) / rgb_offset.C / rgb_offset.G_Offset;
        rgb.B = (rgb.B) / rgb_offset.C / rgb_offset.B_Offset;
    }   
    rgb.R = ((rgb.R > 30)? (rgb.R - 30): (rgb.R)) * 255 /225;
    rgb.G = ((rgb.G > 30)? (rgb.G - 30): (rgb.G)) * 255 /225;
    rgb.B = ((rgb.B > 30)? (rgb.B - 30): (rgb.B)) * 255 /225;
    if(rgb.R>255)
        rgb.R = 255; 
    if(rgb.G>255)
        rgb.G = 255; 
    if(rgb.B>255)
        rgb.B = 255; 
    return ((rgb.R>>3) << 11) | ((rgb.G>>2) << 5) | ((rgb.B>>3));
}

/******************************************************************************
function:   Set the onboard LED brightness
parameter	:
     value : 0 - 100
******************************************************************************/




