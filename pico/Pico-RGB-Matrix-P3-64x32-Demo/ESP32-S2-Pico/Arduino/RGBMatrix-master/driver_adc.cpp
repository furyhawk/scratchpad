#include "driver_adc.h"

uint16_t get_adc_value(void)
{
	uint16_t read_raw;
	read_raw = analogRead(ADC0);
    
	// read_raw = (read_raw*1100)/4096;
	return read_raw;
}