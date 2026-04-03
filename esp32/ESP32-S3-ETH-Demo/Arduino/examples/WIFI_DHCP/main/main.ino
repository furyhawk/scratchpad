/**
 ******************************************************************************
 * @file     WiFi_DHCP.ino
 * @brief    Connect ESP32 to a Wi-Fi network and print the assigned IP address.
 * @version  V1.0
 * @date     2025-07-03
 * @license  MIT
 * @copyright Copyright (c) 2025, Waveshare Electronics CO.,LTD
 *
 * Experiment Objective:
 * Demonstrate how to connect an ESP32 to a Wi-Fi Access Point using SSID and 
 * password, and print the IP address assigned by the router.
 *
 * Hardware Resources:
 * 1. ESP32-S3-ETH
 *
 * Experiment Phenomenon:
 * 1. The device connects to the specified Wi-Fi network.
 * 2. After connection, the assigned IP address is printed to the serial console.
 *
 * Notes:
 * - Ensure the SSID and password match your local Wi-Fi network.
 *
 ******************************************************************************
 *
 * Development Platform: Arduino IDE / PlatformIO
 * Support Forum: service.waveshare.com
 * Company Website: www.waveshare.com
 *
 ******************************************************************************
 */

#include <WiFi.h>  // Include Wi-Fi library

// Replace with your Wi-Fi network credentials
const char *ssid = "Waveshare";         // Your WiFi SSID
const char *password = "88888888";      // Your WiFi password

void setup() {
  // Start serial communication
  Serial.begin(115200);
  while (!Serial) {
    ; // Wait for the serial port to be ready
  }

  Serial.println();
  Serial.println("Connecting to WiFi...");

  // Begin Wi-Fi connection
  WiFi.begin(ssid, password);

  // Wait until connected
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  // Connection successful
  Serial.println();
  Serial.println("Connected to WiFi");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP()); // Print assigned IP address
}

void loop() {
  // Keep connection alive (optional: can be used to add functionality)
  delay(1000);
}
