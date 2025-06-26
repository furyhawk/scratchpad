#include "driver_RGBMatrix.h"
unsigned char display_rgb[Matrix_ROWS_SHOW][Matrix_COLS];
// uint8_t display_rgb_count = 0;
static uint8_t CS_cnt = 0;
uint8_t UpdateVideoMemoryFlag;
extern uint8_t autoLightFlag;
uint8_t UpdateVideoMemory = 0;
#if defined CONFIG_SUPPORT_PICO
void picoRGBMatrixDeviceInit(void)
{
        
    gpio_init(R1);
    gpio_init(G1);
    gpio_init(B1);
    gpio_init(R2);
    gpio_init(G2);
    gpio_init(B2);

    gpio_init(A);
    gpio_init(B);
    gpio_init(C);
    gpio_init(D);
    gpio_init(E);

    
    gpio_init(CLK);
    gpio_init(STB);
    gpio_init(OE);


    gpio_set_dir(R1, GPIO_OUT);
    gpio_set_dir(G1, GPIO_OUT);
    gpio_set_dir(B1, GPIO_OUT);
    gpio_set_dir(R2, GPIO_OUT);
    gpio_set_dir(G2, GPIO_OUT);
    gpio_set_dir(B2, GPIO_OUT);
    
    gpio_set_dir(A, GPIO_OUT);
    gpio_set_dir(B, GPIO_OUT);
    gpio_set_dir(C, GPIO_OUT);
    gpio_set_dir(D, GPIO_OUT);
    gpio_set_dir(E,GPIO_OUT);
    gpio_set_dir(CLK, GPIO_OUT);
    gpio_set_dir(STB, GPIO_OUT);
    gpio_set_dir(OE, GPIO_OUT);
    
    OE_HIGH;
    STB_LOW;
    CLK_LOW;

    int MaxLed = 64;

    int C12[16] = {0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1};
    int C13[16] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0};

    for (int l = 0; l < MaxLed; l++)
    {
        int y = l % 16;
        R1_LOW;
        G1_LOW;
        B1_LOW;
        R2_LOW;
        G2_LOW;
        B2_LOW;
        if (C12[y] == 1)
        {
            R1_HIGH;
            G1_HIGH;
            B1_HIGH;
            R2_HIGH;
            G2_HIGH;
            B2_HIGH;
        }
        if (l > MaxLed - 12)
        {
            STB_HIGH;
        }
        else
        {
            STB_LOW;
        }
        CLK_HIGH;
        sleep_us(2);
        CLK_LOW;
    }
    STB_LOW;
    CLK_LOW;

    // Send Data to control register 12
    for (int l = 0; l < MaxLed; l++)
    {
        int y = l % 16;
        R1_LOW;
        G1_LOW;
        B1_LOW;
        R2_LOW;
        G2_LOW;
        B2_LOW;
        if (C13[y] == 1)
        {
            R1_HIGH;
            G1_HIGH;
            B1_HIGH;
            R2_HIGH;
            G2_HIGH;
            B2_HIGH;
        }
        if (l > MaxLed - 13)
        {
            STB_HIGH;
        }
        else
        {
            STB_LOW;
        }
        CLK_HIGH;
        sleep_us(2);
        CLK_LOW;
    }
    STB_LOW;
    CLK_LOW;
}
#endif

static void RGBMatrixWriteData(uint8_t high_data,uint8_t low_data,unsigned char display_rgb_count)
{
    uint8_t j;

	uint8_t rgb; 
    for(j = 0; j < 8; j++)
    {
		rgb = display_rgb[CS_cnt][8*display_rgb_count + j];
        CLK_LOW;
        
        R1_LOW;
        G1_LOW;
        B1_LOW;

        R2_LOW;
        G2_LOW;
        B2_LOW;
        if(high_data&0x01)
        {
			if(rgb & 0x04)
                R1_HIGH;
            if(rgb & 0x02)
                G1_HIGH;
            if(rgb & 0x01)
                B1_HIGH;
        }

        if(low_data&0x01)
        {
            if(rgb & 0x40)
                R2_HIGH;
            if(rgb & 0x20)
                G2_HIGH;
            if(rgb & 0x10)
                B2_HIGH;
        }
        high_data>>=1;
        low_data>>=1;

        CLK_HIGH;

    }

}

void RGBMatrixDeviceFlush(uint8_t *buf)
{
    uint8_t i;
    CS_cnt ++;
    if(CS_cnt > (Matrix_ROWS_SHOW -1))
    {
        CS_cnt = 0;
    }  
	UpdateVideoMemory = 1;
    OE_HIGH;
    for(i = 0; i < (Matrix_COLS_BYTE); i++)
    {
        RGBMatrixWriteData(buf[CS_cnt * Matrix_COLS_BYTE + i],buf[(CS_cnt + Matrix_ROWS_SHOW) * Matrix_COLS_BYTE + i ],i);
    }

    if(CS_cnt & 0x01) A_HIGH; else A_LOW;
    if(CS_cnt & 0x02) B_HIGH; else B_LOW;
    if(CS_cnt & 0x04) C_HIGH; else C_LOW;
    if(CS_cnt & 0x08) D_HIGH; else D_LOW;
    if(CS_cnt & 0x10) E_HIGH; else E_LOW;

    STB_HIGH;
    NOP;
    STB_LOW;
	UpdateVideoMemory = 0;
	if(autoLightFlag != 0)
	{
		autoLightFlag = 1;
        
	}
	else
	{
		OE_LOW;
	}  
}

void select_area_color(uint8_t start_x,uint8_t start_y,uint8_t end_x,uint8_t end_y,uint8_t color,uint8_t altitude)
{
    uint8_t i,j;
    if(altitude == HIGH_ROW)
    {
        for(i =start_y;i <= end_y;i++)
        {
            for(j = start_x;j <= end_x;j++)
            {
                display_rgb[i][j] =  (display_rgb[i][j] & 0xF0)|color;
            }
        }
    }
    if(altitude == LOW_ROW)
    {
        for(i =start_y;i <= end_y;i++)
        {
            for(j = start_x;j <= end_x;j++)
            {
                display_rgb[i][j] = (display_rgb[i][j]&0x0F)|(color << 4);
            }
        }
    }
}