#ifndef BLE_SCAN_BSP_H
#define BLE_SCAN_BSP_H

#include "freertos/FreeRTOS.h"


#ifdef __cplusplus
extern "C" {
#endif

void ble_scan_prepare(void);  //初始化之前的释放内存
void ble_stack_init(void);    //ble初始化
void ble_scan_start(void);    //ble扫描开始
void ble_stack_deinit(void);  //ble反初始化 

extern EventGroupHandle_t ble_even_;
extern int ble_scan_apNum;


#ifdef __cplusplus
}
#endif

#endif
