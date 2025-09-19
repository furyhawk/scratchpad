#ifndef USER_AUDIO_BSP_H
#define USER_AUDIO_BSP_H




#ifdef __cplusplus
extern "C" {
#endif

uint8_t *i2s_get_handle(uint32_t *len);
void user_audio_bsp_init(void);
void i2s_music(void *args);
void i2s_echo(void *arg);
void audio_playback_set_vol(uint8_t vol);
void example_i2s_audio_Test(void *arg);

int audio_playback_read(void *data_ptr,uint32_t len);

int audio_playback_write(void *data_ptr,uint32_t len);
void audio_play_init(void);

#ifdef __cplusplus
}
#endif

#endif // !MY_ADF_BSP_H
