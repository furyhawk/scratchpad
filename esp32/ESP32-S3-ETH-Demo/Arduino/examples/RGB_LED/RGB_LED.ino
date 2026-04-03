/**
 ****************************************************************************** 
 * @file     RGB_LED.ino
 * @brief    Control and demonstrate RGB LED effects using NeoPixel.
 *           Includes color wipe, rainbow, and theater chase effects.
 * @version  V1.0
 * @date     2024-12-21
 * @license  MIT
 ****************************************************************************** 
 * Experiment Objective: Demonstrate basic RGB LED control, including static 
 *                       and dynamic effects such as color transitions and 
 *                       theater chase.
 *
 * Hardware Resources:
 * 1. NeoPixel RGB LED strip --> Connected via a defined pin.
 *
 ****************************************************************************** 
 * Development Platform: Arduino/ESP32
 * Support Forum: service.waveshare.com
 * Company Website: www.waveshare.com
 *
 ****************************************************************************** 
 */

#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
  #include <avr/power.h>
#endif

#define PIN 21           // Pin connected to NeoPixel
#define LED1 -1          // GPIO for an additional LED (optional)

Adafruit_NeoPixel strip = Adafruit_NeoPixel(60, PIN, NEO_GRB + NEO_KHZ800);

void setup() {
  #if defined (__AVR_ATtiny85__)
    if (F_CPU == 16000000) clock_prescale_set(clock_div_1);
  #endif

  strip.begin();
  strip.setBrightness(50);
  strip.show();

  pinMode(LED1, OUTPUT);
  digitalWrite(LED1, HIGH);  // Turn on the additional LED
}

void loop() {
  colorWipe(strip.Color(255, 0, 0), 50); // Red
  colorWipe(strip.Color(0, 255, 0), 50); // Green
  colorWipe(strip.Color(0, 0, 255), 50); // Blue

  digitalWrite(LED1, LOW);               // Turn off the additional LED
  theaterChase(strip.Color(127, 127, 127), 50); // White
  theaterChase(strip.Color(127, 0, 0), 50);     // Red
  theaterChase(strip.Color(0, 0, 127), 50);     // Blue
  digitalWrite(LED1, HIGH);              // Turn on the additional LED
}

void colorWipe(uint32_t c, uint8_t wait) {
  for(uint16_t i = 0; i < strip.numPixels(); i++) {
    strip.setPixelColor(i, c);
    strip.show();
    delay(wait);
  }
}

void rainbow(uint8_t wait) {
  for(uint16_t j = 0; j < 256; j++) {
    for(uint16_t i = 0; i < strip.numPixels(); i++) {
      strip.setPixelColor(i, Wheel((i + j) & 255));
    }
    strip.show();
    delay(wait);
  }
}

void rainbowCycle(uint8_t wait) {
  for(uint16_t j = 0; j < 256 * 5; j++) {
    for(uint16_t i = 0; i < strip.numPixels(); i++) {
      strip.setPixelColor(i, Wheel(((i * 256 / strip.numPixels()) + j) & 255));
    }
    strip.show();
    delay(wait);
  }
}

void theaterChase(uint32_t c, uint8_t wait) {
  for (uint8_t j = 0; j < 10; j++) {
    for (uint8_t q = 0; q < 3; q++) {
      for (uint16_t i = 0; i < strip.numPixels(); i += 3) {
        strip.setPixelColor(i + q, c);
      }
      strip.show();
      delay(wait);
      for (uint16_t i = 0; i < strip.numPixels(); i += 3) {
        strip.setPixelColor(i + q, 0);
      }
    }
  }
}

void theaterChaseRainbow(uint8_t wait) {
  for (uint16_t j = 0; j < 256; j++) {
    for (uint8_t q = 0; q < 3; q++) {
      for (uint16_t i = 0; i < strip.numPixels(); i += 3) {
        strip.setPixelColor(i + q, Wheel((i + j) % 255));
      }
      strip.show();
      delay(wait);
      for (uint16_t i = 0; i < strip.numPixels(); i += 3) {
        strip.setPixelColor(i + q, 0);
      }
    }
  }
}

uint32_t Wheel(byte WheelPos) {
  WheelPos = 255 - WheelPos;
  if (WheelPos < 85) {
    return strip.Color(255 - WheelPos * 3, 0, WheelPos * 3);
  }
  if (WheelPos < 170) {
    WheelPos -= 85;
    return strip.Color(0, WheelPos * 3, 255 - WheelPos * 3);
  }
  WheelPos -= 170;
  return strip.Color(WheelPos * 3, 255 - WheelPos * 3, 0);
}
