/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2023 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "usart.h"
#include "gpio.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "RGBMatrix_device.h"
#include "GUI_Paint.h"
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/

/* USER CODE BEGIN PV */

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{
  /* USER CODE BEGIN 1 */
	

//  Paint_Clear(0xff);
	//memset(BlackImage, 0xff, 8192);
  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */
	
  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_USART2_UART_Init();
  /* USER CODE BEGIN 2 */
	//Microsecond delay initialization
	DWT_Init();
	
	//HUB75 initialization
	HUB75_Init();
	 
	//clear screen
	HUB75_Clear();
	printf("Display graphics.\n");
	
	Paint_DrawPoint(44, 9, WHITE, DOT_PIXEL_1X1, DOT_STYLE_DFT);
	Paint_DrawPoint(47, 8, WHITE, DOT_PIXEL_2X2, DOT_STYLE_DFT);
	Paint_DrawPoint(52, 7, WHITE, DOT_PIXEL_3X3, DOT_STYLE_DFT);
	Paint_DrawPoint(59, 6, WHITE, DOT_PIXEL_4X4, DOT_STYLE_DFT);
	
	Paint_DrawLine(20, 12, 20, 32, WHITE, DOT_PIXEL_1X1, LINE_STYLE_SOLID);
	Paint_DrawLine(10, 22, 30, 22, WHITE, DOT_PIXEL_1X1, LINE_STYLE_SOLID);
	Paint_DrawCircle(20, 22, 10, GREEN, DOT_PIXEL_1X1, DRAW_FILL_EMPTY);

	Paint_DrawLine(44, 12, 44, 32, WHITE, DOT_PIXEL_1X1, LINE_STYLE_SOLID);
	Paint_DrawLine(34, 22, 54, 22, WHITE, DOT_PIXEL_1X1, LINE_STYLE_SOLID);
	Paint_DrawCircle(44, 22, 10, BLUE, DOT_PIXEL_1X1, DRAW_FILL_EMPTY);
	
	Paint_DrawLine(42, 38, 64, 64, CYAN, DOT_PIXEL_1X1, LINE_STYLE_DOTTED);
	Paint_DrawLine(0, 64, 22, 38, CYAN, DOT_PIXEL_1X1, LINE_STYLE_DOTTED);
	
	Paint_DrawRectangle(22, 38, 42, 58, RED, DOT_PIXEL_1X1, DRAW_FILL_FULL);
	Paint_DrawCircle(32, 48, 10, PURPLE, DOT_PIXEL_1X1, DRAW_FILL_FULL);
	Paint_DrawRectangle(22, 38, 42, 58, CYAN, DOT_PIXEL_1X1, DRAW_FILL_EMPTY);
	
	
	Paint_DrawRectangle(1, 1, 64, 64, RED, DOT_PIXEL_1X1, DRAW_FILL_EMPTY);
	
	HUB75_Display();
	
	printf("Display string.\n");
	HUB75_Clear();
	Paint_DrawString_EN(5, 0, "Hello", &Font16, BLACK, YELLOW);
	Paint_DrawString_EN(5, 17, "world", &Font12, PURPLE, BLACK);
	Paint_DrawNum(0, 33, 23.456789, &Font16, 3, CYAN, BLACK);
	HUB75_Display();
	
	HUB75_Clear();
	
	printf("Display Chinese and scroll down left.\n");
	Paint_DrawString_CN(0, 10, "Î¢Ñ©µç×Ó", &Font24CN, CYAN, BLACK);
	int scroll = 0;
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {

		RGBMatrixWriteData();
		
		if(scroll>SCROLL_SPEED)
		{
			scroll = 0;
			scrollLeft();
			//scrollRight();
			//scrollUp();
			scrollDown();
		}
		
		scroll++;

    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_ON;
  RCC_OscInitStruct.HSEPredivValue = RCC_HSE_PREDIV_DIV1;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLMUL = RCC_PLL_MUL9;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK)
  {
    Error_Handler();
  }
}

/* USER CODE BEGIN 4 */

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
