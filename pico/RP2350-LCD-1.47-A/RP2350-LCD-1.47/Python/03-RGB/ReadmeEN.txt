/*****************************************************************************
* | File      	:   Readme_EN.txt
* | Author      :   
* | Function    :   Help with use
* | Info        :
*----------------
* |	This version:   V1.0
* | Date        :   2025-03-04
* | Info        :   Here is an English version of the documentation for your quick use.
******************************************************************************/
This file is to help you use this routine.
Here is a brief description of the use of this project:

1. Basic information:
This routine is used to test or demonstrate WS2812B on RP2350-LCD-1.47.

2. Pin connection:
You can check the pin connection at WS2812B.py, and repeat it here:
RGB_IO    ->    22

3. Basic use:
    1): Press and hold the Bootsel button on the RP2350-LCD-1.47 board, connect RP2350-LCD-1.47 to the USB port of the 
        computer through the Type-C USB cable, and then release the button.
        After connecting, the computer will automatically recognize a removable disk
        
    2): Copy the WAVESHARE_RP2350_LCD_1_47.uf2 file from the Uf2 folder in the Python directory to an identified 
        removable disk
    
    3): Update Thonny IDE
        sudo apt upgrade thonny
        
    4): Open Thonny IDE （Click raspberry logo -> Programming -> Thonny Python IDE ）
        select Tools -> Options... -> Interpreter
        select MicroPython(Raspberry Pi Pico  and ttyACM0 port
        
    5): Open the Python/WS2812B.py file in Thonny IDE
        Then run the current script (little green triangle)
    