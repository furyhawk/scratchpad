#include <stdio.h>      //printf()
#include <stdlib.h>     //exit()
#include <signal.h>

#include "DEV_Config.h"
#include "TCS34087.h"

UWORD r,g,b,c;
UWORD cpl,lux,k;

void  Handler(int signo)
{
    //System Exit
    printf("\r\nHandler:Program stop\r\n");     
    DEV_ModuleExit();
    exit(0);
}

int main(int argc, char **argv)
{
    RGB rgb;
    UDOUBLE RGB888=0;
    UWORD   RGB565=0;
	if (DEV_ModuleInit() != 0){
        exit(0);
    }
    
    // Exception handling:ctrl + c
    signal(SIGINT, Handler);
    
    if(TCS34087_Init() != 0){
        printf("TCS34087 initialization error!!\r\n");
        DEV_ModuleExit();
        exit(0);
    } 
    printf("TCS34087 initialization success!!\r\n");

    while(1){    
        rgb=TCS34087_Get_RGBData();
        RGB888=TCS34087_GetRGB888(rgb);
        RGB565=TCS34087_GetRGB565(rgb);
        
        printf(" RGB888 :R=%d   G=%d  B=%d   RGB888=0X%X  RGB565=0X%X  C=%d LUX=%d ", (RGB888>>16), \
                (RGB888>>8) & 0xff, (RGB888) & 0xff, RGB888, RGB565, rgb.C,TCS34087_Get_Lux(rgb));
                
        if(TCS34087_GetLux_Interrupt() == 1){
            printf("Lux_Interrupt = 1\r\n");
        }else{
            printf("Lux_Interrupt = 0\r\n");
        }
     

        
	}

	DEV_ModuleExit();
    return 0; 
}