/**
 ******************************************************************************
 * @file     IO_Test.ino
 * @author   Kaloha
 * @version  V1.0
 * @date     2024-10-10
 * @brief    GPIO control experiment
 * @license  MIT
 * @copyright Copyright (c) 2024, Waveshare Electronics CO.,LTD
 ******************************************************************************
 * 
 * Experiment Objective: Learn how to use GPIO as an output to control multiple GPIO pins.
 *
 * Hardware Resources and Pin Assignment: 
 * 1. GPIO Pins --> ESP32-S3-ETH Module
 *    GPIO Pins used: {21, 17, 16, 18, 15, 3, 2, 1, 0, 44, 43, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 45, 46, 47, 48}
 *
 * Experiment Phenomenon:
 * 1. GPIO pins will be set HIGH and LOW sequentially every 300ms.
 * 
 * Notes:
 * None
 * 
 ******************************************************************************
 * 
 * Development Platform: Waveshare ESP32-S3-ETH Module
 * Support Forum: service.waveshare.com
 * Company Website: www.waveshare.com
 *
 ******************************************************************************
 */

#define NUM_GPIO 25

// Define GPIO pins
const int gpio_pin[NUM_GPIO] = {21, 17, 16, 18, 15, 3, 2, 1, 0, 44, 43, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 45, 46, 47, 48};

char current_gpio = 0;

void setup() {
  //Serial.begin(9600); 
  char i = 0;
  
  // Set all GPIO pins to OUTPUT mode and turn them off initially
  for (i = 0; i < NUM_GPIO; i++) {
      pinMode(gpio_pin[i], OUTPUT); // Set GPIO pin as output
      digitalWrite(gpio_pin[i], LOW); // Set GPIO pin to LOW (turn off)
      printf("GPIO %d initialized to LOW.\n", gpio_pin[i]); // Use printf to print GPIO state
  }
}

void loop() {
  // Turn on each GPIO one by one
  for (current_gpio = 0; current_gpio < NUM_GPIO; current_gpio++) {
      digitalWrite(gpio_pin[current_gpio], HIGH); // Set GPIO pin to HIGH (turn on)
      printf("GPIO %d set to HIGH.\n", gpio_pin[current_gpio]); // Print GPIO state
      delay(300); // Delay for 300ms
  }

  // Turn off each GPIO one by one
  for (current_gpio = 0; current_gpio < NUM_GPIO; current_gpio++) {
      digitalWrite(gpio_pin[current_gpio], LOW); // Set GPIO pin to LOW (turn off)
      printf("GPIO %d set to LOW.\n", gpio_pin[current_gpio]); // Print GPIO state
      delay(300); // Delay for 300ms
  }
}
