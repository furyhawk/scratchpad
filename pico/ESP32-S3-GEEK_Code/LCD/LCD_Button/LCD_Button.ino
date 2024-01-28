#include <SPI.h>
#include "LCD_Driver.h"
#include "GUI_Paint.h"
#include "image.h"
#include "OneButton.h"

#define PIN_INPUT 0
OneButton button(PIN_INPUT, true);

char click = 1;

void setup() {
  Serial.begin(115200);
  Config_Init();
  LCD_Init();
  LCD_Clear(BLACK);
  LCD_SetBacklight(1000);
  Paint_NewImage(LCD_WIDTH, LCD_HEIGHT, 0, BLACK);
  Paint_DrawImage(gImage_pic1, 0, 0, 135, 240);

  button.attachLongPressStart(LongPressStart, &button);
  button.attachClick(Click, &button);
  button.setLongPressIntervalMs(1000);
}

void loop() {
  // keep watching the push button:
  button.tick();

  delay(10);
}

// this function will be called when the button started long pressed.
void LongPressStart(void *oneButton)
{
  analogWrite(DEV_BL_PIN, 0);
}

void Click(void *oneButton)
{
  LCD_SetBacklight(1000);
  Paint_NewImage(LCD_WIDTH, LCD_HEIGHT, 0, BLACK);
  click++;
  if(click >= 4)click = 1;
  switch(click)
  {
    case 1:  
    Paint_DrawImage(gImage_pic1, 0, 0, 135, 240);
    break;
    case 2:  
    Paint_DrawImage(gImage_pic2, 0, 0, 135, 240);
    break;
    case 3: 
    Paint_DrawImage(gImage_pic3, 0, 0, 135, 240);
    break;
  }
}