#include <SPI.h>
#include "LCD_Driver.h"
#include "GUI_Paint.h"
#include "image.h"
#include "OneButton.h"

#define PIN_INPUT 0
OneButton button(PIN_INPUT, true);

void setup() {
  Serial.begin(115200);
  Config_Init();
  LCD_Init();
  LCD_SetBacklight(100);
  Paint_NewImage(LCD_WIDTH, LCD_HEIGHT, 90, WHITE);
  Paint_SetRotate(90);
  LCD_Clear(BLACK);
  Paint_DrawString_EN(28, 50, "Button Start", &Font24, BLACK, GREEN);

  button.attachLongPressStart(LongPressStart, &button);
  button.attachClick(Click, &button);
  button.attachDoubleClick(DoubleClick, &button);
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
  LCD_Clear(BLACK);
  Paint_DrawString_EN(50, 50, "LongPress", &Font24, BLACK, RED);
}

void Click(void *oneButton)
{
  LCD_Clear(BLACK);
  Paint_DrawString_EN(75, 50, "Click", &Font24, BLACK, YELLOW);
}

void DoubleClick(void *oneButton)
{
  LCD_Clear(BLACK);
  Paint_DrawString_EN(35, 50, "DoubleClick", &Font24, BLACK, BLUE);
}