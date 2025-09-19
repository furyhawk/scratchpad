#ifndef USER_APP_H
#define USER_APP_H

#include "freertos/FreeRTOS.h"
typedef struct 
{
  int16_t x;
  int16_t y;
}app_touch_t;

extern QueueHandle_t app_touch_data_queue;

#ifdef __cplusplus
extern "C" {
#endif


void user_app_init(void);


#ifdef __cplusplus
}
#endif

#endif