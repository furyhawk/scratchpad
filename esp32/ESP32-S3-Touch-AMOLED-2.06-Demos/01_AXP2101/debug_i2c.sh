#!/bin/bash

echo "=== ESP32-S3 AXP2101 I2C Debugging Script ==="

# First, let's check the current I2C configuration
echo "Current I2C configuration:"
grep -E "CONFIG_PMU_I2C_|CONFIG_I2C_MASTER_FREQUENCY" build/config/sdkconfig.h

echo -e "\n=== Common ESP32-S3 Touch AMOLED Board I2C Pins ==="
echo "Option 1 (Most common): SDA=21, SCL=22"
echo "Option 2 (Alternative): SDA=6, SCL=7" 
echo "Option 3 (Your current): SDA=15, SCL=14"

echo -e "\n=== To fix the I2C configuration, try these steps ==="
echo "1. Run: idf.py menuconfig"
echo "2. Navigate to: XPowersLib Configuration"
echo "3. Set PMU SDA GPIO Num to: 21"
echo "4. Set PMU SCL GPIO Num to: 22" 
echo "5. Set Master Frequency to: 50000 (50kHz for more reliability)"
echo "6. Save and rebuild"

echo -e "\n=== Alternative: Manual sdkconfig edit ==="
echo "Add these lines to sdkconfig:"
echo "CONFIG_PMU_I2C_SDA=21"
echo "CONFIG_PMU_I2C_SCL=22"
echo "CONFIG_I2C_MASTER_FREQUENCY=50000"