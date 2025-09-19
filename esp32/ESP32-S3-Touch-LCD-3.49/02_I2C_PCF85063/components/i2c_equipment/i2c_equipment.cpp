#include <stdio.h>
#include "i2c_equipment.h"
#include "i2c_bsp.h"
#include "user_config.h"
#include "SensorPCF85063.hpp"
#include "SensorQMI8658.hpp"
SensorPCF85063 rtc;
SensorQMI8658 qmi;

IMUdata acc;
IMUdata gyr;

static uint32_t hal_callback(SensorCommCustomHal::Operation op, void *param1, void *param2)
{
  switch (op) 
  {
    // Set GPIO mode
    case SensorCommCustomHal::OP_PINMODE: {
        uint8_t pin = reinterpret_cast<uintptr_t>(param1);
        uint8_t mode = reinterpret_cast<uintptr_t>(param2);
        gpio_config_t config;
        memset(&config, 0, sizeof(config));
        config.pin_bit_mask = 1ULL << pin;
        switch (mode) {
        case INPUT:
            config.mode = GPIO_MODE_INPUT;
            break;
        case OUTPUT:
            config.mode = GPIO_MODE_OUTPUT;
            break;
        }
        config.pull_up_en = GPIO_PULLUP_DISABLE;
        config.pull_down_en = GPIO_PULLDOWN_DISABLE;
        config.intr_type = GPIO_INTR_DISABLE;
        ESP_ERROR_CHECK(gpio_config(&config));
    }
    break;
    // Set GPIO level
    case SensorCommCustomHal::OP_DIGITALWRITE: {
        uint8_t pin = reinterpret_cast<uintptr_t>(param1);
        uint8_t level = reinterpret_cast<uintptr_t>(param2);
        gpio_set_level((gpio_num_t )pin, level);
    }
    break;
    // Read GPIO level
    case SensorCommCustomHal::OP_DIGITALREAD: {
        uint8_t pin = reinterpret_cast<uintptr_t>(param1);
        return gpio_get_level((gpio_num_t)pin);
    }
    break;
    // Get the current running milliseconds
    case SensorCommCustomHal::OP_MILLIS:
        return (uint32_t) (esp_timer_get_time() / 1000LL);

    // Delay in milliseconds
    case SensorCommCustomHal::OP_DELAY: {
        if (param1) {
            uint32_t ms = reinterpret_cast<uintptr_t>(param1);
            vTaskDelay(pdMS_TO_TICKS(ms));
            //esp_rom_delay_us((ms % portTICK_PERIOD_MS) * 1000UL);
            //ESP_LOGE("MS","%ld",ms);
        }
    }
    break;
    // Delay in microseconds
    case SensorCommCustomHal::OP_DELAYMICROSECONDS: {
        uint32_t us = reinterpret_cast<uintptr_t>(param1);
        esp_rom_delay_us(us);
    }
    break;
    default:
        break;
  }
  return 0;
}

bool i2c_dev_Callback(uint8_t addr, uint8_t reg, uint8_t *buf, size_t len, bool writeReg, bool isWrite)
{
    uint8_t ret;
    int areg = reg;
    i2c_master_dev_handle_t i2c_dev_handle = NULL;
    if(RTC_PCF85063_ADDR==addr)
    i2c_dev_handle = rtc_dev_handle;
    else if(IMU_QMI8658_ADDR==addr)
    i2c_dev_handle = imu_dev_handle;
    if(isWrite) // 写寄存器
    {
        if(writeReg)
        {
            ret = i2c_writr_buff(i2c_dev_handle,areg,buf,len);
        }
        else
        {
            ret = i2c_writr_buff(i2c_dev_handle,-1,buf,len);
        }
    }
    else
    {
      	if(writeReg)
      	{
      	  	ret = i2c_read_buff(i2c_dev_handle,areg,buf,len);
      	}
      	else
      	{
      	    ret = i2c_read_buff(i2c_dev_handle,-1,buf,len);
      	}
    }
    return (ret == ESP_OK) ? true : false;
}

void i2c_rtc_setup(void)
{
  	if(rtc.begin(i2c_dev_Callback))
  	{
  	  	ESP_LOGI("rtc","rtc_will");
  	}
}
void i2c_dev_init(void)
{
  	//i2c_mux = xSemaphoreCreateMutex();
  	//assert(i2c_mux);
}
void i2c_qmi_setup(void)
{
  	if(qmi.begin(i2c_dev_Callback,hal_callback,IMU_QMI8658_ADDR))
  	{
  	  	ESP_LOGI("qmi","qmi_will");
  	}
  	ESP_LOGI("qmi","qmi_ID:%02x",qmi.getChipID());
  	if (qmi.selfTestAccel()) 
  	{
  	  	ESP_LOGI("qmi","Accelerometer self-test successful");
  	}
  	else 
  	{
  	  	ESP_LOGE("qmi","Accelerometer self-test failed!");
  	}
  	if (qmi.selfTestGyro())
  	{
  	  	ESP_LOGI("qmi","Gyroscope self-test successful");
  	}
  	else
  	{
  	  	ESP_LOGE("qmi","Gyroscope self-test failed!");
  	}
  	qmi.configAccelerometer(SensorQMI8658::ACC_RANGE_4G,SensorQMI8658::ACC_ODR_1000Hz,SensorQMI8658::LPF_MODE_0);
  	qmi.configGyroscope(SensorQMI8658::GYR_RANGE_64DPS,SensorQMI8658::GYR_ODR_896_8Hz,SensorQMI8658::LPF_MODE_3);
  	qmi.enableGyroscope();
  	qmi.enableAccelerometer();

  	// Print register configuration information
  	qmi.dumpCtrlRegister();
}
/*
uint16_t year = 2023;
uint8_t month = 9;
uint8_t day = 7;
uint8_t hour = 11;
uint8_t minute = 24;
uint8_t second = 30;
*/
void i2c_rtc_setTime(uint16_t year,uint8_t month,uint8_t day,uint8_t hour,uint8_t minute,uint8_t second)
{
  	rtc.setDateTime(year, month, day, hour, minute, second);
}

void i2c_rtc_loop_task(void *arg)
{
  	for(;;)
  	{
  	  	RTC_DateTime datetime = rtc.getDateTime();
  	  	printf("%d/%d/%d %d:%d:%d \n",datetime.getYear(),datetime.getMonth(),datetime.getDay(),datetime.getHour(),datetime.getMinute(),datetime.getSecond());  
  	  	vTaskDelay(pdMS_TO_TICKS(1000));
  	}
}


RtcDateTime_t i2c_rtc_get(void)
{
  	RtcDateTime_t time;
  	RTC_DateTime datetime = rtc.getDateTime();
  	time.year = datetime.getYear();
  	time.month = datetime.getMonth();
  	time.day = datetime.getDay();
  	time.hour = datetime.getHour();
  	time.minute = datetime.getMinute();
  	time.second = datetime.getSecond();
  	time.week = datetime.getWeek();
  	return time;
}


void i2c_qmi_task(void *arg)
{
  	for(;;)
  	{
  	  	if (qmi.getDataReady())
  	  	{
  	  	  if (qmi.getAccelerometer(acc.x, acc.y, acc.z))
  	  	  {
  	  	    	// Print to serial plotter
  	  	    	printf("ACCEL.x:%.2f,ACCEL.y:%.2f,ACCEL.z:%.2f Unit:g\n",acc.x,acc.y,acc.z);
  	  	  }
  	  	  if (qmi.getGyroscope(gyr.x, gyr.y, gyr.z))
  	  	  {
  	  	    	// Print to serial plotter
  	  	    	printf("GYRO.x:%.2f,GYRO.y:%.2f,GYRO.z:%.2f Unit:degrees/sec\n",gyr.x,gyr.y,gyr.z);
  	  	    	// Serial.print(" GYRO.x:"); Serial.print(gyr.x); Serial.println(" degrees/sec");
  	  	    	// Serial.print(",GYRO.y:"); Serial.print(gyr.y); Serial.println(" degrees/sec");
  	  	    	// Serial.print(",GYRO.z:"); Serial.print(gyr.z); Serial.println(" degrees/sec");
			
  	  	  }
  	  	  	printf("Temperature: %.2f Unit:degrees C\n",qmi.getTemperature_C());
  	  	}
  	  	vTaskDelay(pdMS_TO_TICKS(100));
  	}
}

ImuDate_t i2c_imu_get(void)
{
  	ImuDate_t imuData;
  	memset(&imuData,0,sizeof(ImuDate_t));
  	if (qmi.getDataReady())
  	{
  	  	if (qmi.getAccelerometer(acc.x, acc.y, acc.z)) //g
  	  	{
  	  	  	imuData.accx = acc.x;
  	  	  	imuData.accy = acc.y;
  	  	  	imuData.accz = acc.z;
  	  	}
  	  	if (qmi.getGyroscope(gyr.x, gyr.y, gyr.z)) //dps
  	  	{
  	  	  	imuData.gyrox = gyr.x;
  	  	  	imuData.gyroy = gyr.y;
  	  	  	imuData.gyroz = gyr.z;
  	  	}
  	}
  	return imuData;
}