#include "src/ExternLib/button/button_bsp.h"
#include "i2c_bsp.h"
#include "codec_bsp.h"
#include "led_bsp.h"
#include "power_bsp.h"

I2cMasterBus I2cbus(48, 47, 0);
CodecPort *codecport = NULL;
static uint8_t *audio_ptr = NULL;
static bool is_Music = true;
EventGroupHandle_t CodecGroups;

/*
Instructions:
Short press BOOT: Play recorded audio
Double press BOOT: Start recording
Short press KEY: Interrupt music playback
Double press KEY: Play a piece of music
*/

void BOOT_LoopTask(void *arg) {
  for (;;) {
    EventBits_t even = xEventGroupWaitBits(BootButtonGroups, (0x01 | 0x02), pdTRUE, pdFALSE, pdMS_TO_TICKS(2000));
    if (even & 0x01) {
      xEventGroupSetBits(CodecGroups, 0x02);
    } else if (even & 0x02) {
      xEventGroupSetBits(CodecGroups, 0x01);
    }
  }
}

void Codec_LoopTask(void *arg) {
  bool is_eco = 0;
  for (;;) {
    EventBits_t even = xEventGroupWaitBits(CodecGroups, (0x01 | 0x02 | 0x04), pdTRUE, pdFALSE, pdMS_TO_TICKS(2 * 1000));
    if (even & 0x01) {
      printf("正在录音/Recording...\n");
      xEventGroupSetBits(Led_Groups, (0x01UL << 5));
      codecport->CodecPort_EchoRead(audio_ptr, 192 * 1000);
      printf("录音完成/Rec Done\n");
      xEventGroupClearBits(Led_Groups, (0x01UL << 5));
      is_eco = 1;
    } else if (even & 0x02) {
      if (1 == is_eco) {
        is_eco = 0;
        printf("正在播放/Playing...\n");
        xEventGroupSetBits(Led_Groups, (0x01UL << 2));
        codecport->CodecPort_PlayWrite(audio_ptr, 192 * 1000);
        printf("播放完成/Play Done\n");
        xEventGroupClearBits(Led_Groups, (0x01UL << 2));
      }
    } else if (even & 0x04) {
      printf("正在播放音乐/Play Music\n");
      xEventGroupSetBits(Led_Groups, (0x01UL << 2));
      codecport->CodecPort_SetSpeakerVol(90);
      uint32_t bytes_sizt;
      size_t bytes_write = 0;
      uint8_t *data_ptr = codecport->CodecPort_GetPcmData(&bytes_sizt);
      while (bytes_write < bytes_sizt) {
        codecport->CodecPort_PlayWrite(data_ptr, 256);
        data_ptr += 256;
        bytes_write += 256;
        if (!is_Music)
          break;
      }
      codecport->CodecPort_SetSpeakerVol(100);
      printf("播放完成/Play Done\n");
      xEventGroupClearBits(Led_Groups, (0x01UL << 2));
    } else {
      Led_SetLevel(LED_PIN_Red, LED_ON);
      Led_SetLevel(LED_PIN_Green, LED_ON);
    }
  }
}

void KEY_LoopTask(void *arg) {
  for (;;) {
    EventBits_t even = xEventGroupWaitBits(GP4ButtonGroups, (0x01 | 0x02 | 0x04), pdTRUE, pdFALSE, pdMS_TO_TICKS(2000));
    if (even & 0x01) {
      is_Music = false;
    } else if (even & 0x02) {
      is_Music = true;
      xEventGroupSetBits(CodecGroups, 0x04);
    }
  }
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  audio_ptr = (uint8_t *)heap_caps_malloc(288 * 1000 * sizeof(uint8_t), MALLOC_CAP_SPIRAM);
  assert(audio_ptr);
  CodecGroups = xEventGroupCreate();
  Custom_PmicPortInit(&I2cbus, 0x34);
  Custom_ButtonInit();
  Led_init();
  codecport = new CodecPort(I2cbus, "USER_CODEC_BOARD");
  codecport->CodecPort_SetInfo("es8311 & es7210", 1, 16000, 2, 16);
  codecport->CodecPort_SetSpeakerVol(100);
  codecport->CodecPort_SetMicGain(35);

  Led_SetLevel(LED_PIN_Red, LED_ON);
  Led_SetLevel(LED_PIN_Green, LED_ON);

  xTaskCreatePinnedToCore(BOOT_LoopTask, "BOOT_LoopTask", 4 * 1024, NULL, 2, NULL, 1);
  xTaskCreatePinnedToCore(KEY_LoopTask, "KEY_LoopTask", 4 * 1024, NULL, 2, NULL, 1);
  xTaskCreatePinnedToCore(Codec_LoopTask, "Codec_LoopTask", 4 * 1024, NULL, 4, NULL, 1);
  xTaskCreatePinnedToCore(Led_RegLoopTask, "Led_RegLoopTask", 4 * 1024, NULL, 4, NULL, 1);
  xTaskCreatePinnedToCore(Led_GreenLoopTask, "Led_GreenLoopTask", 4 * 1024, NULL, 4, NULL, 1);
}

void loop() {
}
