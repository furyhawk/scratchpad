/*****************************************************************************
* | File      	:   TCS34087.h
* | Author      :   Waveshare team
* | Function    :   TCS34087 driver
* | Info        :
*                TCS34087 initialization, reading data, writing data 
                 and data processing
*----------------
* |	This version:   V1.0
* | Date        :   2022-08-12
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
******************************************************************************/
#ifndef __TCS_H
#define __TCS_H

#include "DEV_Config.h"

/**
* Device address
**/
// I2C 7-bit address 0x29, 8-bit address 0x52
#define TCS34087_ADDRESS          0x29

/**
* Register
**/
#define TCS34087_ENABLE           0x80    /* Enable device states */ 
#define TCS34087_ENABLE_FDEN      0x40    /* Flicker Detection Enable -  Writing a 1 activates flicker detection*/
#define TCS34087_ENABLE_WEN       0x08    /* Wait enable - Writing 1 activates the wait timer */
#define TCS34087_ENABLE_AEN       0x02    /* ALS Enable - Writing a 1 enables ALS/Color */
#define TCS34087_ENABLE_PON       0x01    /* Power ON. When asserted, the internal oscillator is activated, allowing timers and ADC channels to operate. */
/* PON: Only set this bit after all other registers have been initialized by the host. */


#define TCS34087_ATIME            0x81    /* ALS integration time */
#define TCS34087_ATIME_Time0      0x00    /* ATIME = ASTEP */
#define TCS34087_ATIME_Time5      0x05    /* ATIME = ASTEP × (n+1)  n=5*/
#define TCS34087_ATIME_Time41     0x41    /* ATIME = ASTEP × (n+1)  n=10*/
#define TCS34087_ATIME_TimeFF     0xFF    /* ATIME = 256 × ASTEP */

#define TCS34087_ASTEP            0x82    /* ALS Integration Time Step Size */

#define TCS34087_WTIME            0x83    /* Wait time (if TCS34087_ENABLE_WEN is asserted) */

#define TCS34087_AILTL            0x84    /* ALS interrupt low threshold */
#define TCS34087_AILTH            0x85

#define TCS34087_AIHTL            0x86    /* ALS interrupt high threshold */
#define TCS34087_AIHTH            0x87

#define TCS34087_AUXID            0x90    /* Auxiliary identification 0x4A*/
#define TCS34087_REVID            0x91    /* Revision identification 0X53*/
#define TCS34087_ID               0x92    /* Device identification 0x18 = TCS34087 */


#define TCS34087_STATUS           0x93    /* Device status one */
#define TCS34087_STATUS_ASAT      0x80    /* ALS and Flicker Detect Saturation */
#define TCS34087_STATUS_AINT      0x04    /* ALS Interrupt */
#define TCS34087_STATUS_CINT      0x02    /* Calibration Interrupt */
#define TCS34087_STATUS_SINT      0x01    /* System Interrupt */

#define TCS34087_ASTATUS          0x94    /* ALS status */
#define TCS34087_ASTATUS_ASAT_STATUS  0x80 /* ALS Saturation Status */
#define TCS34087_ASTATUS_AGAIN_STATUS 0x00 /* ALS Gain Status */

#define TCS34087_ADATA0L          0x95    /* ALS channel zero data Clear*/
#define TCS34087_ADATA0H          0x96

#define TCS34087_ADATA1L          0x97    /* ALS channel one data Red*/
#define TCS34087_ADATA1H          0x98

#define TCS34087_ADATA2L          0x99    /* ALS channel two data Green*/
#define TCS34087_ADATA2H          0x9A

#define TCS34087_ADATA3L          0x9B    /* ALS channel three data Blue*/
#define TCS34087_ADATA3H          0x9C

#define TCS34087_ADATA4L          0x9D    /* ALS channel four data WIDEBAND data*/
#define TCS34087_ADATA4H          0x9E

#define TCS34087_ADATA5L          0x9F    /* ALS channel five data  FLICKER data*/
#define TCS34087_ADATA5H          0xA0

#define TCS34087_STATUS2          0xA3    /* Device status two */
#define TCS34087_AVALID           0x40    /* ALS Valid */
#define TCS34087_ASAT_DIGITAL     0x10    /* ALS Digital Saturation */
#define TCS34087_ASAT_ANALOG      0x80    /* ALS Analog Saturation */
#define TCS34087_FDSAT_ANALOG     0x02    /* Flicker Detect Analog Saturation */
#define TCS34087_FDSAT_DIGITAL    0x01    /* Flicker Detect Digital Saturation */

#define TCS34087_STATUS3          0xA4    /* Device status three */
#define TCS34087_STATUS3_AINT_AIHT  0x20  /* ALS Interrupt High */
#define TCS34087_STATUS3_AINT_AILT  0x10  /* ALS Interrupt Low */

#define TCS34087_STATUS5          0xA6    /* Device status five */
#define TCS34087_STATUS5_SINT_FD  0x08    /* Flicker Detect Interrupt */

#define TCS34087_STATUS6          0xA7    /* Device status six */
#define TCS34087_STATUS6_OVTEMP_DETECTED    0x20   /* Over Temperature Detected */
#define TCS34087_STATUS6_FD_TRIGGER_ERROR   0x10   /* Flicker Detect Trigger Error */
#define TCS34087_STATUS6_ALS_TRIGGER_ERROR  0x04   /* ALS Trigger Error */
#define TCS34087_STATUS6_SAI_ACTIVE         0x02   /* Sleep After Interrupt Active */
#define TCS34087_STATUS6_INIT_BUSY          0x01   /* Initialization Busy */

#define TCS34087_CFG0             0xA9    /* Configuration zero */
#define TCS34087_CFG0_LOWPOWER_IDLE 0x40 /* Low Power Idle */
#define TCS34087_CFG0_ALS_TRIGGER_LONG 0x04 /* ALS Trigger Long */
#define TCS34087_CFG0_RAM_BANK      0x00   /* RAM Bank Selection */

#define TCS34087_CFG1             0xAA    /* Configuration one */
#define TCS34087_CFG1_AGAIN       0x09    /* ALS Gain. Sets the ALS sensitivity. 
Value = 0x00~0x0C Value = 0x00 GAIN = 0.5x GAIN = 2^(Value-1)*/

#define TCS34087_CFG3             0xAC    /* Configuration three */
#define TCS34087_CFG3_SAI         0x10    /* Sleep After Interrupt */

#define TCS34087_CFG4             0xAD    /* Configuration four */
#define TCS34087_CFG4_INT_PINMAP  0x40    /* Interrupt Pin Map */
#define TCS34087_CFG4_INT_INVERT  0x08    /* Interrupt Invert */

#define TCS34087_CFG6             0xAF    /* Configuration six */
#define TCS34087_CFG6_ALS_AGC_MAX_GAIN_START  0x40 /* Figure 35 */

#define TCS34087_CFG8             0xB1    /* Configuration eight */
#define TCS34087_CFG8_ALS_AGC_ENABLE 0x04 /* ALS AGC Enable */

#define TCS34087_CFG9             0xB2    /* Configuration nine */
#define TCS34087_CFG9_SIEN_FD     0x40    /* System Interrupt Flicker Detection */

#define TCS34087_CFG10            0xB3    /* Configuration ten */
#define TCS34087_CFG10_ALS_AGC_HIGH_HYST 0xC0 /* ALS AGC High Hysteresis */
#define TCS34087_CFG10_ALS_AGC_LOW_HYST  0x30 /* ALS AGC Low Hysteresis */
#define TCS34087_CFG10_FD_PERS    0x02    /* Flicker Detect Persistence */


#define TCS34087_CFG11            0xB4    /* Configuration eleven */
#define TCS34087_CFG11_AINT_DIRECT  0x80  /* ALS Interrupt Direct */

#define TCS34087_CFG12            0xB5    /* Configuration twelve */
#define TCS34087_CFG12_ALS_TH_CHANNEL 0x00 /* ALS Thresholds Channel */

#define TCS34087_PERS             0xBD     /* Persistence configuration */
#define TCS34087_PERS_APERS       0x00     /* ALS Interrupt Persistence */
#define TCS34087_PERS_2_CYCLE     0x02     /* 2 clean channel values outside threshold range generates an interrupt */
#define TCS34087_PERS_60_CYCLE    0x0F     /* 60 clean channel values outside threshold range generates an interrupt */

#define TCS34087_ASTEPL           0xCA    /* ALS integration step size */
#define TCS34087_ASTEPH           0xCB    

#define TCS34087_AGC_GAIN_MAX     0xCF    /* Maximum AGC gains */
#define TCS34087_AGC_GAIN_MAX_AGC_FD_GAIN_MAX 0x90 /* Flicker Detection AGC Gain Max */
#define TCS34087_AGC_GAIN_MAX_AGC_AGAIN_MAX   0x09 /* ALS AGC Gain Max */

#define TCS34087_AZ_CONFIG        0xD6    /* Autozero configuration */ 
#define TCS34087_AZ_CONFIG_AZ_NTH_ITERATION 0xFF /* ALS Autozero Frequency */

#define TCS34087_FD_STATUS        0xDB    /* Flicker detection configuration zero */
#define TCS34087_FD_STATUS_FD_MEASUREMENT_VALID   0x20  /* Flicker Detection Measurement Valid */
#define TCS34087_FD_STATUS_FD_SATURATION_DETECTED 0x10  /* Flicker Saturation Detected */
#define TCS34087_FD_STATUS_FD_120HZ_FLICKER_VALID 0x08  /* Flicker Detection 120Hz Flicker Valid */
#define TCS34087_FD_STATUS_FD_100HZ_FLICKER_VALID 0x04  /* Flicker Detection 100Hz Flicker Valid */
#define TCS34087_FD_STATUS_FD_120HZ_FLICKER       0x02  /* Flicker Detected at 120Hz */
#define TCS34087_FD_STATUS_FD_100HZ_FLICKER       0x01  /* Flicker Detected at 100Hz */


#define TCS34087_INTENAB          0xF9    /* Enable interrupts */
#define TCS34087_INTENAB_ASIEN    0x80    /* ALS and Flicker Detect Saturation Interrupt Enable */
#define TCS34087_INTENAB_AIEN     0x04    /* ALS Interrupt Enable */
#define TCS34087_INTENAB_SIEN     0x01    /* System Interrupt Enable */

#define TCS34087_CONTROL          0xFA    /* Control */
#define TCS34087_CONTROL_ALS_MANUAL_AZ     0x04 /* ALS Manual Autozero */
#define TCS34087_CONTROL_CLEAR_SAI_ACTIVE  0x01 /* Clear Sleep-After-Interrupt Active */


/**
* Offset and Compensated
**/
#define TCS34087_R_Coef 0.136 
#define TCS34087_G_Coef 1.000
#define TCS34087_B_Coef -0.444
#define TCS34087_GA 1.0
#define TCS34087_DF 310.0
#define TCS34087_CT_Coef 3810.0
#define TCS34087_CT_Offset 1391.0
#define TCS34087_R_Offset 1.0 

#define TCS34087_G_Offset 0.92
#define TCS34087_B_Offset 0.73
/**
* Lum
**/
typedef enum
{
  LUM_0  = 36,   /**<  Clear channel < 30000   */
  LUM_1  = 48,   /**<  Clear channel < 40000  */
  LUM_2  = 65,   /**<  Clear channel < 50000    */
  LUM_3  = 80,   /**<  Clear channel < 60000  */
  LUM_4  = 104   /**<  Clear channel < 65535   */
}
LUM_Value;
/**
* Integration Time
**/
typedef enum
{
  TCS34725_INTEGRATIONTIME_2_78US  = 0x00,   /**<  STEP SIZE = 2.78us  VALUE = 0   */
  TCS34725_INTEGRATIONTIME_nMS     = 0x01,   /**<  STEP SIZE = 2.78us x (n+1)  VALUE = n  */
  TCS34725_INTEGRATIONTIME_1_67MS  = 0x02,   /**<  STEP SIZE = 1.67ms    VALUE = 599    */
  TCS34725_INTEGRATIONTIME_2_78MS  = 0x03,   /**<  STEP SIZE = 2.78ms   VALUE = 999  */
  TCS34725_INTEGRATIONTIME_50MS    = 0x04,   /**<  STEP SIZE = 50ms   VALUE = 17999   */
  TCS34725_INTEGRATIONTIME_182MS   = 0x05    /**<  STEP SIZE = 182ms   VALUE = 65535  */
}
TCS34087_ASTEP_Time_t;

/**
* CFG1 Gain
**/
typedef enum
{
  TCS34087_GAIN_0_5X              = 0x00,   /**<  0.5x gain  */
  TCS34087_GAIN_1X                = 0x01,   /**<  No gain  */
  TCS34087_GAIN_4X                = 0x03,   /**<  4x gain  */
  TCS34087_GAIN_8X                = 0x04,   /**<  8x gain  */
  TCS34087_GAIN_16X               = 0x05,   /**<  16x gain */
  TCS34087_GAIN_64X               = 0x07,   /**<  64x gain */
  TCS34087_GAIN_128X              = 0x08,   /**<  128x gain */
  TCS34087_GAIN_256X              = 0x09,   /**<  256x gain */
  TCS34087_GAIN_512X              = 0x0A,   /**<  512x gain */
  TCS34087_GAIN_1024X             = 0x0B,   /**<  1024x gain */
  TCS34087_GAIN_2048X             = 0x0C,   /**<  2048x gain */
}
TCS34087Gain_t;


typedef struct{
   UWORD R;
   UWORD G;
   UWORD B;
   UWORD C;
   UWORD W;
   UWORD F;
}RGB;

typedef struct{
  UWORD C;
  float G_Offset;
  float B_Offset;
}RGB_Offset;

/*-----------------------------------------------------------------------------*/
//initialization
UBYTE TCS34087_Init(void);
void TCS34087_SetLight(UWORD value);
void TCS34087_Set_Gain(TCS34087Gain_t gain);
void TCS34087_Set_Integration_Time(UBYTE atime,TCS34087_ASTEP_Time_t time);
// void TCS34087_Set_Config(TCS34087Gain_t gain, TCS34087IntegrationTime_t it);

//Read Color
RGB TCS34087_Get_RGBData(void);
UWORD TCS34087_Get_ColorTemp(RGB rgb);
UWORD TCS34087_GetRGB565(RGB rgb);
UDOUBLE TCS34087_GetRGB888(RGB rgb);


//Read Light
UWORD TCS34087_Get_Lux(RGB rgb);
UBYTE TCS34087_GetLux_Interrupt();
#endif
