#include "IMU.h"

int main()
{
	IMU_ST_ANGLES_DATA stAngles;
	IMU_ST_SENSOR_DATA stGyroRawData;
	IMU_ST_SENSOR_DATA stAccelRawData;
	IMU_ST_SENSOR_DATA stMagnRawData;

	float temp;
	imuInit();
	
	while(1)
	{
		imuDataGet( &stAngles, &stGyroRawData, &stAccelRawData, &stMagnRawData);
		temp = QMI8658_readTemp();
		printf("\r\n /-------------------------------------------------------------/ \r\n");
		printf("\r\n Roll: %.2f     Pitch: %.2f     Yaw: %.2f \r\n",stAngles.fRoll, stAngles.fPitch, stAngles.fYaw);
		printf("\r\n Acceleration: X: %d     Y: %d     Z: %d \r\n",stAccelRawData.s16X, stAccelRawData.s16Y, stAccelRawData.s16Z);
		printf("\r\n Gyroscope: X: %d     Y: %d     Z: %d \r\n",stGyroRawData.s16X, stGyroRawData.s16Y, stGyroRawData.s16Z);
		printf("\r\n Magnetic: X: %d     Y: %d     Z: %d \r\n",stMagnRawData.s16X, stMagnRawData.s16Y, stMagnRawData.s16Z);
		printf("\r\n QMITemp:%.2f C\r\n",temp);
		delay(100);
	} 
  
  return 0;
}