/**
 ******************************************************************************
 * @file     ETH_StaticIP.ino
 * @brief    Initialize W5500 Ethernet module with static IP configuration and 
 *           print the assigned IP address to the serial monitor.
 * @version  V1.1
 * @date     2025-07-03
 * @license  MIT
 * @copyright Copyright (c) 2025, Waveshare Electronics CO.,LTD
 *
 * Experiment Objective:
 * Demonstrate how to configure the W5500 Ethernet module with a static IP 
 * address and verify network initialization by printing the IP to the console.
 *
 * Hardware Resources:
 * 1. ESP32-S3-ETH
 *
 * Experiment Phenomenon:
 * 1. The W5500 module is initialized via SPI with user-defined pin assignments.
 * 2. The module is configured with a static IP address.
 * 3. The assigned IP address is printed via the serial port after successful setup.
 *
 * Notes:
 * - Ensure W5500 wiring matches the defined pin numbers.
 * - Modify the static IP settings according to your local network environment.
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

// W5500 Pin Definitions
#define W5500_CS     14  // Chip Select pin
#define W5500_RST     9  // Reset pin (optional, not used here)
#define W5500_INT    10  // Interrupt pin (optional, not used here)
#define W5500_MISO   12  // MISO pin
#define W5500_MOSI   11  // MOSI pin
#define W5500_SCK    13  // Clock pin

// MAC address (customize if required)
byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };

// Static IP Configuration
IPAddress ip(192, 168, 9, 200);         // Static IP address
IPAddress dns(192, 168, 9, 1);          // DNS server
IPAddress gateway(192, 168, 9, 1);      // Gateway address
IPAddress subnet(255, 255, 255, 0);     // Subnet mask

EthernetClient client;

void setup() {
  Serial.begin(115200);  // Start serial communication
  while (!Serial) {
    ; // Wait until serial port is ready
  }

  // Initialize SPI with custom pin configuration
  SPI.begin(W5500_SCK, W5500_MISO, W5500_MOSI, W5500_CS);

  // Initialize Ethernet with static IP settings
  Ethernet.init(W5500_CS);
  Ethernet.begin(mac, ip, dns, gateway, subnet);

  // Verify if IP address is properly assigned
  if (Ethernet.localIP() == IPAddress(0, 0, 0, 0)) {
    Serial.println("Failed to configure Ethernet with static IP");
    while (true); // Halt on failure
  }

  // Print assigned IP address
  Serial.print("IP Address: ");
  Serial.println(Ethernet.localIP());
}

void loop() {
  delay(1000); // Wait for 1 second
}
