#include "driver_adc.h"

void adc_Init(void)
{
#if defined CONFIG_SUPPORT_PICO
    stdio_init_all();
    adc_init();
    adc_gpio_init(Light_sensor);
    adc_select_input(0);
#endif

}


uint16_t get_adc_value(void)
{
	uint16_t read_raw;
#if defined CONFIG_SUPPORT_PICO
    read_raw = adc_read();
    return (read_raw - 700);
#endif
}