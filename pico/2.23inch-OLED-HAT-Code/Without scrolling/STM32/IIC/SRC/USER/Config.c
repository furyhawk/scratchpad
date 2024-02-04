/**
  ******************************************************************************
  * @file    xxx.c 
  * @author  Waveshare Team
  * @version 
  * @date    xx-xx-2019
  * @brief   xxxxx.
  ******************************************************************************
  * @attention
  *
  * THE PRESENT FIRMWARE WHICH IS FOR GUIDANCE ONLY AIMS AT PROVIDING CUSTOMERS
  * WITH CODING INFORMATION REGARDING THEIR PRODUCTS IN ORDER FOR THEM TO SAVE
  * TIME. AS A RESULT, WAVESHARE SHALL NOT BE HELD LIABLE FOR ANY
  * DIRECT, INDIRECT OR CONSEQUENTIAL DAMAGES WITH RESPECT TO ANY CLAIMS ARISING
  * FROM THE CONTENT OF SUCH FIRMWARE AND/OR THE USE MADE BY CUSTOMERS OF THE
  * CODING INFORMATION CONTAINED HEREIN IN CONNECTION WITH THEIR PRODUCTS.
  *
  ******************************************************************************
  */

/* Includes ------------------------------------------------------------------*/
#include "LIB_Config.h"

/* Private typedef -----------------------------------------------------------*/
/* Private define ------------------------------------------------------------*/

/* Private macro -------------------------------------------------------------*/

/* Private macro -------------------------------------------------------------*/
/* Private variables ---------------------------------------------------------*/
/* Private function prototypes -----------------------------------------------*/

static void device_init(void);
static void driver_init(void);
static void port_init(void);

#ifdef INTERFACE_4WIRE_SPI
static void spi2_init(void);
#endif
/* Private functions ---------------------------------------------------------*/


/**
  * @brief  System initialization.
  * @param  None
  * @retval  None
  */
void system_init(void)
{
	RCC_ClocksTypeDef tRCC;
	
	RCC_GetClocksFreq(&tRCC); 
	delay_init(tRCC.HCLK_Frequency);
	
    device_init();
    driver_init();
}


/**
 * @brief 
 * @param 
 * @retval 
 */
static void device_init(void)
{
	port_init();
#ifdef INTERFACE_4WIRE_SPI
	spi2_init();
#endif
	iic_init();
}

/**
  * @brief  driver initialization.
  * @param  None
  * @retval None
  */
static void driver_init(void)
{
	ssd1305_init();
}


static void port_init(void) 
{
	GPIO_InitTypeDef tGPIO;
	
	RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA | RCC_APB2Periph_GPIOB | RCC_APB2Periph_GPIOC | RCC_APB2Periph_AFIO, ENABLE); 
	
	/*----------------------------------------------------------------------------------*/
	//SPI
#ifdef INTERFACE_4WIRE_SPI
	tGPIO.GPIO_Pin = SSD1305_CLK_PIN | SSD1305_DIN_PIN;	 //SCK  MISO	MOSI		 		 
	tGPIO.GPIO_Speed = GPIO_Speed_50MHz;
	tGPIO.GPIO_Mode = GPIO_Mode_AF_PP; 	
	GPIO_Init(GPIOB, &tGPIO);
#endif
	
	
	/*----------------------------------------------------------------------------------*/
	
	//SSD1305 OLED
	tGPIO.GPIO_Pin = SSD1305_CS_PIN;     // CS				 
	tGPIO.GPIO_Speed = GPIO_Speed_50MHz;
	tGPIO.GPIO_Mode = GPIO_Mode_Out_PP;	
	GPIO_Init(GPIOB, &tGPIO);
	
	tGPIO.GPIO_Pin = SSD1305_RES_PIN | SSD1305_DC_PIN;     // RES D/C 				 
	tGPIO.GPIO_Speed = GPIO_Speed_50MHz;
	tGPIO.GPIO_Mode = GPIO_Mode_Out_PP;	
	GPIO_Init(GPIOC, &tGPIO);
	
	
	/*----------------------------------------------------------------------------------*/
	//I2C
#ifdef INTERFACE_IIC
	tGPIO.GPIO_Pin = IIC_SCL_PIN | IIC_SDA_PIN;
	tGPIO.GPIO_Mode = GPIO_Mode_Out_PP; //GPIO_Mode_Out_PP
	tGPIO.GPIO_Speed = GPIO_Speed_2MHz;
	GPIO_Init(GPIOB, &tGPIO);
#endif
	/*----------------------------------------------------------------------------------*/
}

/**
  * @brief  This function handles SysTick Handler.
  * @param  None
  * @retval None
  */
void SysTick_Handler(void)
{
	;
}

/**
  * @brief  SPI initialization.
  * @param  None
  * @retval None
  */
#ifdef INTERFACE_4WIRE_SPI
static void spi2_init(void)
{
	SPI_InitTypeDef tSPI;

	RCC_APB1PeriphClockCmd(RCC_APB1Periph_SPI2, ENABLE);

	tSPI.SPI_Direction = SPI_Direction_2Lines_FullDuplex;
	tSPI.SPI_Mode = SPI_Mode_Master;		
	tSPI.SPI_DataSize = SPI_DataSize_8b;		
	tSPI.SPI_CPOL = SPI_CPOL_High;		
	tSPI.SPI_CPHA = SPI_CPHA_2Edge;	
	tSPI.SPI_NSS = SPI_NSS_Soft;		
	tSPI.SPI_BaudRatePrescaler = SPI_BaudRatePrescaler_8;		
	tSPI.SPI_FirstBit = SPI_FirstBit_MSB;	
	tSPI.SPI_CRCPolynomial = 7;	
	SPI_Init(SPI2, &tSPI);  
 
	SPI_Cmd(SPI2, ENABLE); 
}
#endif



/*-------------------------------END OF FILE-------------------------------*/
