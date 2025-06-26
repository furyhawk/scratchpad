#ifndef __HAL_GPIO_KEY_H
#define __HAL_GPIO_KEY_H
#define     KEY0_MENU            0
#define     KEY1_DOWN            1
#define     KEY2_UP              2
void HAL_GPIOKeyInit(void);
void HAL_whichKeyPress(void);

#endif
