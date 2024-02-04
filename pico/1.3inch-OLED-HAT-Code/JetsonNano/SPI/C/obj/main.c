#include <stdlib.h>     //exit()
#include <signal.h>     //signal()
#include <stdio.h>
#include <time.h>
#include "GUI_Paint.h"
#include "image.h"
#include "DEV_Config.h"
#include <unistd.h>

void  Handler(int signo)
{
    //System Exit
    printf("\r\nHandler:Program  End\r\n");
    DEV_ModuleExit();

    exit(0);
}

char value[10] = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'};
int main(int argc, char **argv)
{
    int i = -1;
    time_t now;
    struct tm *timenow;
    
    // Exception handling:ctrl + c
    signal(SIGINT, Handler);
    
 
	if(DEV_ModuleInit()==1)
		return 1;
    printf("OLED example. Press Ctrl + C to exit.\n");

    SH1106_begin();
    Paint_NewImage(WIDTH, HEIGHT,0,WHITE);
	Paint_Clear(BLACK);
    Paint_SetRotate(180);
    
    Paint_DrawString_CN(0,0, "Î¢Ñ©µç×Ó",  &Font24CN, 0x0000, 0xffff);
    SH1106_display();
    DEV_Delay_ms(2000);
    Paint_Clear(BLACK);
    while(1)
    {
        //printf("time %d:%d:%d\r\n",value[timenow->tm_hour],value[timenow->tm_min],value[timenow->tm_sec]);
        time(&now);
        timenow = localtime(&now);

        Paint_DrawBitmap(0, 2, Signal816, 16, 8, WHITE); 
        Paint_DrawBitmap(22, 2, Msg816, 16, 8, WHITE); 
        Paint_DrawBitmap(44, 2, Bluetooth88, 8, 8, WHITE); 
        Paint_DrawBitmap(66, 2, GPRS88, 8, 8, WHITE); 
        Paint_DrawBitmap(88, 2, Alarm88, 8, 8, WHITE); 
        Paint_DrawBitmap(110, 2, Bat816, 16, 8, WHITE); 
        Paint_DrawString_EN(0, 52, "MUSIC", &Font12, 0x0000, WHITE);
        Paint_DrawString_EN(95, 52, "MENU", &Font12, 0x0000, WHITE);
        

        Paint_DrawChar(15,  23, value[timenow->tm_hour / 10], &Font24, 0x0000, WHITE);
        Paint_DrawChar(31, 23, value[timenow->tm_hour % 10], &Font24, 0x0000, WHITE);
        Paint_DrawChar(55, 23, ':', &Font24, 0x0000, WHITE);
        Paint_DrawChar(79, 23, value[timenow->tm_min / 10], &Font24, 0x0000, WHITE);
        Paint_DrawChar(95, 23, value[timenow->tm_min % 10], &Font24, 0x0000, WHITE);
        
        if(i != value[timenow->tm_min % 10]){
            SH1106_display();
        }
        i = value[timenow->tm_min % 10];
        
        sleep(2);
    }
    DEV_ModuleExit();
    exit(0);
    return 0;
}

