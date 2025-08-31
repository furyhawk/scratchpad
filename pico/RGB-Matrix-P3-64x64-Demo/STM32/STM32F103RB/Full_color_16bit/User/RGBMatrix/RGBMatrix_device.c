#include "RGBMatrix_device.h"

HUB75_port RGB_Matrix;
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
uint32_t _PM_timerSave;
uint32_t freq = 0;
void HUB75_show()
{
	HAL_TIM_Base_Start_IT(&htim1);
	_PM_timerSave = __HAL_TIM_GET_COUNTER(&htim1); 
}

void HUB75_Init(uint8_t width,uint8_t address_size,uint8_t bitDepth)
{
	RGB_Matrix.tile = 1;
	
	RGB_Matrix.address_size = address_size;
	RGB_Matrix.column_select =  1 << RGB_Matrix.address_size - 1;
	
	RGB_Matrix.width = width;
	
	RGB_Matrix.height = (2 << RGB_Matrix.address_size) * abs(RGB_Matrix.tile);

	RGB_Matrix.min_Period = HUB75_MIN_PERIOD;
	RGB_Matrix.timer_Period = RGB_Matrix.min_Period;
	
	RGB_Matrix.bitDepth=bitDepth;
	
	RGB_Matrix.plane = RGB_Matrix.bitDepth; // Take a four-bit color. Due to processor speed issues, if it is too high, flickering will occur.

}




uint16_t initialRedBit = 0x0800 << 1, initialGreenBit = 0x0040 << 1, initialBlueBit = 0x0001 << 1;
//Take the four higher color RGB 11110 111100 11110
void RGBMatrixWrite_565Data(uint8_t row , uint8_t plane){
	
	if(plane == 0){
		initialRedBit   = 0x0800 << 1 ;
		initialGreenBit = 0x0040 << 1 ;
		initialBlueBit	= 0x0001 << 1 ;
	}
			
			uint16_t *upperSrc, *lowerSrc; // Canvas scanline pointers
			int16_t srcIdx;
			int8_t srcInc;
	
			for (int8_t tile = abs(RGB_Matrix.tile) - 1; tile >= 0; tile--) {
				if(RGB_Matrix.tile < 0)
				{
					lowerSrc = RGB_Matrix.BlackImage + (tile * RGB_Matrix.width * (RGB_Matrix.height / 2)) + RGB_Matrix.width * ((RGB_Matrix.height / 2) - 1 - row);
					upperSrc = lowerSrc + RGB_Matrix.width * (RGB_Matrix.height / 2); 
					srcIdx = RGB_Matrix.width - 1;                                      
					srcInc = -1;
				}
				else
				{
					upperSrc = RGB_Matrix.BlackImage + (tile * RGB_Matrix.width * (RGB_Matrix.height / 2)) + (RGB_Matrix.width * row);
					lowerSrc = upperSrc + RGB_Matrix.width * (RGB_Matrix.height / 2); 
					srcIdx = 0;                                     
					srcInc = 1;
				}
			
			
			for(uint16_t x = 0; x < RGB_Matrix.width; x++, srcIdx += srcInc)
			{

				if(upperSrc[srcIdx] & initialRedBit)
					R1_GPIO_Port->BSRR = R1_Pin;
				else
					R1_GPIO_Port->BSRR = (uint32_t)R1_Pin << 16u;
				
				if(upperSrc[srcIdx] & initialGreenBit)
					G1_GPIO_Port->BSRR = G1_Pin;
				else
					G1_GPIO_Port->BSRR = (uint32_t)G1_Pin << 16u;
				
				if(upperSrc[srcIdx] & initialBlueBit)
					B1_GPIO_Port->BSRR = B1_Pin;
				else
					B1_GPIO_Port->BSRR = (uint32_t)B1_Pin << 16u;
				
				if(lowerSrc[srcIdx] & initialRedBit)
					R2_GPIO_Port->BSRR = R2_Pin;
				else
					R2_GPIO_Port->BSRR = (uint32_t)R2_Pin << 16u;
				
				if(lowerSrc[srcIdx] & initialGreenBit)
					G2_GPIO_Port->BSRR = G2_Pin;
				else
					G2_GPIO_Port->BSRR = (uint32_t)G2_Pin << 16u;
				
				if(lowerSrc[srcIdx] & initialBlueBit)
					B2_GPIO_Port->BSRR = B2_Pin;
				else
					B2_GPIO_Port->BSRR = (uint32_t)B2_Pin << 16u;

				
				 CLK_GPIO_Port->BSRR = (uint32_t)CLK_Pin << 16u ;

				 CLK_GPIO_Port->BSRR = CLK_Pin;

					
			} //end x
		}// end tile
				initialRedBit <<= 1;
				initialGreenBit <<= 1;
				initialBlueBit <<= 1;
			
			

	
}

//timer interrupt callback
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim)
{
    if(htim->Instance == htim1.Instance)
    {

			OE_GPIO_Port->BSRR = OE_Pin;

			LAT_GPIO_Port->BSRR = (uint32_t)LAT_Pin << 16u;
			LAT_GPIO_Port->BSRR = LAT_Pin;
			
			HAL_TIM_Base_Stop_IT(&htim1);
			//uint8_t prevPlane = plane;
			//printf("prevPlane:%d\n",prevPlane);
			LAT_GPIO_Port->BSRR = (uint32_t)LAT_Pin << 16u;
			
			if(RGB_Matrix.plane == 0)
			{
				if(RGB_Matrix.column_select & 0x1)
					A_GPIO_Port->BSRR = A_Pin;
				else
					A_GPIO_Port->BSRR = (uint32_t)A_Pin << 16u;
				
				if(RGB_Matrix.column_select & 0x2)
					B_GPIO_Port->BSRR = B_Pin;
				else
					B_GPIO_Port->BSRR = (uint32_t)B_Pin << 16u;
				
				if(RGB_Matrix.column_select & 0x4)
					C_GPIO_Port->BSRR = C_Pin;
				else
					C_GPIO_Port->BSRR = (uint32_t)C_Pin << 16u;
				
				if(RGB_Matrix.column_select & 0x8)
					D_GPIO_Port->BSRR = D_Pin;
				else
					D_GPIO_Port->BSRR = (uint32_t)D_Pin << 16u;
				
				if(RGB_Matrix.column_select & 0x10)
					E_GPIO_Port->BSRR = E_Pin;
				else
					E_GPIO_Port->BSRR = (uint32_t)E_Pin << 16u;
				
			}
			
			if(++RGB_Matrix.plane >= RGB_Matrix.bitDepth)
			{
				RGB_Matrix.plane = 0;
				
				if(++RGB_Matrix.column_select >= (1 << RGB_Matrix.address_size))
				{
					RGB_Matrix.column_select = 0;				
				}		
			}  

			__HAL_TIM_SET_COUNTER(&htim1,0);
			htim1.Instance->ARR = RGB_Matrix.timer_Period << RGB_Matrix.plane;
			
			HAL_TIM_Base_Start_IT(&htim1);
			
			OE_GPIO_Port->BSRR = (uint32_t)OE_Pin << 16u;;
			
			RGBMatrixWrite_565Data(RGB_Matrix.column_select,RGB_Matrix.plane);
	
			if(RGB_Matrix.plane == 0)
			{
				uint32_t elapsed = __HAL_TIM_GET_COUNTER(&htim1) - _PM_timerSave;
				RGB_Matrix.timer_Period = ((RGB_Matrix.timer_Period * 7) + elapsed) / 8;			
				if (RGB_Matrix.timer_Period < RGB_Matrix.min_Period) RGB_Matrix.timer_Period = RGB_Matrix.min_Period;
			}
			
    }
}

uint16_t Wheel(uint8_t WheelPos) {
  if(WheelPos < 16) {
   return ((32 - WheelPos) << 11) |(WheelPos << 5) | 0;
  } else if(WheelPos < 32) {
   WheelPos -= 16;
   return 0 | ((32 - WheelPos) << 5) | WheelPos;
		
  } else {
   WheelPos -= 32;
   return (WheelPos <<11 )| 0 | (32 - WheelPos);
  }
}


