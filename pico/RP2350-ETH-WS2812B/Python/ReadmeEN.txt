/*****************************************************************************
* | File      	:   Readme_EN.txt
* | Author      :   
* | Function    :   Help with use
* | Info        :
*----------------
* |	This version:   V1.0
* | Date        :   2024-11-13
* | Info        :   Here is an English version of the documentation for your quick use.
******************************************************************************/
This file is to help you use this routine.
Here is a brief description of the use of this project:

1. Basic information:
This routine is used to test or demonstrate WS2812B on RP2350-ETH.

2. Pin connection:
You can check the pin connection at RP2350-ETH-WS2812B.py, and repeat it here:
DIN    ->    25

3. Basic use:
    1): Press and hold the Bootsel button on the RP2350-ETH board, connect RP2350-ETH to the USB port of the 
        computer through the Type-C USB cable, and then release the button.
        After connecting, the computer will automatically recognize a removable disk 
        
    2): Copy the rp2-pcio2-20240809-v1.24.0.uf2 file from the Uf2 folder in the Python directory to an identified 
        removable disk
    
    3): Update Thonny IDE
        sudo apt upgrade thonny
        
    4): Open Thonny IDE （Click raspberry logo -> Programming -> Thonny Python IDE ）
        select Tools -> Options... -> Interpreter
        select MicroPython(Raspberry Pi Pico  and ttyACM0 port
        
    5): Open the Python/ RP2350-ETH-WS2812B.py file in Thonny IDE
        Then run the current script (little green triangle)
    