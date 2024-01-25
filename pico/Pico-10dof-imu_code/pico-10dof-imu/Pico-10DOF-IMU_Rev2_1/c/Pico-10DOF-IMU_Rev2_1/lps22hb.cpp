#include <stdio.h>
#include <math.h>
#include "lps22hb.h"
#include <Wire.h>

#ifdef __cplusplus
extern "C" {
#endif

char I2C_readByte(char reg)
{
  uint8_t data; // `data` will store the register data

  // Initialize the Tx buffer
  Wire1.beginTransmission(LPS22HB_I2C_ADDRESS);
  // Put slave register address in Tx buffer
  Wire1.write(reg);
  // Send the Tx buffer, but send a restart to keep connection alive
  Wire1.endTransmission(false);
  // Read one byte from slave register address
  Wire1.requestFrom(LPS22HB_I2C_ADDRESS, (uint8_t) 1);
  // Fill Rx buffer with result
  data = Wire1.read();
  // Return data read from slave register
  return data;
}

unsigned short I2C_readU16(char reg)
{
  Wire1.beginTransmission(LPS22HB_I2C_ADDRESS);
  // Put slave register address in Tx buffer
  Wire1.write(reg);
  // Send the Tx buffer, but send a restart to keep connection alive
  Wire1.endTransmission(false);

  uint8_t i = 0;
  uint8_t buf[2];
  // Read bytes from slave register address
  Wire1.requestFrom(LPS22HB_I2C_ADDRESS, (uint8_t)2);
  while (Wire1.available())
  {
    // Put read results in the Rx buffer
    buf[i++] = Wire1.read();
  }
  int value = buf[1] * 0x100 + buf[0];

  return value; // Return number of bytes written
}

void I2C_writeByte(char reg, char val)
{
  Wire1.beginTransmission(LPS22HB_I2C_ADDRESS);  // Initialize the Tx buffer
  Wire1.write(reg);      // Put slave register address in Tx buffer
  Wire1.write(val);                 // Put data in Tx buffer
  Wire1.endTransmission();           // Send the Tx buffer
}

void LPS22HB_RESET()
{   uint8_t Buf;
    Buf=I2C_readU16(LPS_CTRL_REG2);
    Buf|=0x04;                                         
    I2C_writeByte(LPS_CTRL_REG2,Buf);                  //SWRESET Set 1
    while(Buf)
    {
        Buf=I2C_readU16(LPS_CTRL_REG2);
        Buf&=0x04;
    }
}

void LPS22HB_START_ONESHOT() {
    uint8_t Buf;
    Buf=I2C_readU16(LPS_CTRL_REG2);
    Buf|=0x01;                                         //ONE_SHOT Set 1
    I2C_writeByte(LPS_CTRL_REG2,Buf);
}

uint8_t LPS22HB_INIT()
{
    if(I2C_readByte(LPS_WHO_AM_I)!=LPS_ID) return 0;    //Check device ID 
    LPS22HB_RESET();                                    //Wait for reset to complete
    I2C_writeByte(LPS_CTRL_REG1 ,   0x02);              //Low-pass filter disabled , output registers not updated until MSB and LSB have been read , Enable Block Data Update , Set Output Data Rate to 0 
    return 1;
}

#ifdef __cplusplus
}
#endif
