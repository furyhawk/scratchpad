#ifndef SDCARD_BSP_H
#define SDCARD_BSP_H
#include "driver/sdmmc_host.h"


typedef struct
{
  float sdcard_size;
}sdcard_bsp_t;

extern sdcard_bsp_t user_sdcard_bsp;
extern EventGroupHandle_t sdcard_even_;

#ifdef __cplusplus
extern "C" {
#endif


void _sdcard_init(void);
esp_err_t sdcard_file_write(const char *path, const char *data);
esp_err_t sdcard_file_read(const char *path, char *buffer, size_t *out_len);

#ifdef __cplusplus
}
#endif

#endif