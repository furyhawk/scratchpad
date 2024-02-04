#ifndef _IMU_H_
#define _IMU_H_

#include "AK09918.h"
#include "QMI8658.h"
#include "stdio.h"
#include <math.h>

typedef struct imu_st_angles_data_tag
{
  float fYaw;
  float fPitch;
  float fRoll;
}IMU_ST_ANGLES_DATA;

void imuInit(void);
void imuDataGet(IMU_ST_ANGLES_DATA *pstAngles, 
                IMU_ST_SENSOR_DATA *pstGyroRawData,
                IMU_ST_SENSOR_DATA *pstAccelRawData,
                IMU_ST_SENSOR_DATA *pstMagnRawData); 

#endif
