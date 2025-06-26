#ifndef __DRIVER_RGBMATRIX_H
#define __DRIVER_RGBMATRIX_H
#include "RGBMatrixConfig.h"

#if defined CONFIG_SUPPORT_PICO

#include "pico/stdlib.h"

#define      R1 2
#define	     R1_HIGH		      gpio_put(R1, 1)
#define	     R1_LOW	              gpio_put(R1, 0)
		     
#define      G1 3
#define	     G1_HIGH		      gpio_put(G1, 1)
#define	     G1_LOW	              gpio_put(G1, 0)
					              
#define      B1 4                 
#define	     B1_HIGH	          gpio_put(B1, 1)
#define	     B1_LOW	              gpio_put(B1, 0)
					              
#define      R2 5                 
#define	     R2_HIGH	          gpio_put(R2, 1)
#define	     R2_LOW	              gpio_put(R2, 0)
					              
#define      G2 8                 
#define	     G2_HIGH	          gpio_put(G2, 1)
#define	     G2_LOW	              gpio_put(G2, 0)
					              
#define      B2 9                 
#define	     B2_HIGH	          gpio_put(B2, 1)
#define	     B2_LOW	              gpio_put(B2, 0)
					              
#define      A 10                 
#define	     A_HIGH		          gpio_put(A, 1)
#define	     A_LOW	              gpio_put(A, 0)
					              
#define      B 16                 
#define	     B_HIGH		          gpio_put(B, 1)
#define	     B_LOW	              gpio_put(B, 0)
					              
#define      C 18                 
#define	     C_HIGH		          gpio_put(C, 1)
#define	     C_LOW	              gpio_put(C, 0)
					              
#define      D 20                 
#define	     D_HIGH		          gpio_put(D, 1)
#define	     D_LOW	              gpio_put(D, 0)
					              
#define      E 22                 
#define	     E_HIGH		          gpio_put(E, 1)
#define      E_LOW	              gpio_put(E, 0)
					              
#define      CLK 11               
#define	     CLK_HIGH 	          gpio_put(CLK, 1)
#define	     CLK_LOW	          gpio_put(CLK, 0)
					              
#define      STB 12               
#define	     STB_HIGH 	          gpio_put(STB, 1)
#define	     STB_LOW	          gpio_put(STB, 0)
					              
#define      OE 13                
#define	     OE_HIGH	          gpio_put(OE, 1)
#define	     OE_LOW	              gpio_put(OE, 0)

#define NOP for(int i = 0; i < 1; i++)


void picoRGBMatrixDeviceInit(void);

#endif

#define HIGH_ROW 1
#define LOW_ROW  0

void RGBMatrixDeviceFlush(uint8_t *buf);
void select_area_color(uint8_t start_x,uint8_t start_y,uint8_t end_x,uint8_t end_y,uint8_t color,uint8_t altitude);

#endif
