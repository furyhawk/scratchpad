#include "lps22hb.h"
#include "imu.h"
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

IMU_EN_SENSOR_TYPE enMotionSensorType;
IMU_ST_ANGLES_DATA stAngles;
IMU_ST_SENSOR_DATA stGyroRawData;
IMU_ST_SENSOR_DATA stAccelRawData;
IMU_ST_SENSOR_DATA stMagnRawData;
float PRESS_DATA=0;
float TEMP_DATA=0;
uint8_t u8Buf[3];

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  delay(5000);
  
	imuInit(&enMotionSensorType);
 
	if(IMU_EN_SENSOR_TYPE_MPU9250 == enMotionSensorType)
	{
		Serial.printf("Motion sersor is MPU9250\n" );
	}
	else
	{
		Serial.printf("Motion sersor NULL\n");
	}
	// if (!LPS22HB_INIT()){
	// 	Serial.printf("LPS22HB Init Error\n");
	// 	exit(1);
	// }

}

void loop() {
  // put your main code here, to run repeatedly:
  // LPS22HB_START_ONESHOT();
  // if((I2C_readByte(LPS_STATUS)&0x01)==0x01)   //a new pressure data is generated
  // {
  //     u8Buf[0]=I2C_readByte(LPS_PRESS_OUT_XL);
  //     u8Buf[1]=I2C_readByte(LPS_PRESS_OUT_L);
  //     u8Buf[2]=I2C_readByte(LPS_PRESS_OUT_H);
  //     PRESS_DATA=(float)((u8Buf[2]<<16)+(u8Buf[1]<<8)+u8Buf[0])/4096.0f;
  // }
  // if((I2C_readByte(LPS_STATUS)&0x02)==0x02)   // a new pressure data is generated
  // {
  //     u8Buf[0]=I2C_readByte(LPS_TEMP_OUT_L);
  //     u8Buf[1]=I2C_readByte(LPS_TEMP_OUT_H);
  //     TEMP_DATA=(float)((u8Buf[1]<<8)+u8Buf[0])/100.0f;
  // }
        
  imuDataGet( &stAngles, &stGyroRawData, &stAccelRawData, &stMagnRawData);
  Serial.printf("\r\n /-------------------------------------------------------------/ \r\n");
  Serial.printf("\r\n Roll: %.2f     Pitch: %.2f     Yaw: %.2f \r\n",stAngles.fRoll, stAngles.fPitch, stAngles.fYaw);
  // Serial.printf("Pressure = %6.2f hPa , Temperature = %6.2f C\r\n", PRESS_DATA, TEMP_DATA);
  //printf("\r\n Acceleration: X: %d     Y: %d     Z: %d \r\n",stAccelRawData.s16X, stAccelRawData.s16Y, stAccelRawData.s16Z);
  //printf("\r\n Gyroscope: X: %d     Y: %d     Z: %d \r\n",stGyroRawData.s16X, stGyroRawData.s16Y, stGyroRawData.s16Z);
  Serial.printf("\r\n Magnetic: X: %d     Y: %d     Z: %d \r\n",stMagnRawData.s16X, stMagnRawData.s16Y, stMagnRawData.s16Z);
}
