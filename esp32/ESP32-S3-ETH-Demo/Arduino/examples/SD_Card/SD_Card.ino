/**
 ******************************************************************************
 * @file     SD_Card.ino
 * @author   Kaloha
 * @version  V1.0
 * @date     2024-10-24
 * @brief    SD card read/write and directory scan experiment
 * @license  MIT
 * @copyright Copyright (c) 2024, Waveshare Electronics CO.,LTD
 ******************************************************************************
 * 
 * Experiment Objective: Learn how to read from, write to, and scan files on an SD card.
 *
 * Hardware Resources and Pin Assignment: 
 * 1. SD Card Interface --> ESP32-S3-ETH Module
 *    Pins used: {MISO: 5, MOSI: 6, SCLK: 7, CS: 4}
 *
 * Experiment Phenomenon:
 * 1. The SD card will be initialized, and if successful, a file named "waveshare.txt" will be created.
 * 2. The file will contain the text "Hello world from Waveshare".
 * 3. The root directory of the SD card will be scanned, and all files found will be printed to the serial console.
 * 4. The "waveshare.txt" file will be opened, its contents read and printed to the serial console.
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


#include <Arduino.h>
#include <SPI.h>
#include <SD.h>

#define SD_MISO_PIN 5
#define SD_MOSI_PIN 6
#define SD_SCLK_PIN 7
#define SD_CS_PIN   4

uint32_t cardSize;

void setup() {
    Serial.begin(115200);

    pinMode(SD_MISO_PIN, INPUT_PULLUP);
    SPI.begin(SD_SCLK_PIN, SD_MISO_PIN, SD_MOSI_PIN, SD_CS_PIN);

    if (SD.begin(SD_CS_PIN)) {
        Serial.println("SDCard MOUNT SUCCESS");
    } else {
        Serial.println("SDCard MOUNT FAIL");
        delay(500);
        return;
    }

    cardSize = SD.cardSize() / (1024 * 1024);
    Serial.printf("SDCard Size: %d MB\n", cardSize);

    // Create and write to the file
    writeFileToSD();

    // Scan and print the file list in the SD card root directory
    listFilesOnSD();

    // Open and read the contents of the waveshare.txt file
    readFileFromSD("/waveshare.txt");
}

void loop() {
    delay(2000); // Allow the CPU to perform other tasks
}

// Function to write to the file
void writeFileToSD() {
    File file = SD.open("/waveshare.txt", FILE_WRITE); // Create or open the file

    if (!file) {
        Serial.println("Failed to open file for writing");
        return;
    }

    // Write "Hello world from Waveshare" to the file
    file.println("Hello world from Waveshare");

    Serial.println("File written successfully");
    file.close(); // Close the file
}

// List all files in the root directory of the SD card
void listFilesOnSD() {
    File root = SD.open("/");

    if (!root) {
        Serial.println("Failed to open root directory");
        return;
    }

    Serial.println("Files in root directory:");
    File file = root.openNextFile();
    while (file) {
        Serial.print("  ");
        Serial.println(file.name());
        file = root.openNextFile();  // Get the next file
    }

    root.close(); // Close the root directory
}

// Read the contents of the waveshare.txt file
void readFileFromSD(const char *filePath) {
    File file = SD.open(filePath);

    if (!file) {
        Serial.printf("Failed to open file %s for reading\n", filePath);
        return;
    }

    Serial.printf("Reading from %s:\n", filePath);
    while (file.available()) {
        Serial.write(file.read());  // Read and print content byte by byte
    }

    file.close(); // Close the file
}
