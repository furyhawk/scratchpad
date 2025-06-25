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
This routine has been verified using the corresponding module with Pico, 
you can view the corresponding test routine in the project;

2. Pin connection:
You can check the pin connection at RP2350-LCD-1.47.py, and repeat it here:
RP2350-LCD-1.47
SCLK     ->      10
MOSI     ->      11
MISO     ->      12
D1       ->      13
D2       ->      14
CS       ->      15

3. Basic use:
    1): Press and hold the button on the Pico board, connect Pico to the USB port of the 
        computer through the Micro USB cable, and then release the button.
        After connecting, the computer will automatically recognize a removable disk
        
    2): Copy the WAVESHARE_RP2350_LCD_1_47.uf2  file in the python directory to the recognized 
        removable disk
    
    3): Update Thonny IDE
        sudo apt upgrade thonny
        
    4): Open Thonny IDE （Click raspberry logo -> Programming -> Thonny Python IDE ）
        select Tools -> Options... -> Interpreter
        select MicroPython(Raspberry Pi Pico  and ttyACM0 port
        
    5): Copy this file to python in the Thonny IDE into RP2350-LCD-1.47 and open the RP2350-LCD-1.47 file
        Then run the current script (green triangle)
    