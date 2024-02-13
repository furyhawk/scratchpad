#include "IMU_AK09918.h"

uint8_t buf[8];
IMU_ST_SENSOR_DATA gstMagOffset = {0,0,0};

void AK09918_CalAvgValue(uint8_t *pIndex, int16_t *pAvgBuffer, int16_t InVal, int32_t *pOutVal);

void AK09918_ReadnByte(uint8_t reg)
{
    Wire.beginTransmission(AK09918_I2C_ADDR);
    Wire.write(reg);
    Wire.endTransmission();

    Wire.requestFrom(AK09918_I2C_ADDR, 8);
    for (int i = 0; i < 8; i++)
    {
      buf[i] = Wire.read();
    }

}

uint8_t AK09918_I2C_Write(uint8_t reg, uint8_t Value)
{
    Wire.beginTransmission(AK09918_I2C_ADDR);
    Wire.write(reg);
    Wire.write(Value);
    Wire.endTransmission();
    return 0;
}

uint8_t AK09918_I2C_ReadByte(uint8_t reg)
{
    uint8_t value;
    Wire.beginTransmission(AK09918_I2C_ADDR);
    Wire.write(reg);
    Wire.endTransmission();

    Wire.requestFrom(AK09918_I2C_ADDR, 1);
    value = Wire.read();
    return value;
}

void AK09918_init(uint8_t mode)
{   
    if(AK09918_I2C_ReadByte(AK09918_WIA2) != 0x0C)
        Serial.printf("AK09918 Fail to read");
    else{
        Serial.println("AK09918 Success to read");
        AK09918_I2C_Write(AK09918_CNTL2,mode);
    }
    // AK09918_MagOffset();
}

void AK09918_Read_data(IMU_ST_SENSOR_DATA *pstMagnRawData)
{
    uint8_t counter = 20;
    uint8_t u8Data[6];
    int16_t s16Buf[3] = {0};
    int32_t s32OutBuf[3] = {0};
    static AK09918_DATA sstAvgBuf[3];

    while(counter > 0)
    {
        u8Data[0] = AK09918_I2C_ReadByte(AK09918_ST1);
        if((u8Data[0] & 0x01)!=0)
            break;
        counter--;
    }


    AK09918_ReadnByte(AK09918_HXL);
    s16Buf[0] = ((short int)buf[1] << 8) | buf[0];
    s16Buf[1] = ((short int)buf[3] << 8) | buf[2];
    s16Buf[2] = ((short int)buf[5] << 8) | buf[4];

    for (int i = 0; i < 3; i++)
        AK09918_CalAvgValue(&sstAvgBuf[i].u8Index, sstAvgBuf[i].s16AvgBuffer, s16Buf[i], s32OutBuf + i);
    
    pstMagnRawData->s16X = s32OutBuf[0] - gstMagOffset.s16X;
    pstMagnRawData->s16Y = s32OutBuf[1] - gstMagOffset.s16Y;
    pstMagnRawData->s16Z = s32OutBuf[2] - gstMagOffset.s16Z;
    // Serial.printf("Magnetic:       X= %d ,      Y  = %d ,      Z  = %d\r\n\n",s32OutBuf[0],s32OutBuf[1],s32OutBuf[2]);
    
}

void AK09918_CalAvgValue(uint8_t *pIndex, int16_t *pAvgBuffer, int16_t InVal, int32_t *pOutVal)
{ 
  uint8_t i;
  
  *(pAvgBuffer + ((*pIndex) ++)) = InVal;
    *pIndex &= 0x07;
    
    *pOutVal = 0;
  for(i = 0; i < 8; i ++) 
    {
      *pOutVal += *(pAvgBuffer + i);
    }
    *pOutVal >>= 3;
}

void AK09918_MagOffset(void)
{
  unsigned char  i;
  IMU_ST_SENSOR_DATA Mag;
  int s32TempGx = 0, s32TempGy = 0, s32TempGz = 0;
  for(i = 0; i < 32; i ++)
  {
    AK09918_Read_data(&Mag);
    s32TempGx += Mag.s16X;
    s32TempGy += Mag.s16Y;
    s32TempGz += Mag.s16Z;
    delay(5);
  }
  gstMagOffset.s16X = s32TempGx >> 5;
  gstMagOffset.s16Y = s32TempGy >> 5;
  gstMagOffset.s16Z = s32TempGz >> 5;
//   QMI8658_printf("\r\n Gyroscope: X: %d     Y: %d     Z: %d \r\n",gstGyroOffset.s16X, gstGyroOffset.s16Y, gstGyroOffset.s16Z);
  return;
}
