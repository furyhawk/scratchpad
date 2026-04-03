/**
 ******************************************************************************
 * @file     WiFi_AP.ino
 * @brief    Set up ESP32-S3-ETH module as a WiFi Access Point (AP) and 
 *           print the IP and MAC address of connected devices.
 * @version  V1.3
 * @date     2024-10-24
 * @license  MIT
 * @copyright Copyright (c) 2024, Waveshare Electronics CO.,LTD
 * 
 * Experiment Objective: Demonstrate how to set up ESP32-S3-ETH module as a 
 *                       WiFi Access Point and retrieve the IP address of 
 *                       connecting clients after DHCP assignment.
 * 
 * Hardware Resources:
 * 1. WiFi Interface --> ESP32-S3-ETH Module
 * 
 * Experiment Phenomenon:
 * 1. The ESP32-S3-ETH module initializes as a WiFi Access Point with the 
 *    specified SSID and password.
 * 2. When a device connects to the AP, its MAC address and assigned IP address
 *    are printed to the serial console after a short delay to allow DHCP 
 *    assignment.
 * 
 * Notes:
 * - This program uses ESP-IDF functions to retrieve client IP and MAC info.
 * 
 ******************************************************************************
 * 
 * Development Platform: Waveshare ESP32-S3-ETH Module
 * Support Forum: service.waveshare.com
 * Company Website: www.waveshare.com
 *
 ******************************************************************************
 */

#include <WiFi.h>
#include <esp_wifi.h>  // ESP-IDF library to access connected client info

// Define the SSID and password for the WiFi Access Point
const char* ssid     = "ESP32-S3-ETH";   // AP network name
const char* password = "88888888";       // AP password (minimum 8 characters)

// Format MAC address into a readable string
String formatMacAddress(const uint8_t* mac) {
    // Convert MAC address from byte array to readable format XX:XX:XX:XX:XX:XX
    char macStr[18];
    snprintf(macStr, sizeof(macStr), "%02X:%02X:%02X:%02X:%02X:%02X", 
             mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
    return String(macStr);
}

// WiFi event handler function
void WiFiEvent(WiFiEvent_t event, WiFiEventInfo_t info) {
    switch (event) {
        case ARDUINO_EVENT_WIFI_AP_STACONNECTED:
            // Print MAC address of newly connected device
            Serial.println("Device connected:");
            Serial.print("MAC Address: ");
            Serial.println(formatMacAddress(info.wifi_ap_staconnected.mac));
            break;

        case ARDUINO_EVENT_WIFI_AP_STADISCONNECTED:
            // Print message when device disconnects from AP
            Serial.println("Device disconnected");
            break;

        case ARDUINO_EVENT_WIFI_AP_STAIPASSIGNED:
            Serial.println("IP Address: ");
            Serial.println(IPAddress(info.got_ip.ip_info.ip.addr));

          break;

        default:
            break;
    }
}

void setup() {
    // Initialize serial communication at 115200 baud rate for debugging
    Serial.begin(115200); 

    // Set up ESP32 as a WiFi Access Point with the specified SSID and password
    WiFi.softAP(ssid, password);

    // Register the WiFi event handler to monitor client connections and disconnections
    WiFi.onEvent(WiFiEvent);

    // Short delay to allow WiFi setup to stabilize
    delay(1000);

    // Print confirmation message to the serial console
    Serial.println("Access Point initialized");
    Serial.print("SSID: ");
    Serial.println(ssid);
}

void loop() {                           
    // No operation in loop, CPU remains idle
    delay(1000);  // Small delay to prevent unnecessary CPU load
}
