/**
 * This example turns the ESP32 into a Bluetooth LE keyboard that writes the words, presses Enter, presses a media key and then Ctrl+Alt+Delete
 */
#include <BleKeyboard.h>
#include <Arduino.h>

BleKeyboard bleKeyboard;

void setup() {
  Serial.begin(115200);
  Serial.println("Starting BLE work!");
  bleKeyboard.begin();
}

void loop() {
  if(bleKeyboard.isConnected()) {
    Serial.println("Sending 'Hello world'...");
    printf("Sending 'Hello world'...\n");
    bleKeyboard.print("Hello world");

    delay(1000);

    Serial.println("Sending Enter key...");
    printf("Sending Enter key...\n");
    bleKeyboard.write(KEY_RETURN);

    delay(1000);

    Serial.println("Sending Play/Pause media key...");
    printf("Sending Play/Pause media key...\n");
    bleKeyboard.write(KEY_MEDIA_PLAY_PAUSE);

    delay(1000);

   //
   // Below is an example of pressing multiple keyboard modifiers 
   // which by default is commented out.
    /*
    Serial.println("Sending Ctrl+Alt+Delete...");
    bleKeyboard.press(KEY_LEFT_CTRL);
    bleKeyboard.press(KEY_LEFT_ALT);
    bleKeyboard.press(KEY_DELETE);
    delay(100);
    bleKeyboard.releaseAll();
    */
  }

  Serial.println("Waiting 5 seconds...");
  delay(5000);
}
