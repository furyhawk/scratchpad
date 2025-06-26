/*
  Keyboard logout

  This sketch demonstrates the Keyboard library.

  When you connect pin 2 to ground, it performs a logout.
  It uses keyboard combinations to do this, as follows:

  On Windows, CTRL-ALT-DEL followed by ALT-l
  On Ubuntu, CTRL-ALT-DEL, and ENTER
  On OSX, CMD-SHIFT-q

  To wake: Spacebar.

  Circuit:
  - Arduino Leonardo or Micro
  - wire to connect D2 to ground

  created 6 Mar 2012
  modified 27 Mar 2012
  by Tom Igoe

  This example is in the public domain.

  https://www.arduino.cc/en/Tutorial/BuiltInExamples/KeyboardLogout
*/

#define OSX 0
#define WINDOWS 1
#define UBUNTU 2
#include "Keyboard.h"
#include <FastLED.h>

#define LED_PIN     18 //GP18
#define NUM_LEDS    3

CRGB leds[NUM_LEDS];
int flag[3];

// change this to match your platform:
int platform = WINDOWS;

void setup() {
  // make pin 2 an input and turn on the pull-up resistor so it goes high unless
  // connected to ground:
  pinMode(12, INPUT_PULLUP);
  pinMode(13, INPUT_PULLUP);
  pinMode(14, INPUT_PULLUP);
  pinMode(25, OUTPUT);
  FastLED.addLeds<WS2812, LED_PIN, GRB>(leds, NUM_LEDS);
  Keyboard.begin();
}

void setup1() {
  FastLED.addLeds<WS2812, LED_PIN, GRB>(leds, NUM_LEDS);
  for(int i = 0;i <= 2;i++){
    leds[i] = CRGB(255,255,255);
    FastLED.show();
  }
  delay(20);
  for(int i = 0;i <= 2;i++){
    leds[i] = CRGB(0,0,0);
    FastLED.show();
  }
  delay(20);
  for(int i = 0;i <= 2;i++){
    leds[i] = CRGB(255,255,255);
    FastLED.show();
  }
  delay(20);
  for(int i = 0;i <= 2;i++){
    leds[i] = CRGB(0,0,0);
    FastLED.show();
  }
  delay(20);
}

void loop1() {
  while (1){
    for(int i = 0;i <= 2;i++){
      leds[i] = CRGB(flag[1]*255,flag[0]*255,flag[2]*255);
      FastLED.show();
      delay(5);
    }
  }
}

void loop() {
  if(digitalRead(12) == LOW){
    Keyboard.press('v');
    flag[2]=1; 
  }else{
    Keyboard.release('v');
    flag[2]=0; 
  }

  if(digitalRead(13) == LOW){
    Keyboard.press('c');
    flag[1]=1;  
  }else{
    Keyboard.release('c');
    flag[1]=0;  
  }
  
  if(digitalRead(14) == LOW){
    Keyboard.press(KEY_LEFT_CTRL);
    flag[0]=1; 
  }else{
    Keyboard.release(KEY_LEFT_CTRL);
    flag[0]=0; 
  }  

  delay(10);
}
