#include "driver_buzzer.h"


void buzzerInit(void)
{
#ifdef CONFIG_SUPPORT_PICO
    gpio_init(BUZZER);
    gpio_set_dir(BUZZER,GPIO_OUT);
    BUZZEROFF();
#elif CONFIG_SUPPORT_ESP32S2
    gpio_reset_pin(BUZZER);
    gpio_set_direction(BUZZER,GPIO_MODE_OUTPUT);
    BUZZEROFF();
#endif

}

