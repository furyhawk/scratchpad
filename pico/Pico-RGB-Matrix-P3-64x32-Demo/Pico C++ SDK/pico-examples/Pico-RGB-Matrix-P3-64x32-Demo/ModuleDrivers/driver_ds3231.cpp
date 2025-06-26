#include "driver_ds3231.h"



#ifdef CONFIG_SUPPORT_ESP32S2
static void esp32s2_i2c_write(i2c_port_t i2c_num,uint8_t regAddr, uint8_t *datawr, size_t size)
{
	i2c_cmd_handle_t cmd = i2c_cmd_link_create();
	i2c_master_start(cmd);
	i2c_master_write_byte(cmd,(DS3231_ADDRESS << 1)| WRITE,true);
	
	i2c_master_write_byte(cmd,regAddr,false);
	
	i2c_master_write(cmd,datawr,size,I2C_MASTER_LAST_NACK);
	i2c_master_stop(cmd);
	i2c_master_cmd_begin(i2c_num,cmd,1000/portTICK_RATE_MS);
	i2c_cmd_link_delete(cmd);
}
static void esp32s2_i2c_read(i2c_port_t i2c_num,uint8_t regAddr, uint8_t *datard, size_t size)
{
	if(size == 0)
		return;
	i2c_cmd_handle_t cmd = i2c_cmd_link_create();
	i2c_master_start(cmd);
	i2c_master_write_byte(cmd,(DS3231_ADDRESS << 1)| WRITE,true);
	i2c_master_write_byte(cmd,regAddr,true);
	i2c_master_start(cmd);
	i2c_master_write_byte(cmd,(DS3231_ADDRESS << 1)| READ,true);
	i2c_master_read(cmd,datard,size,I2C_MASTER_LAST_NACK);
	i2c_master_stop(cmd);
	i2c_master_cmd_begin(i2c_num,cmd,1000/portTICK_RATE_MS);
	i2c_cmd_link_delete(cmd);
}

#endif


uint8_t bcd2dec(uint8_t val)
{
    return (val >> 4) * 10 + (val & 0x0f);
}

uint8_t dec2bcd(uint8_t val)
{
    return ((val / 10) << 4) + (val % 10);
}

void InitDs3231(void)
{
	
#if defined CONFIG_SUPPORT_PICO
	uint8_t val[2];
	
	i2c_init(I2C_PORT, 400000);
	gpio_set_function(SDA, GPIO_FUNC_I2C);
	gpio_set_function(SCL, GPIO_FUNC_I2C);
	gpio_pull_up(SDA);
	gpio_pull_up(SCL);
    
    val[0] = DS3231_ADDR_CONTROL;
    val[1] = DS3231_CTRL_TEMPCONV;
    i2c_write_blocking(I2C_PORT,DS3231_ADDRESS,val,2,false);
    val[0] = DS3231_ADDR_STATUS;
    val[1] = DS3231_ADDR_TIME;
    i2c_write_blocking(I2C_PORT,DS3231_ADDRESS,val,2,false);
#elif defined CONFIG_SUPPORT_ESP32S2
	//iic init
	i2c_config_t i2c_config;
	i2c_config.mode = I2C_MODE_MASTER;
	i2c_config.sda_io_num = GPIO_NUM_14;
	i2c_config.scl_io_num = GPIO_NUM_15;
	i2c_config.sda_pullup_en = GPIO_PULLUP_ENABLE;
	i2c_config.scl_pullup_en = GPIO_PULLUP_ENABLE;
	i2c_config.master.clk_speed = 1000000;

	i2c_param_config(DS3231_I2C_NUM, &i2c_config); //i2c 参数初始
	i2c_driver_install(DS3231_I2C_NUM, I2C_MODE_MASTER, 0, 0, 0); //i2c 驱动程序安装
	
#endif

}

void ds3231_get_time(PRTC_tm time)
{

    uint8_t data[7];
#if defined CONFIG_SUPPORT_PICO
	uint8_t val = 0x00;
    i2c_write_blocking(I2C_PORT, DS3231_ADDRESS, &val, 1, true);
    i2c_read_blocking(I2C_PORT, DS3231_ADDRESS, data, 7, false);
#elif defined CONFIG_SUPPORT_ESP32S2
    esp32s2_i2c_read(DS3231_I2C_NUM, DS3231_ADDR_TIME, data, 7);
#endif
    time->tm_sec = bcd2dec(data[0]);
    time->tm_min = bcd2dec(data[1]);
    if (data[2] & DS3231_12HOUR_FLAG)
    {
  
        time->tm_hour = bcd2dec(data[2] & DS3231_12HOUR_MASK) - 1;
  
        if (data[2] & DS3231_PM_FLAG) time->tm_hour += 12;
    }
    else time->tm_hour = bcd2dec(data[2]); /* 24H */
    time->tm_wday = bcd2dec(data[3]);
    time->tm_mday = bcd2dec(data[4]);
    time->tm_mon  = bcd2dec(data[5] & DS3231_MONTH_MASK);
    time->tm_year = bcd2dec(data[6]) + 2000;
}

void ds3231_set_time(PRTC_tm time)
{

#if defined CONFIG_SUPPORT_PICO
	uint8_t data[8];
	data[0] = 0x00;
    /* time/date data */
    data[1] = dec2bcd(time->tm_sec);
    data[2] = dec2bcd(time->tm_min);
    data[3] = dec2bcd(time->tm_hour);
    /* The week data must be in the range 1 to 7, and to keep the start on the
     * same day as for tm_wday have it start at 1 on Sunday. */
    data[4] = dec2bcd(time->tm_wday);
    data[5] = dec2bcd(time->tm_mday);
    data[6] = dec2bcd(time->tm_mon);
    data[7] = dec2bcd(time->tm_year - 2000);
 	i2c_write_blocking(I2C_PORT,DS3231_ADDRESS,data,8,false);

#elif defined CONFIG_SUPPORT_ESP32S2
	uint8_t data[7];

    /* time/date data */
    data[0] = dec2bcd(time->tm_sec);
    data[1] = dec2bcd(time->tm_min);
    data[2] = dec2bcd(time->tm_hour);
    /* The week data must be in the range 1 to 7, and to keep the start on the
     * same day as for tm_wday have it start at 1 on Sunday. */
    data[3] = dec2bcd(time->tm_wday);
    data[4] = dec2bcd(time->tm_mday);
    data[5] = dec2bcd(time->tm_mon);
    data[6] = dec2bcd(time->tm_year - 2000);
    esp32s2_i2c_write(DS3231_I2C_NUM, DS3231_ADDR_TIME, data, 7);
#endif
    
}

void ds3231_get_temp_integer(uint8_t *temp)
{
	//uint16_t temperature_int;
	
#if defined CONFIG_SUPPORT_PICO
	uint8_t val = DS3231_ADDR_TEMP,data;
	unsigned char start_temperature[2] = {0x0E,0x20};
    i2c_write_blocking(I2C_PORT,DS3231_ADDRESS,start_temperature,2,false);
    i2c_write_blocking(I2C_PORT, DS3231_ADDRESS, &val, 1, true);
    i2c_read_blocking(I2C_PORT, DS3231_ADDRESS, &data, 1, false);
	*temp = data;
#elif defined CONFIG_SUPPORT_ESP32S2
	uint8_t data[2];
	esp32s2_i2c_read(DS3231_I2C_NUM, DS3231_ADDR_TEMP, data, 2);
	//temperature_int = (int16_t)(int8_t)data[0] << 2 | data[1] >> 6;
	*temp = data[0];
#endif
	
}

void ds3231_set_sec(uint8_t sec_temp)
{
#if defined CONFIG_SUPPORT_PICO
	uint8_t data[2];
	data[0] = DS3231_ADDR_TIME_SEC;
	data[1] = dec2bcd(sec_temp);
	i2c_write_blocking(I2C_PORT,DS3231_ADDRESS,data,2,false);
#elif defined CONFIG_SUPPORT_ESP32S2
	uint8_t data[1];
	data[0] = dec2bcd(sec_temp);
	esp32s2_i2c_write(DS3231_I2C_NUM, DS3231_ADDR_TIME_SEC, data, 1);
#endif
}
void ds3231_set_min(uint8_t min_temp)
{
#if defined CONFIG_SUPPORT_PICO
	uint8_t data[2];
	data[0] = DS3231_ADDR_TIME_MIN;
	data[1] = dec2bcd(min_temp);
	i2c_write_blocking(I2C_PORT,DS3231_ADDRESS,data,2,false);
#elif defined CONFIG_SUPPORT_ESP32S2
	uint8_t data[1];
	data[0] = dec2bcd(min_temp);
	esp32s2_i2c_write(DS3231_I2C_NUM, DS3231_ADDR_TIME_MIN, data, 1);
#endif
}
void ds3231_set_hour(uint8_t hour_temp)
{
#if defined CONFIG_SUPPORT_PICO
	uint8_t data[2];
	data[0] = DS3231_ADDR_TIME_HOUR;
	data[1] = dec2bcd(hour_temp);
	i2c_write_blocking(I2C_PORT,DS3231_ADDRESS,data,2,false);
#elif defined CONFIG_SUPPORT_ESP32S2
	uint8_t data[1];
	data[0] = dec2bcd(hour_temp);
	esp32s2_i2c_write(DS3231_I2C_NUM, DS3231_ADDR_TIME_HOUR, data, 1);
#endif
}
void ds3231_set_wday(uint8_t wday_temp)
{
#if defined CONFIG_SUPPORT_PICO
	uint8_t data[2];
	data[0] = DS3231_ADDR_TIME_WDAY;
	data[1] = dec2bcd(wday_temp);
	i2c_write_blocking(I2C_PORT,DS3231_ADDRESS,data,2,false);
#elif defined CONFIG_SUPPORT_ESP32S2
	uint8_t data[1];
	data[0] = dec2bcd(wday_temp);
	esp32s2_i2c_write(DS3231_I2C_NUM, DS3231_ADDR_TIME_WDAY, data, 1);
#endif
}
void ds3231_set_mday(uint8_t mday_temp)
{
#if defined CONFIG_SUPPORT_PICO
	uint8_t data[2];
	data[0] = DS3231_ADDR_TIME_MDAY;
	data[1] = dec2bcd(mday_temp);
	i2c_write_blocking(I2C_PORT,DS3231_ADDRESS,data,2,false);
#elif defined CONFIG_SUPPORT_ESP32S2
	uint8_t data[1];
	data[0] = dec2bcd(mday_temp);
	esp32s2_i2c_write(DS3231_I2C_NUM, DS3231_ADDR_TIME_MDAY, data, 1);
#endif
}
void ds3231_set_mon(uint8_t mon_temp)
{
#if defined CONFIG_SUPPORT_PICO
	uint8_t data[2];
	data[0] = DS3231_ADDR_TIME_MON;
	data[1] = dec2bcd(mon_temp);
	i2c_write_blocking(I2C_PORT,DS3231_ADDRESS,data,2,false);
#elif defined CONFIG_SUPPORT_ESP32S2
	uint8_t data[1];
	data[0] = dec2bcd(mon_temp);
	esp32s2_i2c_write(DS3231_I2C_NUM, DS3231_ADDR_TIME_MON, data, 1);
#endif
}
void ds3231_set_year(uint16_t year_temp)
{
#if defined CONFIG_SUPPORT_PICO
	uint8_t data[2];
	data[0] = DS3231_ADDR_TIME_YEAR;
	data[1] = dec2bcd(year_temp - 2000);
	i2c_write_blocking(I2C_PORT,DS3231_ADDRESS,data,2,false);
#elif defined CONFIG_SUPPORT_ESP32S2
	uint8_t data[1];
	data[0] = dec2bcd(year_temp - 2000);
	esp32s2_i2c_write(DS3231_I2C_NUM, DS3231_ADDR_TIME_YEAR, data, 1);
#endif
}
