#include <math.h>
#include "SHTC3.h"

char SHTC3_CheckCrc(uint8_t data[],unsigned char len,unsigned char checksum)
{
  unsigned char bit;        // bit mask
  unsigned char crc = 0xFF; // calculated checksum
  unsigned char byteCtr;    // byte counter
  // calculates 8-Bit checksum with given polynomial
  for(byteCtr = 0; byteCtr < len; byteCtr++) {
    crc ^= (data[byteCtr]);
    for(bit = 8; bit > 0; --bit) {
      if(crc & 0x80) {
        crc = (crc << 1) ^ CRC_POLYNOMIAL;
      } else {
        crc = (crc << 1);
      }
    }
  }

  // verify checksum
  if(crc != checksum) {                 
    return 1;                       //Error
  } else {
    return 0;                       //No error
  }       
}
void SHTC3_WriteCommand(unsigned short cmd)
{   
    uint8_t buf[] = {(cmd>>8) ,cmd};
    HAL_I2C_Master_Transmit(&hi2c1,SHTC3_I2C_ADDRESS,buf,2,100);          
                                                 //1:error 0:No error
}
void SHTC3_WAKEUP(void)
{     
    SHTC3_WriteCommand(SHTC3_WakeUp);                  // write wake_up command  
    delay_us(300);                          //Delay 300us
      
}
void SHTC3_SLEEP(void)
{    
 //   bcm2835_i2c_begin();
    SHTC3_WriteCommand(SHTC3_Sleep);                        // Write sleep command
      
}

void SHTC_SOFT_RESET(void)
{   
    SHTC3_WriteCommand(SHTC3_Software_RES);                 // Write reset command
    delay_us(300);                                 //Delay 300us
     
}


float TH_Value()
{
		unsigned short TH_DATA;
		uint8_t checksum;
    uint8_t buf[3];
		SHTC3_WriteCommand(SHTC3_NM_CD_ReadTH);                 //Read temperature first,clock streching disabled (polling)
    HAL_Delay(20);
    HAL_I2C_Master_Receive(&hi2c1,SHTC3_I2C_ADDRESS,buf,3,1000);

   checksum=buf[2];
   if(!SHTC3_CheckCrc(buf,2,checksum))
        TH_DATA=(buf[0]<<8|buf[1]);
	 return (175 * (float)TH_DATA / 65536.0f - 45.0f);       //Calculate temperature value
}

float RH_Value()
{
		unsigned short RH_DATA;
		uint8_t checksum;
		uint8_t buf[3];
		SHTC3_WriteCommand(SHTC3_NM_CD_ReadRH);                 //Read temperature first,clock streching disabled (polling)
		HAL_Delay(20);
		HAL_I2C_Master_Receive(&hi2c1,SHTC3_I2C_ADDRESS,buf,3,1000);

    checksum=buf[2];
    if(!SHTC3_CheckCrc(buf,2,checksum))
        RH_DATA=(buf[0]<<8|buf[1]);
		return (100 * (float)RH_DATA / 65536.0f);									//Calculate temperature value
}
