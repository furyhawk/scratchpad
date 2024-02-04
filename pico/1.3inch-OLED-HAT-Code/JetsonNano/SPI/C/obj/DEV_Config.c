/*****************************************************************************
* | File      	:   DEV_Config.c
* | Author      :   Waveshare team
* | Function    :   Hardware underlying interface
* | Info        :
*                Used to shield the underlying layers of each master 
*                and enhance portability
*----------------
* |	This version:   V1.0
* | Date        :   2018-12-18
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
#include "DEV_Config.h"



static void DEV_GPIOConfig(void)
{
    SYSFS_GPIO_Export(DEV_RST_PIN);
    SYSFS_GPIO_Export(DEV_DC_PIN);
    SYSFS_GPIO_Export(DEV_BL_PIN);
    SYSFS_GPIO_Export(DEV_CS_PIN);

    SYSFS_GPIO_Direction(DEV_RST_PIN, OUT);
    SYSFS_GPIO_Direction(DEV_DC_PIN, OUT);
    SYSFS_GPIO_Direction(DEV_BL_PIN, OUT);
    SYSFS_GPIO_Direction(DEV_CS_PIN, OUT);    
}


/******************************************************************************
function:	
	Module initialization, BCM2835 library and initialization pins,
	SPI protocol, PWM
******************************************************************************/
UBYTE DEV_ModuleInit(void)
{
    DEV_GPIOConfig();
    
    SYSFS_software_spi_begin();
    SYSFS_software_spi_setBitOrder(SOFTWARE_SPI_MSBFIRST);
    SYSFS_software_spi_setDataMode(SOFTWARE_SPI_Mode0);
    SYSFS_software_spi_setClockDivider(SOFTWARE_SPI_CLOCK_DIV2);
    
    
    
    
    
    
    DEV_Digital_Write(DEV_BL_PIN, 1);
    DEV_Digital_Write(DEV_CS_PIN, 0);

    return 0;
}


void DEV_SPI_WriteByte(UBYTE value)
{
    SYSFS_software_spi_transfer(value);
}


void DEV_Delay_us(UWORD xus)
{
    for(int j=xus; j > 0; j--);
}

void DEV_Delay_ms(UWORD xms)
{
    for(int j=xms; j > 0; j--)
        for(int i=100000; i > 0; i--);

}


/******************************************************************************
function:	
	Module exits, closes SPI and BCM2835 library
******************************************************************************/
void DEV_ModuleExit(void)
{
    SYSFS_software_spi_end(); 
    
    SYSFS_GPIO_Write(DEV_RST_PIN, LOW);
    SYSFS_GPIO_Write(DEV_DC_PIN, LOW);
    SYSFS_GPIO_Write(DEV_BL_PIN, LOW);

}

