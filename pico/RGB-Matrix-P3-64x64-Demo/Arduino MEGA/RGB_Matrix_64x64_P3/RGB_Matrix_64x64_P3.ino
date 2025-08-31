// testshapes demo for RGBmatrixPanel library.
// Demonstrates the drawing abilities of the RGBmatrixPanel library.
// For 64x64 RGB LED matrix.

// WILL NOT FIT on ARDUINO UNO -- requires a Mega, M0 or M4 board

#include "RGBmatrixPanel.h"

#include "bit_bmp.h"
#include "fonts.h"
#include <string.h>
#include <stdlib.h>

// Most of the signal pins are configurable, but the CLK pin has some
// special constraints.  On 8-bit AVR boards it must be on PORTB...
// Pin 11 works on the Arduino Mega.  On 32-bit SAMD boards it must be
// on the same PORT as the RGB data pins (D2-D7)...
// Pin 8 works on the Adafruit Metro M0 or Arduino Zero,
// Pin A4 works on the Adafruit Metro M4 (if using the Adafruit RGB
// Matrix Shield, cut trace between CLK pads and run a wire to A4).

//#define CLK  8   // USE THIS ON ADAFRUIT METRO M0, etc.
//#define CLK A4 // USE THIS ON METRO M4 (not M0)
#define CLK 11 // USE THIS ON ARDUINO MEGA
#define OE   9
#define LAT 10
#define A   A0
#define B   A1
#define C   A2
#define D   A3
#define E   A4

RGBmatrixPanel matrix(A, B, C, D, E, CLK, LAT, OE, false, 64);
//Configure the serial port to use the standard printf function

void setup()
{
  Serial.begin(115200);
  matrix.begin();
  delay(500);
}



void loop()
{
  // Do nothing -- image doesn't change
 Demo_0();
 Demo_1();
 Demo_2();
}

//Clear screen
void screen_clear()
{
  matrix.fillRect(0, 0, matrix.width(), matrix.height(), matrix.Color333(0, 0, 0));
}


void Demo_0()
{
  // draw a pixel in solid white
  screen_clear();
  matrix.setFont(NULL);
  matrix.drawPixel(0, 0, matrix.Color333(7, 7, 7));
  delay(500);

    matrix.fillRect(0, 0, matrix.width(), matrix.height(), matrix.Color333(0, 7, 0));
    delay(500);

    matrix.drawRect(0, 0, matrix.width(), matrix.height(), matrix.Color333(7, 7, 0));
    delay(500);

    // draw an 'X' in red
    matrix.drawLine(0, 0, matrix.width()-1, matrix.height()-1, matrix.Color333(7, 0, 0));
    matrix.drawLine(matrix.width()-1, 0, 0, matrix.height()-1, matrix.Color333(7, 0, 0));
    delay(500);

    // draw a blue circle
    matrix.drawCircle(10, 10, 10, matrix.Color333(0, 0, 7));
    delay(500);

    // fill a violet circle
    matrix.fillCircle(40, 21, 10, matrix.Color333(7, 0, 7));
    delay(500);

    // fill the screen with 'black'
    screen_clear();

    // draw some text!
    matrix.setTextSize(1);     // size 1 == 8 pixels high
    matrix.setTextWrap(false); // Don't wrap at end of line - will do ourselves

    matrix.setCursor(5, 0);    // start at top left, with 8 pixel of spacing
    uint8_t w = 0;
    char *str = "WaveshareElectronics";
    for (w=0; w<9; w++) {
      matrix.setTextColor(Wheel(w));
      matrix.print(str[w]);
    }
    matrix.setCursor(0, 8);    // next line
    for (w=9; w<20; w++) {
      matrix.setTextColor(Wheel(w));
      matrix.print(str[w]);
    }
    matrix.println();
    //matrix.setTextColor(matrix.Color333(4,4,4));
    //matrix.println("Industries");
    matrix.setTextColor(matrix.Color333(7,7,7));
    matrix.println("RGB MATRIX!");

    // print each letter with a rainbow color
    matrix.setTextColor(matrix.Color333(7,0,0));
    matrix.print('6');
    matrix.setTextColor(matrix.Color333(7,4,0));
    matrix.print('4');
    matrix.setTextColor(matrix.Color333(7,7,0));
    matrix.print('x');
    matrix.setTextColor(matrix.Color333(4,7,0));
    matrix.print('6');
    matrix.setTextColor(matrix.Color333(0,7,0));
    matrix.print('4');
    matrix.setCursor(40, 24);

    matrix.setTextColor(matrix.Color333(0,4,7));
    matrix.print('R');
    matrix.setTextColor(matrix.Color333(0,0,7));
    matrix.print('G');
    matrix.setTextColor(matrix.Color333(4,0,7));
    matrix.print('B');


    matrix.setCursor(5, 32);    // start at middle left, with 8 pixel of spacing
    for (w=0; w<9; w++) {
      matrix.setTextColor(Wheel(w));
      matrix.print(str[w]);
    }
    matrix.setCursor(0, 40);    // next line
    for (w=9; w<20; w++) {
      matrix.setTextColor(Wheel(w));
      matrix.print(str[w]);
    }
    matrix.println();
    //matrix.setTextColor(matrix.Color333(4,4,4));
    //matrix.println("Industries");
    matrix.setTextColor(matrix.Color333(7,7,7));
    matrix.println("LED MATRIX!");

    // print each letter with a rainbow color
    matrix.setTextColor(matrix.Color333(7,0,0));
    matrix.print('6');
    matrix.setTextColor(matrix.Color333(7,4,0));
    matrix.print('4');
    matrix.setTextColor(matrix.Color333(7,7,0));
    matrix.print('x');
    matrix.setTextColor(matrix.Color333(4,7,0));
    matrix.print('6');
    matrix.setTextColor(matrix.Color333(0,7,0));
    matrix.print('4');
    matrix.setCursor(40, 56);
    matrix.setTextColor(matrix.Color333(0,4,7));
    matrix.print('R');
    matrix.setTextColor(matrix.Color333(0,0,7));
    matrix.print('G');
    matrix.setTextColor(matrix.Color333(4,0,7));
    matrix.print('B');
    delay(2000);
}

// Input a value 0 to 7 to get a color value.
// The colours are a transition r - g - b - back to r.
uint16_t Wheel(byte WheelPos) {
  if(WheelPos < 8) {
   return matrix.Color333(7 - WheelPos, WheelPos, 0);
  } else if(WheelPos < 16) {
   WheelPos -= 8;
   return matrix.Color333(0, 7-WheelPos, WheelPos);
  } else {
   WheelPos -= 16;
   return matrix.Color333(WheelPos, 0, 7 - WheelPos);
  }
}

/*  @name :  display_Image
 *  @brief:  display an image
 *           The image data is in the "bit_bmp.h"
 *           You can use some tools to get the image data
 *           You can set the data bits which is 8 or 16 and set the MSB first which is true or false on line 1001 of Adafruit_GFX.c
 *  @param:    x   Top left corner x coordinate
 *             y   Top left corner y coordinate
 *         bitmap  byte array with 16-bit color bitmap,the image data is in the "bit_bmp.h"
 *             w   Width of bitmap in pixels
 *             h   Height of bitmap in pixels
 *  @retval: None
 */
void display_Image(int16_t x, int16_t y, const uint16_t bitmap[],int16_t w, int16_t h)
{
  matrix.display_image(x, y, bitmap, w, h);
}

#include "Fonts/FreeSerif9pt7b.h"
#include "Fonts/FreeSerifBoldItalic9pt7b.h"
#include "Fonts/RobotoMono_Thin7pt7b.h"
#include "Fonts/FreeSans9pt7b.h"

/*  @name : display_text
 *  @brief: display a text string
 *  @param:    x            X coordinate in pixels
 *             y            Y coordinate in pixels
 *           *str           Text string
 *            *f            Text font,if you use the default font,the value will be NULL,
 *                                    if you use other font ,you should add header file of font to folder named “Fonts” like this Demo
 *           color          16-bit 5-6-5 Color to draw text with
 *         pixels_size      Desired text size. 1 is default 6x8, 2 is 12x16, 3 is 18x24, etc
 *  
 *  @retval: None
 */
void display_text(int x, int y, char *str, const GFXfont *f, int color, int pixels_size)
{
  matrix.setTextSize(pixels_size);// size 1 == 8 pixels high
  matrix.setTextWrap(false); // Don't wrap at end of line - will do ourselves
  matrix.setFont(f);      //set font
  matrix.setCursor(x, y);
  matrix.setTextColor(color);
  matrix.println(str);
}
void Demo_1()
{
  screen_clear();
  display_text(-1, 14, "R", &FreeSerif9pt7b, matrix.Color333(7, 0, 0), 1);
  display_text(8 , 14, "G", &FreeSerif9pt7b, matrix.Color333(0, 7, 0), 1);
  display_text(19, 14, "B", &FreeSerif9pt7b, matrix.Color333(0, 0, 7), 1);
  display_text(31,  5, "m", NULL, 0x7800, 1);
  display_text(37,  5, "a", NULL, 0xFFE0, 1);
  display_text(42,  5, "t", NULL, 0x07E0, 1);
  display_text(48,  5, "r", NULL, 0X001F, 1);
  display_text(53,  5, "i", NULL, 0x07FF, 1);
  display_text(58,  5, "x", NULL, 0x780F, 1);
  display_text(-1, 30, "P30",&RobotoMono_Thin7pt7b, 0xFFE0, 1);
  display_text(12, 25, ".",NULL, 0xFFE0, 1);
  display_text(21, 30, "6",&FreeSerifBoldItalic9pt7b , 0x780F, 1);
  display_text(29, 30, "4",&FreeSerifBoldItalic9pt7b , 0x780F, 1);
  display_text(38, 30, "x",&FreeSans9pt7b , 0x780F, 1);
  display_text(46, 30, "6",&FreeSerifBoldItalic9pt7b , 0x780F, 1);
  display_text(54, 30, "4",&FreeSerifBoldItalic9pt7b , 0x780F, 1);

  display_text(-1, 14+32, "R", &FreeSerif9pt7b, matrix.Color333(7, 0, 0), 1);
  display_text(8 , 14+32, "G", &FreeSerif9pt7b, matrix.Color333(0, 7, 0), 1);
  display_text(19, 14+32, "B", &FreeSerif9pt7b, matrix.Color333(0, 0, 7), 1);
  display_text(31,  5+32, "M", NULL, 0x7800, 1);
  display_text(37,  5+32, "a", NULL, 0xFFE0, 1);
  display_text(42,  5+32, "t", NULL, 0x07E0, 1);
  display_text(48,  5+32, "r", NULL, 0X001F, 1);
  display_text(53,  5+32, "i", NULL, 0x07FF, 1);
  display_text(58,  5+32, "x", NULL, 0x780F, 1);
  display_text(-1, 30+32, "P30",&RobotoMono_Thin7pt7b, 0xFFE0, 1);
  display_text(12, 25+32, ".",NULL, 0xFFE0, 1);
  display_text(21, 30+32, "6",&FreeSerifBoldItalic9pt7b , 0x780F, 1);
  display_text(29, 30+32, "4",&FreeSerifBoldItalic9pt7b , 0x780F, 1);
  display_text(38, 30+32, "x",&FreeSans9pt7b , 0x780F, 1);
  display_text(46, 30+32, "6",&FreeSerifBoldItalic9pt7b , 0x780F, 1);
  display_text(54, 30+32, "4",&FreeSerifBoldItalic9pt7b , 0x780F, 1);
  delay(2000);
    
  display_Image(0, 0, gImage_image, 64, 64);
  delay(2000);
}

void Demo_2()
{
    screen_clear();
    matrix.DrawString_CN( 1   , 12, "微", &Font16CN, matrix.Color333(7, 0, 0));
    matrix.DrawString_CN( 1+16, 12, "雪", &Font16CN, matrix.Color333(6, 1, 0));
    matrix.DrawString_CN( 1+32, 12, "电", &Font16CN, matrix.Color333(5, 2, 7));
    matrix.DrawString_CN( 1+48, 12, "子", &Font16CN, matrix.Color333(0, 7, 0));   
    matrix.DrawString_CN( 1    ,35, "欢", &Font16CN, matrix.Color333(0, 6, 1));
    matrix.DrawString_CN( 1+16, 35, "迎", &Font16CN, matrix.Color333(0, 5, 2));
    matrix.DrawString_CN( 1+32, 35, "您", &Font16CN, matrix.Color333(0, 0, 7));
    matrix.DrawString_CN( 1+48, 35, "！", &Font16CN, matrix.Color333(1, 0, 6));
    delay(2000);
    screen_clear();
    matrix.DrawString_CN( 1   ,  0, "微", &Font32CN, matrix.Color333(0, 7, 7));
    matrix.DrawString_CN( 1+32,  0, "雪", &Font32CN, matrix.Color333(0, 7, 7));
    matrix.DrawString_CN( 1   ,  32,"电", &Font32CN, matrix.Color333(0, 7, 7));
    matrix.DrawString_CN( 1+32,  32,"子", &Font32CN, matrix.Color333(0, 7, 7));
    delay(2000);
    screen_clear();
    matrix.DrawString_CN( 1   ,   0, "欢", &Font32CN, matrix.Color333(0, 7, 7));
    matrix.DrawString_CN( 1+32,   0, "迎", &Font32CN, matrix.Color333(0, 7, 7));
    matrix.DrawString_CN( 1   ,   32,"您", &Font32CN, matrix.Color333(0, 7, 7));
    matrix.DrawString_CN( 1+37,   32,"！", &Font32CN, matrix.Color333(0, 7, 7));
    delay(2000);
    screen_clear();
    matrix.DrawString_CN( 0, 0, "微", &Font64CN, matrix.Color333(7, 0, 0));
    delay(1000);
    screen_clear();
    matrix.DrawString_CN( 0, 0, "雪", &Font64CN, matrix.Color333(0, 7, 0));
    delay(1000);
    screen_clear();
    matrix.DrawString_CN( 0, 0, "电", &Font64CN, matrix.Color333(0, 0, 7));
    delay(1000);
    screen_clear();
    matrix.DrawString_CN( 0, 0, "子", &Font64CN, matrix.Color333(7, 7, 7));
    delay(1000);
    screen_clear();
    matrix.DrawString_CN( 0, 0, "欢", &Font64CN, matrix.Color333(7, 5, 0));
    delay(1000);
    screen_clear();
    matrix.DrawString_CN( 0, 0, "迎", &Font64CN, matrix.Color333(0, 7, 5));
    delay(1000);
    screen_clear();
    matrix.DrawString_CN( 0, 0, "您", &Font64CN, matrix.Color333(5, 0, 7));
    delay(1000);
    screen_clear();
    matrix.DrawString_CN( 13, 0, "！", &Font64CN, matrix.Color333(7, 7, 7));
    delay(2000);
    screen_clear();
}

