#include "AK09918.h"
uint8_t buf[8];
uint8_t AK09918_dev;
void AK09918_CalAvgValue(uint8_t *pIndex, int16_t *pAvgBuffer, int16_t InVal, int32_t *pOutVal);
void AK09918_Read_8_Byte(uint8_t reg)
{
    HAL_I2C_Mem_Read(&hi2c1, AK09918_I2C_ADDR, reg, I2C_MEMADD_SIZE_8BIT, buf, 8, 0x10);
}

void AK09918_I2C_Write(uint8_t reg, uint8_t Value)
{
    uint8_t Buf[1] = {0};
		Buf[0] = Value;
		HAL_I2C_Mem_Write(&hi2c1, AK09918_I2C_ADDR, reg, I2C_MEMADD_SIZE_8BIT, Buf, 1, 0x10);
}

uint8_t AK09918_I2C_ReadByte(uint8_t reg)
{
    uint8_t Buf[1]={0};
		HAL_I2C_Mem_Read(&hi2c1, AK09918_I2C_ADDR, reg, I2C_MEMADD_SIZE_8BIT, Buf, 1, 0x10);
		return Buf[0];
}
void AK09918_init(uint8_t mode)
{   

    if(AK09918_I2C_ReadByte(AK09918_WIA2) != 0x0C)
        printf("Fail to read\r\n");
    else{
        printf("Success to read\r\n");
        AK09918_I2C_Write(AK09918_CNTL2,mode);
    }
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

    if (counter != 0)
        {
            AK09918_Read_8_Byte(AK09918_HXL);
            s16Buf[0] = ((short int)buf[1] << 8) | buf[0];
            s16Buf[1] = ((short int)buf[3] << 8) | buf[2];
            s16Buf[2] = ((short int)buf[5] << 8) | buf[4];
        }
    for (int i = 0; i < 3; i++)
        AK09918_CalAvgValue(&sstAvgBuf[i].u8Index, sstAvgBuf[i].s16AvgBuffer, s16Buf[i], s32OutBuf + i);
    
    pstMagnRawData->s16X = s32OutBuf[0];
    pstMagnRawData->s16Y = s32OutBuf[1];
    pstMagnRawData->s16Z = s32OutBuf[2];
    // printf("Magnetic:       X= %d ,      Y  = %d ,      Z  = %d\r\n\n",s32OutBuf[0],s32OutBuf[1],s32OutBuf[2]);
    
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

