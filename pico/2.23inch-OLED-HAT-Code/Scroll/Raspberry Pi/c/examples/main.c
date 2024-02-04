#include "test.h"

void  Handler(int signo)
{
    //System Exit
    printf("\r\nHandler:exit\r\n");
    DEV_ModuleExit();

    exit(0);
}

int main(int argc, char *argv[])
{
    // Exception handling:ctrl + c
    signal(SIGINT, Handler);

    if(DEV_ModuleInit() != 0) {
		return -1;
	}
    SSD1305_begin();
    SSD1305_string(0, 0, "Welcome to use", 12, 1); 
    SSD1305_string(0, 12, "Waveshare Electronic", 12, 1); 
    SSD1305_string(0, 24, "2.23inch OLED", 12, 1);
    SSD1305_string(0, 36, "128x32 Pixels", 12, 1);
    SSD1305_Scrolling_Set();
    SSD1305_display();
    SSD1305_Scrolling_Start();

    return 0;
    
}
