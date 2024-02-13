#ifndef _IMU_H_
#define _IMU_H_

#include "IMU_AK09918.h"
#include "IMU_QMI8658.h"
#include <stdio.h>
#include <math.h>

typedef struct imu_st_angles_data_tag
{
  float fYaw;
  float fPitch;
  float fRoll;
}IMU_ST_ANGLES_DATA;

typedef struct imu_q_data_tag
{
  float a;
  float b;
  float c;
  float d;
}IMU_Q_DATA;

void imuInit();
void imuDataGet(IMU_ST_ANGLES_DATA *pstAngles, 
                IMU_ST_SENSOR_DATA *pstGyroRawData,
                IMU_ST_SENSOR_DATA *pstAccelRawData,
                IMU_ST_SENSOR_DATA *pstMagnRawData,
                IMU_Q_DATA *qRawData); 

#endif
