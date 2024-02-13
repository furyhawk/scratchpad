#include "IMU.h"

void imuAHRSupdate(float gx, float gy, float gz, float ax, float ay, float az, float mx, float my, float mz);
float invSqrt(float x);

/******************************************************************************
 * IMU module                                                                 *
 ******************************************************************************/
#define Kp 4.50f   // proportional gain governs rate of convergence to accelerometer/magnetometer
#define Ki 1.0f    // integral gain governs rate of convergence of gyroscope biases

float angles[3];
float q0, q1, q2, q3;

// #define S_SCL   33
// #define S_SDA   32

void imuInit()
{
    // Wire.begin(S_SDA, S_SCL);
    // Serial.begin(115200);
   
    QMI8658_init();
    AK09918_init(AK09918_CONTINUOUS_50HZ);

    q0 = 1.0f;  
    q1 = 0.0f;
    q2 = 0.0f;
    q3 = 0.0f;

  return;
}

void imuDataGet(IMU_ST_ANGLES_DATA *pstAngles, 
                IMU_ST_SENSOR_DATA *pstGyroRawData,
                IMU_ST_SENSOR_DATA *pstAccelRawData,
                IMU_ST_SENSOR_DATA *pstMagnRawData,
                IMU_Q_DATA *qRawData)
{
  float MotionVal[9];
  short int acc[3], gyro[3];
  unsigned int tim_count=0;
  IMU_ST_SENSOR_DATA stMagnRawData;

  QMI8658_read_acc_xyz(acc);
  QMI8658_read_gyro_xyz(gyro);

  AK09918_Read_data(&stMagnRawData);

  MotionVal[0]=gyro[0]/32.8;
  MotionVal[1]=gyro[1]/32.8;
  MotionVal[2]=gyro[2]/32.8;
  MotionVal[3]=acc[0];
  MotionVal[4]=acc[1];
  MotionVal[5]=acc[2];
  MotionVal[6]=stMagnRawData.s16X;
  MotionVal[7]=stMagnRawData.s16Y;
  MotionVal[8]=stMagnRawData.s16Z;
  imuAHRSupdate((float)MotionVal[0] * 0.0175, (float)MotionVal[1] * 0.0175, (float)MotionVal[2] * 0.0175,
                (float)MotionVal[3], (float)MotionVal[4], (float)MotionVal[5], 
                (float)MotionVal[6], (float)MotionVal[7], MotionVal[8]);

  qRawData->a = q0;
  qRawData->b = q1;
  qRawData->c = q2;
  qRawData->d = q3;

  pstAngles->fPitch = asin(-2 * q1 * q3 + 2 * q0* q2)* 57.3; // pitch
  pstAngles->fRoll = atan2(2 * q2 * q3 + 2 * q0 * q1, -2 * q1 * q1 - 2 * q2* q2 + 1)* 57.3; // roll
  pstAngles->fYaw = atan2(-2 * q1 * q2 - 2 * q0 * q3, 2 * q2 * q2 + 2 * q3 * q3 - 1) * 57.3; 

  pstGyroRawData->s16X = gyro[0];
  pstGyroRawData->s16Y = gyro[1];
  pstGyroRawData->s16Z = gyro[2];

  pstAccelRawData->s16X = acc[0];
  pstAccelRawData->s16Y = acc[1];
  pstAccelRawData->s16Z = acc[2];

  pstMagnRawData->s16X = stMagnRawData.s16X;
  pstMagnRawData->s16Y = stMagnRawData.s16Y;
  pstMagnRawData->s16Z = stMagnRawData.s16Z;  

  return;  
}

void imuAHRSupdate(float gx, float gy, float gz, float ax, float ay, float az, float mx, float my, float mz) 
{
  float norm;
  float hx, hy, hz, bx, bz;
  float vx, vy, vz, wx, wy, wz;
  float exInt = 0.0, eyInt = 0.0, ezInt = 0.0;
  float ex, ey, ez, halfT = 0.024f;

  float q0q0 = q0 * q0;
  float q0q1 = q0 * q1;
  float q0q2 = q0 * q2;
  float q0q3 = q0 * q3;
  float q1q1 = q1 * q1;
  float q1q2 = q1 * q2;
  float q1q3 = q1 * q3;
  float q2q2 = q2 * q2;   
  float q2q3 = q2 * q3;
  float q3q3 = q3 * q3;          

  norm = invSqrt(ax * ax + ay * ay + az * az);       
  ax = ax * norm;
  ay = ay * norm;
  az = az * norm;

  norm = invSqrt(mx * mx + my * my + mz * mz);          
  mx = mx * norm;
  my = my * norm;
  mz = mz * norm;

  // compute reference direction of flux
  hx = 2 * mx * (0.5f - q2q2 - q3q3) + 2 * my * (q1q2 - q0q3) + 2 * mz * (q1q3 + q0q2);
  hy = 2 * mx * (q1q2 + q0q3) + 2 * my * (0.5f - q1q1 - q3q3) + 2 * mz * (q2q3 - q0q1);
  hz = 2 * mx * (q1q3 - q0q2) + 2 * my * (q2q3 + q0q1) + 2 * mz * (0.5f - q1q1 - q2q2);         
  bx = sqrt((hx * hx) + (hy * hy));
  bz = hz;     

  // estimated direction of gravity and flux (v and w)
  vx = 2 * (q1q3 - q0q2);
  vy = 2 * (q0q1 + q2q3);
  vz = q0q0 - q1q1 - q2q2 + q3q3;
  wx = 2 * bx * (0.5 - q2q2 - q3q3) + 2 * bz * (q1q3 - q0q2);
  wy = 2 * bx * (q1q2 - q0q3) + 2 * bz * (q0q1 + q2q3);
  wz = 2 * bx * (q0q2 + q1q3) + 2 * bz * (0.5 - q1q1 - q2q2);  

  // error is sum of cross product between reference direction of fields and direction measured by sensors
  ex = (ay * vz - az * vy) + (my * wz - mz * wy);
  ey = (az * vx - ax * vz) + (mz * wx - mx * wz);
  ez = (ax * vy - ay * vx) + (mx * wy - my * wx);

  if(ex != 0.0f && ey != 0.0f && ez != 0.0f)
  {
    exInt = exInt + ex * Ki * halfT;
    eyInt = eyInt + ey * Ki * halfT;  
    ezInt = ezInt + ez * Ki * halfT;

    gx = gx + Kp * ex + exInt;
    gy = gy + Kp * ey + eyInt;
    gz = gz + Kp * ez + ezInt;
  }

  q0 = q0 + (-q1 * gx - q2 * gy - q3 * gz) * halfT;
  q1 = q1 + (q0 * gx + q2 * gz - q3 * gy) * halfT;
  q2 = q2 + (q0 * gy - q1 * gz + q3 * gx) * halfT;
  q3 = q3 + (q0 * gz + q1 * gy - q2 * gx) * halfT;  

  norm = invSqrt(q0 * q0 + q1 * q1 + q2 * q2 + q3 * q3);
  q0 = q0 * norm;
  q1 = q1 * norm;
  q2 = q2 * norm;
  q3 = q3 * norm;
}

float invSqrt(float x) 
{
  float halfx = 0.5f * x;
  float y = x;
  
  long i = *(long*)&y;                //get bits for floating value
  i = 0x5f3759df - (i >> 1);          //gives initial guss you
  y = *(float*)&i;                    //convert bits back to float
  y = y * (1.5f - (halfx * y * y));   //newtop step, repeating increases accuracy
  
  return y;
}
