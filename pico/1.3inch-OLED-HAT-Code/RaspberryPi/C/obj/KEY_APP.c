/*****************************************************************************
* |	This version:   V1.0
* | Date        :   2019-07-06
* | Info        :   Basic version
*
******************************************************************************/
#include "KEY_APP.h"
#include "OLED_GUI.h"
#include "OLED_Driver.h"
// #include "Debug.h"

// if use 2019-06-20-raspbian-buster
// sudo nano /boot/config.txt
// add:
// gpio=6,19,5,26,13,21,20,16=pu
uint16_t W = WIDTH/10;
uint16_t H = HEIGHT/5;

void Draw_Init(void)
{

    CLEAR(BACK_COLOR);
    
    /* Press */
    DrawRectangle(W*2, H*2, W*3, H*3, WORD_COLOR, DRAW_EMPTY, DOT_PIXEL_DFT);
    DisString_EN(W*2+Font_Offset, H*2+Font_Offset, "P", &Font_KEY, BACK_COLOR, WORD_COLOR);
    
    /* Left */
    DrawRectangle(W*1, H*2, W*2, H*3, WORD_COLOR, DRAW_EMPTY, DOT_PIXEL_DFT);
    DisString_EN(W*1+Font_Offset, H*2+Font_Offset, "L", &Font_KEY, BACK_COLOR, WORD_COLOR);


    /* Right */
    DrawRectangle(W*3, H*2, W*4, H*3, WORD_COLOR, DRAW_EMPTY, DOT_PIXEL_DFT);
    DisString_EN(W*3+Font_Offset, H*2+Font_Offset, "R", &Font_KEY, BACK_COLOR, WORD_COLOR);

    // /* Up */
    DrawRectangle(W*2, H*1, W*3, H*2, WORD_COLOR, DRAW_EMPTY, DOT_PIXEL_DFT);
    DisString_EN(W*2+Font_Offset, H*1+Font_Offset, "U", &Font_KEY, BACK_COLOR, WORD_COLOR);
 

    // /* Down */
    DrawRectangle(W*2, H*3, W*3, H*4, WORD_COLOR, DRAW_EMPTY, DOT_PIXEL_DFT);
    DisString_EN(W*2+Font_Offset, H*3+Font_Offset, "D", &Font_KEY, BACK_COLOR, WORD_COLOR);

    // /* Key1 */
    DrawRectangle(W*7, H*1, W*9, H*2, WORD_COLOR, DRAW_EMPTY, DOT_PIXEL_DFT);
    DisString_EN(W*7+Font_Offset+5, H*1+Font_Offset, "K1", &Font_KEY, BACK_COLOR, WORD_COLOR);
    // DrawRectangle(95, 40, 120, 60, 0x00, DRAW_EMPTY, DOT_PIXEL_DFT);
    // DisString_EN(98, 43, "K1", &Font16, 0x00, 0xff);

    // /* Key2	*/
    DrawRectangle(W*7, H*2, W*9, H*3, WORD_COLOR, DRAW_EMPTY, DOT_PIXEL_DFT);
    DisString_EN(W*7+Font_Offset+5, H*2+Font_Offset, "K2", &Font_KEY, BACK_COLOR, WORD_COLOR);
    // DrawRectangle(95, 60, 120, 80, 0x00, DRAW_EMPTY, DOT_PIXEL_DFT);
    // DisString_EN(98, 63, "K2", &Font16, 0x00, 0xff);

    // /* Key3 */
    DrawRectangle(W*7, H*3, W*9, H*4, WORD_COLOR, DRAW_EMPTY, DOT_PIXEL_DFT);
    DisString_EN(W*7+Font_Offset+5, H*3+Font_Offset, "K3", &Font_KEY, BACK_COLOR, WORD_COLOR);
    // DrawRectangle(95, 80, 120, 100, 0x00, DRAW_EMPTY, DOT_PIXEL_DFT);
    // DisString_EN(98, 83, "K3", &Font16, 0x00, 0xff);
    OLED_Display();
}

void KEY_Listen(void)
{
    Draw_Init();
    for(;;) {
        if(KEY_UP_RD == 0) {
            while(KEY_UP_RD == 0) {
                DrawRectangle(W*2, H*1, W*3, H*2, WORD_COLOR, DRAW_FULL, DOT_PIXEL_DFT);
                OLED_Display();
            }
            Draw_Init();
        }
        if(KEY_DOWN_RD == 0) {
            while(KEY_DOWN_RD == 0) {
                DrawRectangle(W*2, H*3, W*3, H*4, WORD_COLOR, DRAW_FULL, DOT_PIXEL_DFT);
                OLED_Display();
            }
            Draw_Init();
        }
        if(KEY_LEFT_RD == 0) {
            while(KEY_LEFT_RD == 0) {
                DrawRectangle(W*1, H*2, W*2, H*3, WORD_COLOR, DRAW_FULL, DOT_PIXEL_DFT);
                OLED_Display();
            }
            Draw_Init();
        }
        if(KEY_RIGHT_RD == 0) {
            while(KEY_RIGHT_RD == 0) {
                DrawRectangle(W*3, H*2, W*4, H*3, WORD_COLOR, DRAW_FULL, DOT_PIXEL_DFT);
                OLED_Display();
            }
            Draw_Init();
        }
        if(KEY_PRESS_RD == 0) {
            while(KEY_PRESS_RD == 0) {
                DrawRectangle(W*2, H*2, W*3, H*3, WORD_COLOR, DRAW_FULL, DOT_PIXEL_DFT);
                OLED_Display();
            }
            Draw_Init();
        }
        if(KEY1_RD == 0) {
            while(KEY1_RD == 0) {
                DrawRectangle(W*7, H*1, W*9, H*2, WORD_COLOR, DRAW_FULL, DOT_PIXEL_DFT);
                OLED_Display();
            }
            Draw_Init();
        }
        if(KEY2_RD == 0) {
            while(KEY2_RD == 0) {
                DrawRectangle(W*7, H*2, W*9, H*3, WORD_COLOR, DRAW_FULL, DOT_PIXEL_DFT);
                OLED_Display();
            }
            Draw_Init();
        }
        if(KEY3_RD == 0) {
            while(KEY3_RD == 0) {
                DrawRectangle(W*7, H*3, W*9, H*4, WORD_COLOR, DRAW_FULL, DOT_PIXEL_DFT);
                OLED_Display();
            }
            Draw_Init();
        }
    }
}