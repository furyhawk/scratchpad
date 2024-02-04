#ifndef _AK09918_H_
#define _AK09918_H_

#include <stdint.h>
#include <stdlib.h> //itoa()
#include "stdio.h"
#include "gpio.h"
#include "usart.h"
#include "i2c.h"

//i2c address
#define AK09918_I2C_ADDR    0x0c << 1     // I2C address (Can't be changed)
#define AK09918_WIA1        0x00    // Company ID
#define AK09918_WIA2        0x01    // Device ID
#define AK09918_RSV1        0x02    // Reserved 1
#define AK09918_RSV2        0x03    // Reserved 2
#define AK09918_ST1         0x10    // DataStatus 1
#define AK09918_HXL         0x11    // X-axis data 
#define AK09918_HXH         0x12
#define AK09918_HYL         0x13    // Y-axis data
#define AK09918_HYH         0x14
#define AK09918_HZL         0x15    // Z-axis data
#define AK09918_HZH         0x16
#define AK09918_TMPS        0x17    // Dummy
#define AK09918_ST2         0x18    // Datastatus 2
#define AK09918_CNTL1       0x30    // Dummy
#define AK09918_CNTL2       0x31    // Control settings
#define AK09918_CNTL3       0x32    // Control settings

#define AK09918_SRST_BIT    0x01    // Soft Reset
#define AK09918_HOFL_BIT    0x08    // Sensor Over Flow
#define AK09918_DOR_BIT     0x02    // Data Over Run
#define AK09918_DRDY_BIT    0x01    // Data Ready


#define AK09918_POWER_DOWN  0x00
#define AK09918_NORMAL  0x01
#define AK09918_CONTINUOUS_10HZ  0x02
#define AK09918_CONTINUOUS_20HZ  0x04
#define AK09918_CONTINUOUS_50HZ  0x06
#define AK09918_CONTINUOUS_100HZ  0x08
#define AK09918_SELF_TEST  0x10 // ignored by switchMode() and initialize(), call selfTest() to use this mode

typedef struct AK09918_data_tag
{
  uint8_t u8Index;
  int16_t s16AvgBuffer[8];
}AK09918_DATA;

typedef struct imu_st_sensor_data_tag
{
  short int s16X;
  short int s16Y;
  short int s16Z;
}IMU_ST_SENSOR_DATA;

void AK09918_init(uint8_t mode);
void AK09918_Read_data(IMU_ST_SENSOR_DATA *pstMagnRawData);


#endif
