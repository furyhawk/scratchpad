#include "RGBMatrix_device.h"

	
uint8_t LED_Buffer[LED_Width * LED_Height];
UWORD i=0,j=0;

/**
 * Initialization routine.
 * You might need to enable access to DWT registers on Cortex-M7
 *   DWT->LAR = 0xC5ACCE55
 */
void DWT_Init(void)
{
    if (!(CoreDebug->DEMCR & CoreDebug_DEMCR_TRCENA_Msk)) {
        CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
        DWT->CYCCNT = 0;
        DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
    }
}

/**
 * Delay routine itself.
 * Time is in microseconds (1/1000000th of a second), not to be
 * confused with millisecond (1/1000th).
 *
 * No need to check an overflow. Let it just tick :)
 *
 * @param uint32_t us  Number of microseconds to delay for
 */
void DWT_Delay(uint32_t us) // microseconds
{
    uint32_t startTick = DWT->CYCCNT,
             delayTicks = us * (SystemCoreClock/1000000);

    while (DWT->CYCCNT - startTick < delayTicks);
}


void HUB75E_DelayUs(int us) {
	DWT_Delay(us);
}

/**
 * HUB75 Initialization.
 * Give the buffer address to the GUI
 *  
 */
void HUB75_Init()
{
	Paint_NewImage(LED_Buffer);
}

/**
 * RGBMatrixWriteData.
 * Write graphics like a monitor.
 *  
 */
void RGBMatrixWriteData()
{
	for (j=0; j < 32 ; j++) {
		for (i=0; i < LED_Width; i++) {								
			RGB_R1((LED_Buffer[i +(j * LED_Width)] & 0x01));
			RGB_G1((LED_Buffer[i +(j * LED_Width)] & 0x02));
			RGB_B1((LED_Buffer[i +(j * LED_Width)] & 0x04));
			
			RGB_R2((LED_Buffer[i +((j+32) * LED_Width)] & 0x01));
			RGB_G2((LED_Buffer[i +((j+32) * LED_Width)] & 0x02));
			RGB_B2((LED_Buffer[i +((j+32) * LED_Width)] & 0x04));
			
			RGB_CLK(0); //data input
			RGB_CLK(1); 
		}
		
		RGB_A((j & 0x1));
		RGB_B((j & 0x2));
		RGB_C((j & 0x4));
		RGB_D((j & 0x8));
		RGB_E((j & 0x10));
		
		RGB_LAT(1);
		RGB_LAT(0);
		
		RGB_OE(0);
		HUB75E_DelayUs(120);
		RGB_OE(1);
	
	}
}

/**
 * HUB75_Display
 * Continuously dynamically refresh 200 times
 *  
 */
void HUB75_Display()
{
	for(UBYTE i;i < 200;i++)
	{
		RGBMatrixWriteData();
	}
}

/**
 * HUB75_Clear
 * Set all cache areas to 0
 *  
 */
void HUB75_Clear()
{
	 memset(LED_Buffer, 0, LED_Width * LED_Height);
}

/**
 * scrollRight
 * All pixels scroll right
 *  
 */
void scrollRight() {
		UBYTE tempBuffer[LED_Height];
		UWORD row ,col;
		// Save the data of the first column
		for (row = 0; row < LED_Height; row++) {
        tempBuffer[row] = LED_Buffer[(row * LED_Width) + 0];
    }
				
		// Shift data in each column right
    for (col  = 0; col  < LED_Width - 1; col++) {
        for (row = 0; row < LED_Height; row++) {				
            LED_Buffer[(row * LED_Width)+col] = LED_Buffer[((row * LED_Width))+(col + 1)];
																
        }
    }
		
		// Restore the data of the first column to the last column
    for (row = 0; row < LED_Height; row++) {
        LED_Buffer[(row * LED_Width)+(LED_Width - 1)] = tempBuffer[row];
    }
   
}

/**
 * scrollLeft
 * All pixels scroll left
 *  
 */
void scrollLeft() {
		UBYTE tempBuffer[LED_Height];
		UWORD row ,col;
	
	 // Save the data of the last column
		 for (row = 0; row < LED_Height; row++) {
        tempBuffer[row] = LED_Buffer[(row * LED_Width) + LED_Width - 1];
    }
		 
		// Shift data in each column left
    for (col  = LED_Width - 1; col > 0; col--) {
        for (row = 0; row < LED_Height; row++) {				
            LED_Buffer[(row * LED_Width) + col] = LED_Buffer[((row * LED_Width))+(col - 1)];
																
        }
    }
		
		 // Restore the data of the last column to the first column
    for (row = 0; row < LED_Height; row++) {
        LED_Buffer[(row * LED_Width)] = tempBuffer[row];
    }

   
}

/**
 * scrollDown
 * All pixels scroll down
 *  
 */
void scrollDown() {
		UBYTE tempBuffer[LED_Width];
		UWORD row ,col;
		//Save the last row of data
		for (col = 0; col < LED_Width ; col++) {
        tempBuffer[col] = LED_Buffer[col];
    }
		//Move each row of data down
    for (row  = 0; row < LED_Height - 1; row++) {
        for (col = 0; col < LED_Width; col++) {				
            LED_Buffer[(row * LED_Width)+col] = LED_Buffer[((row + 1) * LED_Width)+col];
																
        }
    }
		
		// Restore the data of the last row to the first row
    for (col = 0; col < LED_Width; col++) {
        LED_Buffer[((LED_Height-1) * LED_Width) + col] = tempBuffer[col];
    }

}

/**
 * scrollUp
 * All pixels scroll up
 *  
 */
void scrollUp() {
	
		UBYTE tempBuffer[LED_Width];
		UWORD row ,col;
		//Save the first row of data
		for (col = 0; col < LED_Width ; col++) {
        tempBuffer[col] = LED_Buffer[(( LED_Height - 1) * LED_Width) + col];
    }
		//Move every bit of data up
    for (row  =  LED_Height - 1; row > 0; row--) {
        for (col = 0; col < LED_Width; col++) {				
            LED_Buffer[(row * LED_Width)+col] = LED_Buffer[((row - 1) * LED_Width)+col];
																
        }
    }
		
		// Restore data from the first row to the last row
    for (col = 0; col < LED_Width; col++) {
        LED_Buffer[col] = tempBuffer[col];
    }
		
}

