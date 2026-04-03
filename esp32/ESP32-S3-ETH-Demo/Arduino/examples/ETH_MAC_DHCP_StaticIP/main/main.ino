/**
 ******************************************************************************
 * @file     ETH_MAC_DHCP_StaticIP.ino
 * @brief    Initialize W5500 Ethernet module using DHCP with a static IP fallback.
 * @version  V1.0
 * @date     2025-07-03
 * @license  MIT
 * @copyright Copyright (c) 2025, Waveshare Electronics CO.,LTD
 *
 * Experiment Objective:
 * Demonstrate how to configure the W5500 Ethernet module via DHCP, and fallback 
 * to a static IP if DHCP fails.
 *
 * Hardware Resources:
 * 1. ESP32-S3-ETH
 *
 * Experiment Phenomenon:
 * 1. The W5500 module initializes via SPI with custom pin settings.
 * 2. Attempts to obtain an IP address via DHCP.
 * 3. If DHCP fails, uses a static IP as backup.
 * 4. Prints the assigned IP address to the serial console.
 *
 * Notes:
 * - Requires the Ethernet_Generic library or compatible W5500 Ethernet library.
 * - Be sure the W5500 module is properly connected to the MCU.
 *
 ******************************************************************************
 *
 * Development Platform: Arduino IDE / PlatformIO
 * Support Forum: service.waveshare.com
 * Company Website: www.waveshare.com
 *
 ******************************************************************************
 */

#include <SPI.h>
#include <Ethernet_Generic.h>  // Or Ethernet.h depending on installed library

// W5500 Pin Assignments
#define W5500_CS     14  // Chip Select (CS)
#define W5500_RST     9  // Reset (RST)
#define W5500_INT    10  // Interrupt (INT) - optional
#define W5500_MISO   12  // MISO
#define W5500_MOSI   11  // MOSI
#define W5500_SCK    13  // SPI Clock (SCK)

// MAC address (can be random but should be unique on the network)
byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };

// Ethernet client instance
EthernetClient client;

void setup() {
  // Start serial communication
  Serial.begin(115200);
  while (!Serial) {
    ; // Wait for serial port to be ready (for native USB boards)
  }

  // Initialize SPI with custom pins
  SPI.begin(W5500_SCK, W5500_MISO, W5500_MOSI, W5500_CS);

  // Optional: Reset the W5500 module
  pinMode(W5500_RST, OUTPUT);
  digitalWrite(W5500_RST, LOW);
  delay(100);
  digitalWrite(W5500_RST, HIGH);
  delay(100);

  // Initialize Ethernet with specified CS pin
  Ethernet.init(W5500_CS);

  // Try to configure using DHCP
  if (Ethernet.begin(mac) == 0) {
    Serial.println("DHCP failed, falling back to static IP...");

    // Static IP fallback settings
    IPAddress ip(192, 168, 1, 177);
    IPAddress gateway(192, 168, 1, 1);
    IPAddress subnet(255, 255, 255, 0);
    IPAddress dns(192, 168, 1, 1);

    // Initialize with static IP
    Ethernet.begin(mac, ip, dns, gateway, subnet);
  }

  delay(1000);

  // Print the assigned IP address
  Serial.print("IP Address: ");
  Serial.println(Ethernet.localIP());
}

void loop() {
  // Your main loop code here (e.g., TCP/UDP handling)
}
