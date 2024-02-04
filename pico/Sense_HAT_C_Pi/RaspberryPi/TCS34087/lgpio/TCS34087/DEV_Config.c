/*****************************************************************************
* | File      	:   DEV_Config.c
* | Author      :   Waveshare team
* | Function    :   Hardware underlying interface
* | Info        :
*                Used to shield the underlying layers of each master 
*                and enhance portability
*----------------
* |	This version:   V1.0
* | Date        :   2019-01-18
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

int fd,GPIO_Handle;

/**
 * delay x ms
**/
void delay(UWORD ms)
{
    lguSleep(ms / 1000);
}

/******************************************************************************
function:	GPIO Function initialization and transfer
parameter:
Info:
******************************************************************************/
void DEV_GPIO_Mode(uint16_t Pin, uint16_t Mode)
{
    /*
        0:  INPT   
        1:  OUTP
    */
   if(Mode == 0 || Mode == LG_SET_INPUT){
        lgGpioClaimInput(GPIO_Handle,LFLAGS,Pin);
        // printf("IN Pin = %d\r\n",Pin);
    }else{
        lgGpioClaimOutput(GPIO_Handle, LFLAGS, Pin, LG_LOW);
        // printf("OUT Pin = %d\r\n",Pin);
    }

}

void DEV_Digital_Write(uint16_t Pin, uint8_t Value)
{
    lgGpioWrite(GPIO_Handle, Pin, Value);
}

uint8_t DEV_Digital_Read(uint16_t Pin)
{
    uint8_t Read_value = 0;
    Read_value = lgGpioRead(GPIO_Handle,Pin);
    return Read_value;
}

/******************************************************************************
function:   Set the I2C device address
parameter	:
        Add : Device address
******************************************************************************/
void DEV_Set_I2CAddress(UBYTE Add)
{
    fd = lgI2cOpen(1,Add,0);
}
/******************************************************************************
function:	
	I2C Write and Read
******************************************************************************/
void DEV_I2C_WriteByte(UBYTE add_, UBYTE data_)
{
	lgI2cWriteByteData(fd, add_, data_);
}

void DEV_I2C_WriteWord(UBYTE add_, UWORD data_)
{
	 lgI2cWriteWordData(fd, add_, data_);
}

UBYTE DEV_I2C_ReadByte(UBYTE add_)
{
	return lgI2cReadByteData(fd, add_);
}

UWORD DEV_I2C_ReadWord(UBYTE add_)
{
    return lgI2cReadWordData(fd, add_);
}
/******************************************************************************
function:	
	Module exits
******************************************************************************/
void DEV_ModuleExit(void)
{
    
}

/******************************************************************************
function:	
	Module initialization, BCM2835 library and initialization pins,
	I2C protocol
******************************************************************************/
UBYTE DEV_ModuleInit(void)
{
    char buffer[NUM_MAXBUF];
    FILE *fp;

    fp = popen("cat /proc/cpuinfo | grep 'Raspberry Pi 5'", "r");
    if (fp == NULL) {
        printf("It is not possible to determine the model of the Raspberry PI\n");
        return -1;
    }

    if(fgets(buffer, sizeof(buffer), fp) != NULL)  
    {
        GPIO_Handle = lgGpiochipOpen(4);
        if (GPIO_Handle < 0)
        {
            printf( "gpiochip4 Export Failed\n");
            return -1;
        }
    }
    else
    {
        GPIO_Handle = lgGpiochipOpen(0);
        if (GPIO_Handle < 0)
        {
            printf( "gpiochip0 Export Failed\n");
            return -1;
        }
    }
	//I2C Config
    DEV_GPIO_Mode(INT_PIN,0);
	fd = lgI2cOpen(1,IIC_Addr,0);
	return 0;
}

/************************************************/
