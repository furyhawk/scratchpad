/**
 ******************************************************************************
 * @file     WIFI_STA.ino
 * @brief    Set up ESP32-S3 module as a WiFi station (STA) and a web server
 *           to control an LED on GPIO18. The web interface allows toggling
 *           the LED state and displays the current LED status as "LED ON" 
 *           or "LED OFF".
 * @version  V1.2
 * @date     2024-11-02
 * @license  MIT
 ******************************************************************************
 * Experiment Objective: Control an LED on GPIO18 of the ESP32-S3 module
 *                       via a web server interface with simple textual status.
 *
 * Hardware Resources:
 * 1. WiFi Interface --> ESP32-S3 Module in Station (STA) mode
 * 2. LED --> Connected to GPIO18
 *
 ******************************************************************************
 *
 * Development Platform: Waveshare ESP32-S3 Module
 * Support Forum: service.waveshare.com
 * Company Website: www.waveshare.com
 *
 ******************************************************************************
 */

#include <WiFi.h>

// Define WiFi network name (SSID) and password
const char *ssid = "Waveshare";         // Your WiFi SSID
const char *password = "88888888";      // Your WiFi password

WiFiServer server(80);                  // Create a web server object that listens on port 80

bool ledState = false;                  // Variable to store the current LED state

void setup() {
    // Initialize serial communication at 115200 baud for debugging purposes
    Serial.begin(115200);
    
    // Configure GPIO18 as an output pin for the LED
    pinMode(18, OUTPUT);
    digitalWrite(18, LOW);              // Ensure the LED starts off

    // Connect to WiFi
    Serial.println("\nConnecting to WiFi network: ");
    Serial.println(ssid);
    
    WiFi.begin(ssid, password);         // Start WiFi connection

    // Wait until WiFi is connected
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }

    // WiFi connected
    Serial.println("\nWiFi connected.");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());     // Print the local IP address

    // Start the server
    server.begin();
}

void loop() {
    // Check if a client has connected
    WiFiClient client = server.available();

    if (client) {
        Serial.println("New Client Connected.");
        String currentLine = "";        // Variable to hold the HTTP request line

        // Loop while the client is connected
        while (client.connected()) {
            if (client.available()) {   // If there's data to read from the client
                char c = client.read(); // Read one byte from the client
                Serial.write(c);        // Echo the byte to the Serial Monitor

                // Check if the byte is a newline character
                if (c == '\n') {
                    // If the current line is blank, the request is done
                    if (currentLine.length() == 0) {
                        // Send an HTTP response
                        client.println("HTTP/1.1 200 OK");
                        client.println("Content-type:text/html");
                        client.println();  // Blank line to separate header from content

                        // Web page content for controlling the LED
                        client.print("<!DOCTYPE html><html>");
                        client.print("<head><title>ESP32-S3 LED Control (GPIO18)</title>");
                        client.print("<style>");
                        client.print("body { font-family: Arial; text-align: center; background-color: #f0f0f0; }");
                        client.print(".status { font-size: 2em; margin: 20px; padding: 10px; border-radius: 5px; }");
                        client.print(".on { color: white; background-color: green; }");
                        client.print(".off { color: white; background-color: red; }");
                        client.print("a { display: inline-block; margin-top: 20px; font-size: 1.2em; padding: 10px 20px; color: white; text-decoration: none; border-radius: 5px; }");
                        client.print(".link-on { background-color: green; }");
                        client.print(".link-off { background-color: red; }");
                        client.print("</style></head>");
                        client.print("<body>");
                        client.print("<h1>ESP32-S3 LED Control (GPIO18)</h1>");
                        
                        // Display LED state
                        if (ledState) {
                            client.print("<div class='status on'>LED ON</div>");
                            client.print("<a href=\"/L\" class='link-off'>Turn LED OFF</a>");
                        } else {
                            client.print("<div class='status off'>LED OFF</div>");
                            client.print("<a href=\"/H\" class='link-on'>Turn LED ON</a>");
                        }
                        
                        client.print("</body></html>");
                        client.println();  // End of response
                        break;  // Exit the loop after sending the response
                    } else {
                        currentLine = "";  // Clear the line for the next request
                    }
                } else if (c != '\r') {
                    currentLine += c;  // Add character to the current line (ignore carriage return)
                }

                // Check the HTTP request for "/H" (turn LED on) or "/L" (turn LED off)
                if (currentLine.endsWith("GET /H")) {
                    digitalWrite(18, HIGH);  // Turn the LED on
                    ledState = true;         // Update ledState to reflect the LED is on
                    Serial.println("LED ON"); // Print to Serial Monitor
                }
                if (currentLine.endsWith("GET /L")) {
                    digitalWrite(18, LOW);   // Turn the LED off
                    ledState = false;        // Update ledState to reflect the LED is off
                    Serial.println("LED OFF"); // Print to Serial Monitor
                }
            }
        }
        // Close the connection
        client.stop();
        Serial.println("Client Disconnected.");
    }
}
