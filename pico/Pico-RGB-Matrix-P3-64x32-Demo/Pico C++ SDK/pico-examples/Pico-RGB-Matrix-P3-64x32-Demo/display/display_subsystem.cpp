#include "display_subsystem.h"
#include "font.h"
static uint16_t LunarCalendarDay;
static uint8_t Lunar_mon;
static uint8_t Lunar_mday;
static uint8_t Lunar_mon_decile;
static uint8_t Lunar_mday_decile;
extern uint8_t LanguageFlag;
//Calculate the lunar calendar according to the Gregorian calendar
static uint16_t MonthAdd[12] = {0,31,59,90,120,151,181,212,243,273,304,334};
uint8_t month_date[2][12]={{31,29,31,30,31,30,31,31,30,31,30,31},
                          {31,28,31,30,31,30,31,31,30,31,30,31}};//Determine the number of days per month in leap and non-leap years
const char *weeks[7] = {"MON","TUE","WED","THU","FRI","SAT","SUN"};
static uint32_t LunarCalendarTable[199] =
{
	0x04AE53,0x0A5748,0x5526BD,0x0D2650,0x0D9544,0x46AAB9,0x056A4D,0x09AD42,0x24AEB6,0x04AE4A,/*1901-1910*/
	0x6A4DBE,0x0A4D52,0x0D2546,0x5D52BA,0x0B544E,0x0D6A43,0x296D37,0x095B4B,0x749BC1,0x049754,/*1911-1920*/
	0x0A4B48,0x5B25BC,0x06A550,0x06D445,0x4ADAB8,0x02B64D,0x095742,0x2497B7,0x04974A,0x664B3E,/*1921-1930*/
	0x0D4A51,0x0EA546,0x56D4BA,0x05AD4E,0x02B644,0x393738,0x092E4B,0x7C96BF,0x0C9553,0x0D4A48,/*1931-1940*/
	0x6DA53B,0x0B554F,0x056A45,0x4AADB9,0x025D4D,0x092D42,0x2C95B6,0x0A954A,0x7B4ABD,0x06CA51,/*1941-1950*/
	0x0B5546,0x555ABB,0x04DA4E,0x0A5B43,0x352BB8,0x052B4C,0x8A953F,0x0E9552,0x06AA48,0x6AD53C,/*1951-1960*/
	0x0AB54F,0x04B645,0x4A5739,0x0A574D,0x052642,0x3E9335,0x0D9549,0x75AABE,0x056A51,0x096D46,/*1961-1970*/
	0x54AEBB,0x04AD4F,0x0A4D43,0x4D26B7,0x0D254B,0x8D52BF,0x0B5452,0x0B6A47,0x696D3C,0x095B50,/*1971-1980*/
	0x049B45,0x4A4BB9,0x0A4B4D,0xAB25C2,0x06A554,0x06D449,0x6ADA3D,0x0AB651,0x093746,0x5497BB,/*1981-1990*/
	0x04974F,0x064B44,0x36A537,0x0EA54A,0x86B2BF,0x05AC53,0x0AB647,0x5936BC,0x092E50,0x0C9645,/*1991-2000*/
	0x4D4AB8,0x0D4A4C,0x0DA541,0x25AAB6,0x056A49,0x7AADBD,0x025D52,0x092D47,0x5C95BA,0x0A954E,/*2001-2010*/
	0x0B4A43,0x4B5537,0x0AD54A,0x955ABF,0x04BA53,0x0A5B48,0x652BBC,0x052B50,0x0A9345,0x474AB9,/*2011-2020*/
	0x06AA4C,0x0AD541,0x24DAB6,0x04B64A,0x69573D,0x0A4E51,0x0D2646,0x5E933A,0x0D534D,0x05AA43,/*2021-2030*/
	0x36B537,0x096D4B,0xB4AEBF,0x04AD53,0x0A4D48,0x6D25BC,0x0D254F,0x0D5244,0x5DAA38,0x0B5A4C,/*2031-2040*/
	0x056D41,0x24ADB6,0x049B4A,0x7A4BBE,0x0A4B51,0x0AA546,0x5B52BA,0x06D24E,0x0ADA42,0x355B37,/*2041-2050*/
	0x09374B,0x8497C1,0x049753,0x064B48,0x66A53C,0x0EA54F,0x06B244,0x4AB638,0x0AAE4C,0x092E42,/*2051-2060*/
	0x3C9735,0x0C9649,0x7D4ABD,0x0D4A51,0x0DA545,0x55AABA,0x056A4E,0x0A6D43,0x452EB7,0x052D4B,/*2061-2070*/
	0x8A95BF,0x0A9553,0x0B4A47,0x6B553B,0x0AD54F,0x055A45,0x4A5D38,0x0A5B4C,0x052B42,0x3A93B6,/*2071-2080*/
	0x069349,0x7729BD,0x06AA51,0x0AD546,0x54DABA,0x04B64E,0x0A5743,0x452738,0x0D264A,0x8E933E,/*2081-2090*/
	0x0D5252,0x0DAA47,0x66B53B,0x056D4F,0x04AE45,0x4A4EB9,0x0A4D4C,0x0D1541,0x2D92B5          /*2091-2099*/
};

void displayDateTimePage(PDisplayDevice displayDevice,PRTC_tm pt_RTC_tm,uint8_t *temp)
{
	memset(displayDevice->FBBase,0,256);
	LunarCalendarDay = 0;
	LunarCalendar(pt_RTC_tm->tm_year,pt_RTC_tm->tm_mon,pt_RTC_tm->tm_mday);
	Lunar_mon = (LunarCalendarDay & 0x3C0) >> 6;
	Lunar_mday = LunarCalendarDay & 0x3F;
	displayDevice->SetPixel(displayDevice,1,1,(pt_RTC_tm->tm_year/1000+0x30),DAT4X7);
	displayDevice->SetPixel(displayDevice,6,1,((pt_RTC_tm->tm_year/100)%10+0x30),DAT4X7);
	displayDevice->SetPixel(displayDevice,11,1,((pt_RTC_tm->tm_year/10)%10+0x30),DAT4X7);
	displayDevice->SetPixel(displayDevice,16,1,(pt_RTC_tm->tm_year%10+0x30),DAT4X7);
	displayDevice->SetPixel(displayDevice,21,1,'-',DAT4X7);
	displayDevice->SetPixel(displayDevice,24,1,(pt_RTC_tm->tm_mon/10+0x30),DAT4X7);
	displayDevice->SetPixel(displayDevice,29,1,(pt_RTC_tm->tm_mon%10+0x30),DAT4X7);
	displayDevice->SetPixel(displayDevice,34,1,'-',DAT4X7);
	displayDevice->SetPixel(displayDevice,37,1,(pt_RTC_tm->tm_mday/10+0x30),DAT4X7);
	displayDevice->SetPixel(displayDevice,42,1,(pt_RTC_tm->tm_mday%10+0x30),DAT4X7);
	select_area_color(0,0,45,7,Green,HIGH_ROW);//Year, month, day, green
	
	if(LanguageFlag == CHINESE){
		displayDevice->SetPixel(displayDevice,47,0,21,DAT8X10);
		if(pt_RTC_tm->tm_wday == 7)
		{
			displayDevice->SetPixel(displayDevice,56,0,22,DAT8X10);
		}
		else
		{
			displayDevice->SetPixel(displayDevice,56,0,(pt_RTC_tm->tm_wday+CNOFFSET),DAT8X10);
		}
	}
	else
	{
		displayDevice->SetPixel(displayDevice,47,1,weeks[pt_RTC_tm->tm_wday-1][0],DAT4X7);
		displayDevice->SetPixel(displayDevice,53,1,weeks[pt_RTC_tm->tm_wday-1][1],DAT4X7);
		displayDevice->SetPixel(displayDevice,58,1,weeks[pt_RTC_tm->tm_wday-1][2],DAT4X7);
	}
	select_area_color(46,0,63,9,Yellow,HIGH_ROW);//Week, yellow

	displayDevice->SetPixel(displayDevice,4,11,(pt_RTC_tm->tm_hour/10),DAT8X10);
	displayDevice->SetPixel(displayDevice,12,11,(pt_RTC_tm->tm_hour%10),DAT8X10);
	displayDevice->SetPixel(displayDevice,20,11,26,DAT8X10);
	displayDevice->SetPixel(displayDevice,25,11,(pt_RTC_tm->tm_min/10),DAT8X10);
	displayDevice->SetPixel(displayDevice,33,11,(pt_RTC_tm->tm_min%10),DAT8X10);
	displayDevice->SetPixel(displayDevice,41,11,26,DAT8X10);
	displayDevice->SetPixel(displayDevice,46,11,(pt_RTC_tm->tm_sec/10),DAT8X10);
	displayDevice->SetPixel(displayDevice,54,11,(pt_RTC_tm->tm_sec%10),DAT8X10);
	select_area_color(3,11,62,15,Cyan_blue,HIGH_ROW);
    select_area_color(3,0,62,4,Cyan_blue,LOW_ROW);
	
	if((Lunar_mon/10) == 1)
		Lunar_mon_decile = 10;
	if((Lunar_mday/10) == 1)
		Lunar_mday_decile = 10;
	else
		Lunar_mday_decile = (Lunar_mday/10);
	if(Lunar_mon > 10 && Lunar_mday > 10)
	{
		displayDevice->SetPixel(displayDevice,1,22,(Lunar_mon_decile+CNOFFSET) ,DAT8X10);
		displayDevice->SetPixel(displayDevice,9,22,(Lunar_mon%10+CNOFFSET),DAT8X10);
		displayDevice->SetPixel(displayDevice,17,22,23,DAT8X10);
		displayDevice->SetPixel(displayDevice,26,22,(Lunar_mday_decile+CNOFFSET) ,DAT8X10);
		displayDevice->SetPixel(displayDevice,34,22,(Lunar_mday%10+CNOFFSET),DAT8X10);
	}
	else if(Lunar_mon > 10 && Lunar_mday <= 10)
	{
		displayDevice->SetPixel(displayDevice,3,22,(Lunar_mon_decile+CNOFFSET) ,DAT8X10);
		displayDevice->SetPixel(displayDevice,11,22,(Lunar_mon%10+CNOFFSET),DAT8X10);
		displayDevice->SetPixel(displayDevice,19,22,23,DAT8X10);
		displayDevice->SetPixel(displayDevice,29,22,(Lunar_mday+CNOFFSET) ,DAT8X10);
	}
	else if(Lunar_mon <= 10 && Lunar_mday > 10)
	{
		displayDevice->SetPixel(displayDevice,3,22,(Lunar_mon+CNOFFSET) ,DAT8X10);
		displayDevice->SetPixel(displayDevice,12,22,23,DAT8X10);
		displayDevice->SetPixel(displayDevice,22,22,(Lunar_mday_decile+CNOFFSET) ,DAT8X10);
		displayDevice->SetPixel(displayDevice,31,22,(Lunar_mday%10+CNOFFSET) ,DAT8X10);
	}
	else if(Lunar_mon <= 10 && Lunar_mday <= 10)
	{
		displayDevice->SetPixel(displayDevice,5,22,(Lunar_mon+CNOFFSET) ,DAT8X10);
		displayDevice->SetPixel(displayDevice,15,22,23,DAT8X10);
		displayDevice->SetPixel(displayDevice,27,22,(Lunar_mday+CNOFFSET) ,DAT8X10);
	}
	select_area_color(1,6,43,15,Purple,LOW_ROW);//Lunar month day, purple
	
	displayDevice->SetPixel(displayDevice,44,24,(*temp/10+0x30) ,DAT4X7);
	displayDevice->SetPixel(displayDevice,49,24,(*temp%10+0x30) ,DAT4X7);
	displayDevice->SetPixel(displayDevice,54,22,24,DAT8X10);
	select_area_color(42,6,62,15,Blue,LOW_ROW); //Temperature display, blue
	
}

void displaySettingPage(PDisplayDevice displayDevice,uint8_t Select_setting_options)
{
	memset(displayDevice->FBBase,0,256);
	if(LanguageFlag == CHINESE)
	{
		
		displayDevice->SetPixel(displayDevice,1,0,0 ,DAT16X16);//setting list  form font.h
		displayDevice->SetPixel(displayDevice,17,0,1 ,DAT16X16);
		displayDevice->SetPixel(displayDevice,33,0,2 ,DAT16X16);
		displayDevice->SetPixel(displayDevice,48,0,3 ,DAT16X16);
		if(Select_setting_options == 1)
		{
			
			displayDevice->SetPixel(displayDevice,2,16,4,DAT16X16);//time setting
			displayDevice->SetPixel(displayDevice,17,16,5 ,DAT16X16);
			displayDevice->SetPixel(displayDevice,32,16,0 ,DAT16X16);
			displayDevice->SetPixel(displayDevice,48,16,1 ,DAT16X16);
		}
		else if(Select_setting_options == 2)
		{
			displayDevice->SetPixel(displayDevice,3,16,6 ,DAT16X16);//Date setting
			displayDevice->SetPixel(displayDevice,17,16,7 ,DAT16X16);
			displayDevice->SetPixel(displayDevice,32,16,0 ,DAT16X16);
			displayDevice->SetPixel(displayDevice,48,16,1 ,DAT16X16);
		}
		else if(Select_setting_options == 3)
		{
			displayDevice->SetPixel(displayDevice,3,16,8,DAT16X16);//Automatic brightness
			displayDevice->SetPixel(displayDevice,16,16,9 ,DAT16X16);
			displayDevice->SetPixel(displayDevice,32,16,10 ,DAT16X16);
			displayDevice->SetPixel(displayDevice,48,16,11 ,DAT16X16);
		}
		else if(Select_setting_options == 4)
		{
			displayDevice->SetPixel(displayDevice,1,16,12,DAT16X16);//Beep setting
			displayDevice->SetPixel(displayDevice,17,16,13,DAT16X16);
			displayDevice->SetPixel(displayDevice,33,16,0,DAT16X16);
			displayDevice->SetPixel(displayDevice,48,16,1,DAT16X16);
		}
		else if(Select_setting_options == 5)
		{
			displayDevice->SetPixel(displayDevice,1,16,14,DAT16X16);//language settings
			displayDevice->SetPixel(displayDevice,17,16,15,DAT16X16);
			displayDevice->SetPixel(displayDevice,33,16,0,DAT16X16);
			displayDevice->SetPixel(displayDevice,48,16,1,DAT16X16);
		}
	}
	else
	{
		displayDevice->SetPixel(displayDevice,10,5,'S',DAT4X7);
		displayDevice->SetPixel(displayDevice,16,5,'E',DAT4X7);
		displayDevice->SetPixel(displayDevice,21,5,'T',DAT4X7);
		displayDevice->SetPixel(displayDevice,35,5,'L',DAT4X7);
		displayDevice->SetPixel(displayDevice,40,5,'I',DAT4X7);
		displayDevice->SetPixel(displayDevice,45,5,'S',DAT4X7);
		displayDevice->SetPixel(displayDevice,51,5,'T',DAT4X7);
		if(Select_setting_options == 1)
		{
			displayDevice->SetPixel(displayDevice,10,21,'T',DAT4X7);
			displayDevice->SetPixel(displayDevice,16,21,'I' ,DAT4X7);
			displayDevice->SetPixel(displayDevice,21,21,'M' ,DAT4X7);
			displayDevice->SetPixel(displayDevice,27,21,'E' ,DAT4X7);
			displayDevice->SetPixel(displayDevice,40,21,'S' ,DAT4X7);
			displayDevice->SetPixel(displayDevice,46,21,'E' ,DAT4X7);
			displayDevice->SetPixel(displayDevice,51,21,'T' ,DAT4X7);
		}
		else if(Select_setting_options == 2)
		{
			displayDevice->SetPixel(displayDevice,10,21,'D',DAT4X7);
			displayDevice->SetPixel(displayDevice,15,21,'A' ,DAT4X7);
			displayDevice->SetPixel(displayDevice,20,21,'T' ,DAT4X7);
			displayDevice->SetPixel(displayDevice,26,21,'E' ,DAT4X7);
			displayDevice->SetPixel(displayDevice,40,21,'S' ,DAT4X7);
			displayDevice->SetPixel(displayDevice,46,21,'E' ,DAT4X7);
			displayDevice->SetPixel(displayDevice,51,21,'T' ,DAT4X7);
		}
		else if(Select_setting_options == 3)
		{
			displayDevice->SetPixel(displayDevice,10,21,'A',DAT4X7);
			displayDevice->SetPixel(displayDevice,15,21,'U' ,DAT4X7);
			displayDevice->SetPixel(displayDevice,20,21,'T' ,DAT4X7);
			displayDevice->SetPixel(displayDevice,26,21,'O' ,DAT4X7);
			displayDevice->SetPixel(displayDevice,35,21,'L' ,DAT4X7);
			displayDevice->SetPixel(displayDevice,40,21,'I' ,DAT4X7);
			displayDevice->SetPixel(displayDevice,45,21,'G' ,DAT4X7);
			displayDevice->SetPixel(displayDevice,50,21,'H' ,DAT4X7);
			displayDevice->SetPixel(displayDevice,55,21,'T' ,DAT4X7);
		}
		else if(Select_setting_options == 4)
		{
			displayDevice->SetPixel(displayDevice,20,21,'B',DAT4X7);
			displayDevice->SetPixel(displayDevice,25,21,'E' ,DAT4X7);
			displayDevice->SetPixel(displayDevice,30,21,'E' ,DAT4X7);
			displayDevice->SetPixel(displayDevice,35,21,'P' ,DAT4X7);
		}
		else if(Select_setting_options == 5)
		{
			displayDevice->SetPixel(displayDevice,23,21,'L',DAT4X7);
			displayDevice->SetPixel(displayDevice,28,21,'A' ,DAT4X7);
			displayDevice->SetPixel(displayDevice,33,21,'N' ,DAT4X7);
		}
	}
	select_area_color(0,0,63,15,Blue,HIGH_ROW);
	select_area_color(0,0,63,15,Red,LOW_ROW);
}

void displaySetTimePage(PDisplayDevice displayDevice,uint8_t set_hour_temp,uint8_t set_min_temp,uint8_t set_sec_temp,int8_t selectedTimeOption)
{
	memset(displayDevice->FBBase,0,256);
	displayDevice->SetPixel(displayDevice,3,11,(set_hour_temp/10),DAT8X10);
	displayDevice->SetPixel(displayDevice,11,11,(set_hour_temp%10),DAT8X10);
	displayDevice->SetPixel(displayDevice,19,11,26,DAT8X10);//:
	displayDevice->SetPixel(displayDevice,24,11,(set_min_temp/10),DAT8X10);
	displayDevice->SetPixel(displayDevice,32,11,(set_min_temp%10),DAT8X10);
	displayDevice->SetPixel(displayDevice,40,11,26,DAT8X10);//:
	displayDevice->SetPixel(displayDevice,45,11,(set_sec_temp/10),DAT8X10);
	displayDevice->SetPixel(displayDevice,53,11,(set_sec_temp%10),DAT8X10);
	if(selectedTimeOption == 0)
	{
		displayDevice->SetPixel(displayDevice,8,21,'^',DAT4X7);//^
	}
	else if(selectedTimeOption == 1)
	{
		displayDevice->SetPixel(displayDevice,29,21,'^',DAT4X7);//^
	}
	else if(selectedTimeOption == 2)
	{
		displayDevice->SetPixel(displayDevice,50,21,'^',DAT4X7);//^
	}
	select_area_color(0,0,63,5,Blue,LOW_ROW);
} 


void displaySetDatePage(PDisplayDevice displayDevice,uint16_t set_year_temp,uint8_t set_mon_temp,uint8_t set_mday_temp,int8_t selectedTimeOption)
{
	memset(displayDevice->FBBase,0,256);
	displayDevice->SetPixel(displayDevice,10,13,(set_year_temp/1000+0x30),DAT4X7);
	displayDevice->SetPixel(displayDevice,15,13,(set_year_temp/100%10+0x30),DAT4X7);
	displayDevice->SetPixel(displayDevice,20,13,(set_year_temp/10%10+0x30),DAT4X7);
	displayDevice->SetPixel(displayDevice,25,13,(set_year_temp%10+0x30),DAT4X7);
	displayDevice->SetPixel(displayDevice,30,13,'-',DAT4X7);
	displayDevice->SetPixel(displayDevice,33,13,(set_mon_temp/10+0x30),DAT4X7);
	displayDevice->SetPixel(displayDevice,38,13,(set_mon_temp%10+0x30),DAT4X7);
	displayDevice->SetPixel(displayDevice,43,13,'-',DAT4X7);
	displayDevice->SetPixel(displayDevice,48,13,(set_mday_temp/10+0x30),DAT4X7);
	displayDevice->SetPixel(displayDevice,53,13,(set_mday_temp%10+0x30),DAT4X7);
	if(selectedTimeOption == 0)
	{
		displayDevice->SetPixel(displayDevice,13,21,'^',DAT4X7);//^
	}
	else if(selectedTimeOption == 1)
	{
		displayDevice->SetPixel(displayDevice,35,21,'^',DAT4X7);//^
	}
	else if(selectedTimeOption == 2)
	{
		displayDevice->SetPixel(displayDevice,50,21,'^',DAT4X7);//^
	}
	select_area_color(0,0,63,5,Blue,LOW_ROW);
}


void displayAutoLightBeepOnOffPage(PDisplayDevice displayDevice,uint8_t Select_setting_options,uint8_t autoLightFlag,uint8_t BeepFlag)
{
	memset(displayDevice->FBBase,0,256);
	displayDevice->SetPixel(displayDevice,28,4,'0',DAT4X7);
	displayDevice->SetPixel(displayDevice,33,4,'N',DAT4X7);
	displayDevice->SetPixel(displayDevice,26,20,'0',DAT4X7);
	displayDevice->SetPixel(displayDevice,31,20,'F',DAT4X7);
	displayDevice->SetPixel(displayDevice,36,20,'F',DAT4X7);
	
	if(Select_setting_options == 3)
	{
		if(autoLightFlag == 0)
			displayDevice->SetPixel(displayDevice,18,18,25,DAT8X10);//'->'  form font.h
		else
			displayDevice->SetPixel(displayDevice,20,2,25,DAT8X10);//->
	}
	else if(Select_setting_options == 4)
	{
		if(BeepFlag == 0)
			displayDevice->SetPixel(displayDevice,18,18,25,DAT8X10);//'->'
		else
			displayDevice->SetPixel(displayDevice,20,2,25,DAT8X10);//->
	}
}

void displaySetLanguagePage(PDisplayDevice displayDevice,uint8_t LanguageFlag)
{
	memset(displayDevice->FBBase,0,256);
	displayDevice->SetPixel(displayDevice,28,4,'C',DAT4X7);
	displayDevice->SetPixel(displayDevice,33,4,'N',DAT4X7);
	displayDevice->SetPixel(displayDevice,28,20,'E',DAT4X7);
	displayDevice->SetPixel(displayDevice,33,20,'N',DAT4X7);
	if(LanguageFlag == 0)
		displayDevice->SetPixel(displayDevice,18,18,25,DAT8X10);//'->'
	else
		displayDevice->SetPixel(displayDevice,20,2,25,DAT8X10);//->	
}



uint8_t LunarCalendar(uint16_t year,uint16_t month,uint16_t day)
{
	uint16_t Spring_NY,Sun_NY,StaticDayCount;
	int index,flag;
	//Spring_NY Record the number of days between the Spring Festival and the New Year's Day.
	//Sun_NY Record the number of days from the New Year's Day to the New Year's Day.
	if ( ((LunarCalendarTable[year-1901] & 0x0060) >> 5) == 1)
		Spring_NY = (LunarCalendarTable[year-1901] & 0x001F) - 1;
	else
		Spring_NY = (LunarCalendarTable[year-1901] & 0x001F) - 1 + 31;
	Sun_NY = MonthAdd[month-1] + day - 1;
	if ( (!(year % 4)) && (month > 2))
		Sun_NY++;
	//StaticDayCountRecord the day 29 or 30 of the big and small month
	//index Keep track of the month in which the calculation starts.
	//flag Is used for a special treatment of leap months.
	//Determine whether the solar calendar day is before or after the Spring Festival
	if (Sun_NY >= Spring_NY)//After the Spring Festival (including the day of the Spring Festival)
	{
		Sun_NY -= Spring_NY;
		month = 1;
		index = 1;
		flag = 0;
		if ( ( LunarCalendarTable[year - 1901] & (0x80000 >> (index-1)) ) ==0)
			StaticDayCount = 29;
		else
			StaticDayCount = 30;
		while (Sun_NY >= StaticDayCount)
		{
			Sun_NY -= StaticDayCount;
			index++;
			if (month == ((LunarCalendarTable[year - 1901] & 0xF00000) >> 20) )
			{
				flag = ~flag;
				if (flag == 0)
					month++;
			}
			else
				month++;
			if ( ( LunarCalendarTable[year - 1901] & (0x80000 >> (index-1)) ) ==0)
				StaticDayCount=29;
			else
				StaticDayCount=30;
		}
		day = Sun_NY + 1;
	}
	else //The solar calendar is before the Spring Festival
	{
		Spring_NY -= Sun_NY;
		year--;
		month = 12;
		if ( ((LunarCalendarTable[year - 1901] & 0xF00000) >> 20) == 0)
			index = 12;
		else
			index = 13;
		flag = 0;
		if ( ( LunarCalendarTable[year - 1901] & (0x80000 >> (index-1)) ) ==0)
			StaticDayCount = 29;
		else
			StaticDayCount = 30;
		while (Spring_NY > StaticDayCount)
		{
			Spring_NY -= StaticDayCount;
			index--;
			if (flag == 0)
				month--;
			if (month == ((LunarCalendarTable[year - 1901] & 0xF00000) >> 20))
				flag = ~flag;
			if ( ( LunarCalendarTable[year - 1901] & (0x80000 >> (index-1)) ) ==0)
				StaticDayCount = 29;
			else
				StaticDayCount = 30;
		}
		day = StaticDayCount - Spring_NY + 1;
	}
	LunarCalendarDay |= day;
	LunarCalendarDay |= (month << 6);
	if (month == ((LunarCalendarTable[year - 1901] & 0xF00000) >> 20))
		return 1;
	else
		return 0;
}


uint8_t get_month_date(uint16_t year_cnt,uint8_t month_cnt)//Determine the maximum number of days in a month
{
    if((year_cnt%4==0&&year_cnt%100!=0)||year_cnt%400==0)
    {
        switch(month_cnt)
        {
            case 1:return month_date[0][0];break;
            case 2:return month_date[0][1];break;
            case 3:return month_date[0][2];break;
            case 4:return month_date[0][3];break;
            case 5:return month_date[0][4];break;
            case 6:return month_date[0][5];break;
            case 7:return month_date[0][6];break;
            case 8:return month_date[0][7];break;
            case 9:return month_date[0][8];break;
            case 10:return month_date[0][9];break;
            case 11:return month_date[0][10];break;
            case 12:return month_date[0][11];break;
        }    
           
    }
    else
    {
        switch(month_cnt)
        {
            case 1:return month_date[1][0];break;
            case 2:return month_date[1][1];break;
            case 3:return month_date[1][2];break;
            case 4:return month_date[1][3];break;
            case 5:return month_date[1][4];break;
            case 6:return month_date[1][5];break;
            case 7:return month_date[1][6];break;
            case 8:return month_date[1][7];break;
            case 9:return month_date[1][8];break;
            case 10:return month_date[1][9];break;
            case 11:return month_date[1][10];break;
            case 12:return month_date[1][11];break;
        }    
    }
	return -1;
}

uint8_t get_weekday(uint16_t year_cnt,uint8_t month_cnt,uint8_t date_cnt)//Determine the day of the week according to the year, month and day
{
    uint8_t weekday = 8;
    if(month_cnt == 1 || month_cnt == 2)
    {
        month_cnt += 12;
        year_cnt--;
    }
    weekday = (date_cnt+1+2*month_cnt+3*(month_cnt+1)/5+year_cnt+year_cnt/4-year_cnt/100+year_cnt/400)%7;
    switch(weekday)
    {
        case 0 : return 7; break;
        case 1 : return 1; break;
        case 2 : return 2; break;
        case 3 : return 3; break;
        case 4 : return 4; break;
        case 5 : return 5; break;                                                             
        case 6 : return 6; break;
    }
	return 0;
}


void LED_Matrix_clear(PDisplayDevice displayDevice,uint8_t color)
{
	memset(displayDevice->FBBase,0xff,256);
	select_area_color(0,0,63,15,color,HIGH_ROW);
	select_area_color(0,0,63,15,color,LOW_ROW);
}









