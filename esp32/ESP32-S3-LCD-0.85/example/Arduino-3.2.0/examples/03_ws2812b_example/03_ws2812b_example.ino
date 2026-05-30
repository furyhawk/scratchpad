#include <FastLED.h>

// How many leds in your strip?
#define NUM_LEDS 8
#define DATA_PIN 48

// Define the array of leds
CRGB leds[NUM_LEDS];

void setup() { 
  FastLED.addLeds<WS2812B, DATA_PIN, RGB>(leds, NUM_LEDS);  // GRB ordering is typical
  FastLED.setBrightness(100); // 0-255
  for(int i = 0; i < NUM_LEDS; i++){
    leds[i] = CRGB::Red;
  }
  FastLED.show();
  
  delay(2000);
}

void loop() { 
  for(int i = 0; i < NUM_LEDS; i++){
    leds[i] = random(0xffffff);
  }
  FastLED.show();
  delay(500);
}
