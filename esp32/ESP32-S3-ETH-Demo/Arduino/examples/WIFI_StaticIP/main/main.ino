/**
 ******************************************************************************
 * @file     WiFi_StaticIP.ino
 * @brief    Connect ESP32 to Wi-Fi using static IP configuration.
 * @version  V1.0
 * @date     2025-07-03
 * @license  MIT
 * @copyright Copyright (c) 2025, Waveshare Electronics CO.,LTD
 *
 * Experiment Objective:
 * Demonstrate how to connect an ESP32 to a Wi-Fi Access Point with a static 
 * IP address and display the assigned IP through the serial monitor.
 *
 * Hardware Resources:
 * 1. ESP32-S3-ETH
 *
 * Experiment Phenomenon:
 * 1. The ESP32 configures itself with a fixed IP address.
 * 2. It connects to the specified Wi-Fi network.
 * 3. The IP address is printed to the serial console after successful connection.
 *
 * Notes:
 * - Make sure the static IP is in the same subnet as your router.
 * - Avoid IP conflicts with other devices on the network.
 *
 ******************************************************************************
 *
 * Development Platform: Arduino IDE
 * Support Forum: service.waveshare.com  
 * Company Website: www.waveshare.com
 *
 ******************************************************************************
 */

#include <WiFi.h>

// Wi-Fi credentials
const char *ssid = "Waveshare";         // Your WiFi SSID
const char *password = "88888888";      // Your WiFi password

// Static IP configuration
IPAddress local_ip(192, 168, 196, 100);        // Static IP
IPAddress gateway(192, 168, 196, 1);           // Gateway
IPAddress subnet(255, 255, 255, 0);          // Subnet mask
IPAddress dns(192, 168, 196, 1);               // DNS server

void setup() {
  // Start serial communication
  Serial.begin(115200);
  while (!Serial) {
    ; // Wait for serial port to be ready
  }

  // Set Wi-Fi mode to Station (client)
  WiFi.mode(WIFI_STA);

  // Apply static IP settings
  WiFi.config(local_ip, gateway, subnet, dns);

  // Begin Wi-Fi connection
  WiFi.begin(ssid, password);

  Serial.println("Connecting to Wi-Fi...");

  // Wait until connected
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting...");
  }

  // Print success message and assigned IP
  Serial.println("Connected to Wi-Fi!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  // Placeholder for your main code
  delay(1000);  // Delay for stability
}
