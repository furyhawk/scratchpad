#ifndef __DRIVER_ADC_H
#define __DRIVER_ADC_H
#include <stdio.h>
#include "RGBMatrixConfig.h"
#include "Arduino.h"
#if defined CONFIG_SUPPORT_PICO

#define wait 0

#elif defined CONFIG_SUPPORT_ESP32S2
#define ADC0 6

#endif

uint16_t get_adc_value(void);


#endif

