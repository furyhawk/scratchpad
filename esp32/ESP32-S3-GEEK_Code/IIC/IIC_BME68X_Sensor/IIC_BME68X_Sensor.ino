/**
 * Copyright (C) 2021 Bosch Sensortec GmbH
 *
 * SPDX-License-Identifier: BSD-3-Clause
 * 
 */

#include "Arduino.h"
#include "bme68xLibrary.h"

#ifndef PIN_CS
#define PIN_CS 15
#endif

#ifndef ADD_I2C
#define ADD_I2C 0x77
#endif

#ifndef PIN_SDA
#define PIN_SDA 16
#endif

#ifndef PIN_SCL
#define PIN_SCL 17
#endif

#ifndef PIN_BL
#define PIN_BL 7
#endif

Bme68x bme;

/**
 * @brief Initializes the sensor and hardware settings
 */
void setup(void)
{
  analogWrite(PIN_BL,0);
  Wire.begin(PIN_SDA, PIN_SCL);     //I2C mode
	//SPI.begin();    //SPI mode
	Serial.begin(115200);
  delay(100);
	Serial.println(PIN_SDA);
  Serial.println(PIN_SCL);

	while (!Serial)
		delay(10);
		
	/* initializes the sensor based on SPI library */
	//bme.begin(PIN_CS, SPI);     //SPI mode
  bme.begin(ADD_I2C, Wire);     //I2C mode

	if(bme.checkStatus())
	{
		if (bme.checkStatus() == BME68X_ERROR)
		{
			Serial.println("Sensor error:" + bme.statusString());
			return;
		}
		else if (bme.checkStatus() == BME68X_WARNING)
		{
			Serial.println("Sensor Warning:" + bme.statusString());
		}
	}
	
	/* Set the default configuration for temperature, pressure and humidity */
	bme.setTPH();

	/* Set the heater configuration to 300 deg C for 100ms for Forced mode */
	bme.setHeaterProf(300, 100);

	Serial.println("TimeStamp(ms), Temperature(deg C), Pressure(Pa), Humidity(%), Gas resistance(ohm), Status");
}

void loop(void)
{
	bme68xData data;

	bme.setOpMode(BME68X_FORCED_MODE);
	delay(500+bme.getMeasDur()/200);

	if (bme.fetchData())
	{
		bme.getData(data);
		Serial.print(String(millis()) + ", ");
		Serial.print(String(data.temperature) + ", ");
		Serial.print(String(data.pressure) + ", ");
		Serial.print(String(data.humidity) + ", ");
		Serial.print(String(data.gas_resistance) + ", ");
		Serial.println(data.status, HEX);
	}
}
