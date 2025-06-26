#include "font.h"
#include "RGBMatrixConfig.h"

void fontChar4X7(uint8_t *frameBuffer,int iX, int iY, char dis_char)
{
	uint8_t i,j,k;
	j=iX/8;//要显示是第几个点阵序号
    k=iX%8;//在第几个bit开始显示
	for(i = iY;i<(iY+7);i++)
	{
		if(k > 0)
		{
			frameBuffer[(Matrix_COLS_BYTE * i) + j] = 
			  (frameBuffer[(Matrix_COLS_BYTE * i) + j]&(0xff>>(8-k))) | (DISPdat4X7[dis_char][i-iY] << k);
			if(j < (Matrix_COLS_BYTE) - 1)
			{
				frameBuffer[(Matrix_COLS_BYTE * i) + (j+1)] =
				  (frameBuffer[(Matrix_COLS_BYTE * i) + (j+1)]&(0xff<<k)) | (DISPdat4X7[dis_char][i-iY] >> (8-k));
			}
		}
		else
		{
			frameBuffer[(Matrix_COLS_BYTE * i) + j] = DISPdat4X7[dis_char][i-iY];
		}
		
	}		
}

void fontChar8X8(uint8_t *frameBuffer,int iX, int iY, char dis_char)
{
	uint8_t i,j,k;
	j=iX/8;//要显示是第几个点阵序号
    k=iX%8;//在第几个bit开始显示
	for(i = iY;i<(iY+10);i++)
	{
		if(k > 0)
		{
			frameBuffer[(Matrix_COLS_BYTE * i) + j] = 
			  (frameBuffer[(Matrix_COLS_BYTE * i) + j]&(0xff>>(8-k))) | (DISPdat8X10[dis_char][i-iY] << k);
			if(j < (Matrix_COLS_BYTE) - 1)
			{
				frameBuffer[(Matrix_COLS_BYTE * i) + (j+1)] =
				  (frameBuffer[(Matrix_COLS_BYTE * i) + (j+1)]&(0xff<<k)) | (DISPdat8X10[dis_char][i-iY] >> (8-k));
			}
		}
		else
		{
			frameBuffer[(Matrix_COLS_BYTE * i) + j] = DISPdat8X10[dis_char][i-iY];
			
		}
		
	}
}

void fontChar16X16(uint8_t *frameBuffer,int iX, int iY, char dis_char)
{
	uint8_t i,j,k;
	j=iX/8;//要显示是第几个点阵序号
    k=iX%8;//在第几个bit开始显示
	for(i = iY;i<(iY+16);i++)
	{
		if(k > 0)
		{
			frameBuffer[(Matrix_COLS_BYTE * i) + j] = 
			  (frameBuffer[(Matrix_COLS_BYTE * i) + j]&(0xff>>(8-k))) | (DISPdat16X16[dis_char][(i-iY)*2] << k);
			frameBuffer[(Matrix_COLS_BYTE * i) + (j+1)] =
				  (frameBuffer[(Matrix_COLS_BYTE * i) + (j+1)]&(0xff<<k)) | (DISPdat16X16[dis_char][(i-iY)*2] >> (8-k));
			frameBuffer[(Matrix_COLS_BYTE * i) + (j+1)] =
				  (frameBuffer[(Matrix_COLS_BYTE * i) + (j+1)]&(0xff>>(8-k))) | (DISPdat16X16[dis_char][(i-iY)*2+1] << k);
			frameBuffer[(Matrix_COLS_BYTE * i) + (j+2)] =
				  (frameBuffer[(Matrix_COLS_BYTE * i) + (j+2)]&(0xff<<k)) | (DISPdat16X16[dis_char][(i-iY)*2+1] >> (8-k));
		}
		else
		{
			frameBuffer[(Matrix_COLS_BYTE * i) + j] = DISPdat16X16[dis_char][(i-iY)*2];
	
			frameBuffer[(Matrix_COLS_BYTE * i) + j + 1] = DISPdat16X16[dis_char][(i-iY)*2+1];

		}
		
	}
}

