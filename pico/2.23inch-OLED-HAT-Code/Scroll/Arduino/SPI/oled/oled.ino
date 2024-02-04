/*********************************************************************************************************
*
* File                : oled.ino
* Hardware Environment: Arduino UNO
* Build Environment   : Arduino
* Version             : V1.0.7
*
*                                  (c) Copyright 2005-2019, WaveShare
*                                       http://www.waveshare.com
*                                       http://www.waveshare.net   
*                                          All Rights Reserved
*
*********************************************************************************************************/
#include <SPI.h>
#include <Wire.h>
#include "ssd1305.h"

#define WIDTH     132
#define HEIGHT     64
#define PAGES       4

#define OLED_RST    9 
#define OLED_DC     8
#define OLED_CS    10
#define SPI_MOSI   11    /* connect to the DIN pin of OLED */
#define SPI_SCK    13     /* connect to the CLK pin of OLED */

uint8_t oled_buf[WIDTH * HEIGHT / 8];

void setup() {
  Serial.begin(9600);
  Serial.print("OLED Example\n");

  /* display an image of bitmap matrix */
  SSD1305_begin();
  SSD1305_clear(oled_buf);
  
  SSD1305_Scrolling_Set(); //Set scroll mode 
  
  SSD1305_bitmap(7, 0, waveshare_ch, 112, 32, oled_buf);
  SSD1305_bitmap(7, 32, waveshare_ch, 112, 64, oled_buf);
  SSD1305_display(oled_buf);
  
  SSD1305_Scrolling_Start();//Start rolling
}

void loop() {

}
