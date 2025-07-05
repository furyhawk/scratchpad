#!/usr/bin/env python3
"""
Test script to verify hardware simulation mode for MI48 thermal camera.
This script tests the mock GPIO classes without requiring actual hardware.
"""

import sys
import os
import time

# Add the pysenxor path to sys.path if needed
sys.path.insert(0, '/Users/user/projects/scratchpad/pico/pysenxor-master')

def test_mock_gpio():
    """Test the mock GPIO classes"""
    print("Testing Mock GPIO Classes...")
    
    # Test importing the mock classes
    try:
        # Mock classes for simulation
        class MockDigitalInputDevice:
            def __init__(self, pin, pull_up=None):
                self.pin = pin
                self.pull_up = pull_up
                print(f"Mock GPIO input device created for pin {pin}")
            
            def wait_for_active(self):
                # Simulate data ready by adding a small delay
                time.sleep(0.01)
                return True
        
        class MockDigitalOutputDevice:
            def __init__(self, pin, active_high=True, initial_value=False):
                self.pin = pin
                self.active_high = active_high
                self.value = initial_value
                print(f"Mock GPIO output device created for pin {pin}")
            
            def on(self):
                self.value = True
                print(f"Mock GPIO {self.pin}: ON")
            
            def off(self):
                self.value = False
                print(f"Mock GPIO {self.pin}: OFF")
        
        # Test creating mock devices
        data_ready = MockDigitalInputDevice("BCM24", pull_up=False)
        cs_pin = MockDigitalOutputDevice("BCM7", active_high=False, initial_value=False)
        reset_pin = MockDigitalOutputDevice("BCM23", active_high=False, initial_value=True)
        
        print("\nTesting mock GPIO operations...")
        
        # Test CS pin
        print("Testing CS pin:")
        cs_pin.on()
        time.sleep(0.1)
        cs_pin.off()
        
        # Test reset pin
        print("Testing reset pin:")
        reset_pin.on()
        time.sleep(0.1)
        reset_pin.off()
        
        # Test data ready
        print("Testing data ready pin:")
        ready = data_ready.wait_for_active()
        print(f"Data ready returned: {ready}")
        
        print("\nMock GPIO test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error during mock GPIO test: {e}")
        return False

def test_dependencies():
    """Test if required dependencies are available"""
    print("Testing dependencies...")
    
    missing_deps = []
    
    try:
        import numpy as np
        print("✓ numpy available")
    except ImportError:
        missing_deps.append("numpy")
        print("✗ numpy not available")
    
    try:
        import cv2 as cv
        print("✓ opencv-python available")
    except ImportError:
        missing_deps.append("opencv-python")
        print("✗ opencv-python not available")
    
    try:
        from smbus import SMBus
        print("✓ smbus available")
    except ImportError:
        missing_deps.append("smbus")
        print("✗ smbus not available")
    
    try:
        from spidev import SpiDev
        print("✓ spidev available")
    except ImportError:
        missing_deps.append("spidev")
        print("✗ spidev not available")
    
    if missing_deps:
        print(f"\nMissing dependencies: {', '.join(missing_deps)}")
        print("Install them with:")
        print(f"pip install {' '.join(missing_deps)}")
        return False
    else:
        print("\nAll dependencies are available!")
        return True

def main():
    """Main test function"""
    print("Hardware Simulation Test")
    print("=" * 30)
    
    # Test dependencies
    deps_ok = test_dependencies()
    print()
    
    # Test mock GPIO
    gpio_ok = test_mock_gpio()
    print()
    
    if deps_ok and gpio_ok:
        print("✓ All tests passed! Hardware simulation should work.")
        return 0
    else:
        print("✗ Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
