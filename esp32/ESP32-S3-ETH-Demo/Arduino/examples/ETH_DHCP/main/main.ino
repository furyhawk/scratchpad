/**
 ******************************************************************************
 * @file     ETH_DHCP.ino
 * @brief    Initialize W5500 Ethernet module using DHCP and print the IP address.
 * @version  V1.0
 * @date     2025-07-03
 * @license  MIT
 * @copyright Copyright (c) 2025, Waveshare Electronics CO.,LTD
 *
 * Experiment Objective:
 * Demonstrate how to initialize the W5500 Ethernet module on an Arduino-compatible 
 * board using DHCP, and display the assigned IP address through the serial console.
 *
 * Hardware Resources:
 * 1. ESP32-S3-ETH
 *
 * Experiment Phenomenon:
 * 1. The W5500 Ethernet module is initialized via SPI.
 * 2. The module attempts to obtain an IP address via DHCP.
 * 3. Upon success, the assigned IP address is printed to the serial console.
 *
 * Notes:
 * - Ensure the W5500 module is properly connected with matching SPI pins.
 * - The MAC address can be modified based on network requirements.
 *
 ******************************************************************************
 *
 * Development Platform: Arduino IDE 
 * Support Forum: service.waveshare.com
 * Company Website: www.waveshare.com
 *
 ******************************************************************************
 */

#include <SPI.h>
#include <Ethernet.h>

// Define W5500 pin assignments
#define W5500_CS    14  // Chip Select pin
#define W5500_RST    9  // Reset pin
#define W5500_INT   10  // Interrupt pin
#define W5500_MISO  12  // MISO pin
#define W5500_MOSI  11  // MOSI pin
#define W5500_SCK   13  // Clock pin

// MAC address (can be arbitrary or set according to network requirements)
byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };

EthernetClient client;

void setup() {
  Serial.begin(115200);  // Start serial communication
  while (!Serial) {
    ; // Wait for the serial port to be ready
  }

  // Initialize SPI with specified pin configuration
  SPI.begin(W5500_SCK, W5500_MISO, W5500_MOSI, W5500_CS);

  // Initialize Ethernet using DHCP to obtain an IP address
  Ethernet.init(W5500_CS);
  if (Ethernet.begin(mac) == 0) {
    Serial.println("Failed to configure Ethernet using DHCP");
    while (true); // Halt if DHCP configuration fails
  }

  // Print the assigned IP address
  Serial.print("IP Address: ");
  Serial.println(Ethernet.localIP());
}

void loop() {
  delay(1000); // Wait for 1 second
}
