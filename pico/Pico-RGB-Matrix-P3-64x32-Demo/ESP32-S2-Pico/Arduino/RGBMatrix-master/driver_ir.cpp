#include "driver_ir.h"
#include "driver_buzzer.h"


static RingbufHandle_t ringBuf;


#define NEC_BITS          32
#define NEC_HDR_MARK    9000
#define NEC_HDR_SPACE   4500
#define NEC_BIT_MARK     560
#define NEC_ONE_SPACE   1680
#define NEC_ZERO_SPACE   560
#define NEC_RPT_SPACE   2250





#ifdef CONFIG_SUPIRStartSuccessFlagPORT_PICO

#define wait 0

#endif

#ifdef CONFIG_SUPPORT_ESP32S2



void esp32S2IRGpioInit(void)
{
	rmt_config_t config;
	config.rmt_mode = RMT_MODE_RX;
	config.clk_div = CLK_DIV;
	config.channel = RMT_CHANNEL;
	config.gpio_num = GPIO_NUM_IR;
	config.mem_block_num = 2;
	config.rx_config.filter_en = 1;
	config.rx_config.filter_ticks_thresh = 100;
	config.rx_config.idle_threshold = TICK_10_US * 100 * 20;
	ESP_ERROR_CHECK(rmt_config(&config));
	ESP_ERROR_CHECK(rmt_driver_install(config.channel, 5000, 0));
	rmt_get_ringbuf_handle(config.channel, &ringBuf);
	rmt_rx_start(config.channel, 1);
}




rmt_item32_t* IRrecvReadIR(void)
{
	int i;
	size_t itemSize;
	rmt_item32_t* item = (rmt_item32_t*) xRingbufferReceive((RingbufHandle_t)ringBuf, (size_t *)&itemSize, (TickType_t)1);
	int numItems = itemSize / sizeof(rmt_item32_t);
	if(numItems > 30)
	{
		return item;
	}
	else 
	{
		return NULL;
	}
}

#endif


