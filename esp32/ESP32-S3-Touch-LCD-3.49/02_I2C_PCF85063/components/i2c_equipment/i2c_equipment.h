#ifndef I2C_EQUIPMENT_H
#define I2C_EQUIPMENT_H


typedef struct 
{
  uint16_t year;
  uint8_t month;
  uint8_t day;
  uint8_t hour;
  uint8_t minute;
  uint8_t second;
  uint8_t week;
}RtcDateTime_t;

typedef struct 
{
  float accx;
  float accy;
  float accz;
  float gyrox;
  float gyroy;
  float gyroz;
}ImuDate_t;



void i2c_rtc_setup(void);
void i2c_rtc_setTime(uint16_t year,uint8_t month,uint8_t day,uint8_t hour,uint8_t minute,uint8_t second);
void i2c_rtc_loop_task(void *arg);
void i2c_qmi_setup(void);
void i2c_dev_init(void);
void i2c_qmi_task(void *arg);
RtcDateTime_t i2c_rtc_get(void);
ImuDate_t i2c_imu_get(void);
#endif 
