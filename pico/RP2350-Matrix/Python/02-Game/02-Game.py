from QMI8658 import QMI8658
from WS2812 import LEDController
import time

def main():
    # Initialize the IMU
    imu = QMI8658()
    # Initialize RGB LED control pins
    led_ctrl = LEDController()
    
    # Coordinate Description:
    # The program is set so that when the USB port is facing upward,
    # the upper left corner of the matrix is (0,0) and the lower right corner is (7,7)
    # Initial position (5,5)
    x, y = 5, 5
    threshold = 0.15  # Acceleration threshold
    move_delay = 100  # Move interval (ms)
    last_move = time.ticks_ms()
    
    try:
        while True:
            xyz=imu.Read_XYZ()
            
            # X-axis acceleration controls the X direction
            # Y-axis acceleration controls the Y direction
            if time.ticks_diff(time.ticks_ms(), last_move) > move_delay:
                moved = False
                
                # X-axis control (development board tilts up and down)
                if xyz[0] < -threshold:
                    x = min(x + 1, 7)
                    moved = True
                elif xyz[0] > threshold:
                    x = max(x - 1, 0)
                    moved = True
            
                # Y-axis control (development board tilts left and right)
                if xyz[1] > threshold:
                    y = min(y + 1, 7)
                    moved = True
                elif xyz[1] < -threshold:
                    y = max(y - 1, 0)
                    moved = True
                
                if moved:
                    last_move = time.ticks_ms()
            
                    # Update the display
                    led_ctrl.clear()
                    led_ctrl.set_pixel(x, y, (0x00, 0x00, 0xFF))
                    led_ctrl.show()
            
            time.sleep_ms(10)
    
    except KeyboardInterrupt:
        led_ctrl.clear()
        led_ctrl.show()
        print("Program exited")

if __name__ == "__main__":
    main()
