#pragma once

#define XPOWERS_CHIP_AXP2101

#include <driver/i2c_master.h>
#include <esp_vfs_fat.h>
#include <sdmmc_cmd.h>
#include <driver/sdmmc_host.h>
#include <driver/gpio.h>
#include <driver/spi_master.h>
#include "XPowersLib.h"
#include "bsp_config.h"

#define SDlist "/sdcard"

/*Bitmap file header   14bit*/
typedef struct BMP_FILE_HEADER {
  uint16_t bType;                         //File identifier
  uint32_t bSize;                         //The size of the file
  uint16_t bReserved1;                    //Reserved value, must be set to 0
  uint16_t bReserved2;                    //Reserved value, must be set to 0
  uint32_t bOffset;                       //The offset from the beginning of the file header to the beginning of the image data bit
} __attribute__((packed)) BMPFILEHEADER;  // 14bit

/*Bitmap information header  40bit*/
typedef struct BMP_INFO {
  uint32_t biInfoSize;       //The size of the header
  uint32_t biWidth;          //The width of the image
  uint32_t biHeight;         //The height of the image
  uint16_t biPlanes;         //The number of planes in the image
  uint16_t biBitCount;       //The number of bits per pixel
  uint32_t biCompression;    //Compression type
  uint32_t bimpImageSize;    //The size of the image, in bytes
  uint32_t biXPelsPerMeter;  //Horizontal resolution
  uint32_t biYPelsPerMeter;  //Vertical resolution
  uint32_t biClrUsed;        //The number of colors used
  uint32_t biClrImportant;   //The number of important colors
} __attribute__((packed)) BMPINFOHEADER;

/*Color table: palette */
typedef struct RGB_QUAD {
  uint8_t rgbBlue;      //Blue intensity
  uint8_t rgbGreen;     //Green strength
  uint8_t rgbRed;       //Red intensity
  uint8_t rgbReversed;  //Reserved value
} __attribute__((packed)) BMPRGBQUAD;
/**************************************** end ***********************************************/


/*****************************I2cMasterBus****************************/
class I2cMasterBus {
private:
  i2c_master_bus_handle_t user_i2c_handle = NULL;
  uint32_t i2c_data_pdMS_TICKS = 0;
  uint32_t i2c_done_pdMS_TICKS = 0;

public:
  I2cMasterBus(int scl_pin, int sda_pin, int i2c_port) {
    i2c_data_pdMS_TICKS = pdMS_TO_TICKS(5000);
    i2c_done_pdMS_TICKS = pdMS_TO_TICKS(1000);

    i2c_master_bus_config_t i2c_bus_config = {};
    i2c_bus_config.clk_source = I2C_CLK_SRC_DEFAULT;
    i2c_bus_config.i2c_port = (i2c_port_t)i2c_port;
    i2c_bus_config.scl_io_num = (gpio_num_t)scl_pin;
    i2c_bus_config.sda_io_num = (gpio_num_t)sda_pin;
    i2c_bus_config.glitch_ignore_cnt = 7;
    i2c_bus_config.flags.enable_internal_pullup = true;
    ESP_ERROR_CHECK(i2c_new_master_bus(&i2c_bus_config, &user_i2c_handle));
  }

  ~I2cMasterBus() {}

  int i2c_write_buff(i2c_master_dev_handle_t dev_handle, int reg, uint8_t *buf, uint8_t len) {
    int ret;
    uint8_t *pbuf = NULL;
    ret = i2c_master_bus_wait_all_done(user_i2c_handle, i2c_done_pdMS_TICKS);
    if (ret != ESP_OK)
      return ret;
    if (reg == -1) {
      ret = i2c_master_transmit(dev_handle, buf, len, i2c_data_pdMS_TICKS);
    } else {
      pbuf = (uint8_t *)malloc(len + 1);
      pbuf[0] = reg;
      for (uint8_t i = 0; i < len; i++) {
        pbuf[i + 1] = buf[i];
      }
      ret = i2c_master_transmit(dev_handle, pbuf, len + 1, i2c_data_pdMS_TICKS);
      free(pbuf);
      pbuf = NULL;
    }
    return ret;
  }

  int i2c_master_write_read_dev(i2c_master_dev_handle_t dev_handle, uint8_t *writeBuf, uint8_t writeLen, uint8_t *readBuf, uint8_t readLen) {
    int ret;
    ret = i2c_master_bus_wait_all_done(user_i2c_handle, i2c_done_pdMS_TICKS);
    if (ret != ESP_OK)
      return ret;
    ret = i2c_master_transmit_receive(dev_handle, writeBuf, writeLen, readBuf, readLen, i2c_data_pdMS_TICKS);
    return ret;
  }

  int i2c_read_buff(i2c_master_dev_handle_t dev_handle, int reg, uint8_t *buf, uint8_t len) {
    int ret;
    uint8_t addr = 0;
    ret = i2c_master_bus_wait_all_done(user_i2c_handle, i2c_done_pdMS_TICKS);
    if (ret != ESP_OK)
      return ret;
    if (reg == -1) {
      ret = i2c_master_receive(dev_handle, buf, len, i2c_data_pdMS_TICKS);
    } else {
      addr = (uint8_t)reg;
      ret = i2c_master_transmit_receive(dev_handle, &addr, 1, buf, len, i2c_data_pdMS_TICKS);
    }
    return ret;
  }

  i2c_master_bus_handle_t Get_I2cBusHandle() {
    return user_i2c_handle;
  }
};

/*****************************axp2101****************************/
static I2cMasterBus *i2cbus_ = NULL;
static i2c_master_dev_handle_t i2cPMICdev_ = NULL;
static uint8_t i2cPMICAddress_;
const char *TAG = "axp2101";
static XPowersPMU axp2101;

static int AXP2101_SLAVE_Read(uint8_t devAddr, uint8_t regAddr, uint8_t *data, uint8_t len) {
  int ret;
  uint8_t count = 3;
  do {
    ret = (i2cbus_->i2c_read_buff(i2cPMICdev_, regAddr, data, len) == ESP_OK) ? 0 : -1;
    if (ret == 0)
      break;
    vTaskDelay(pdMS_TO_TICKS(100));
    count--;
  } while (count);
  return ret;
}

static int AXP2101_SLAVE_Write(uint8_t devAddr, uint8_t regAddr, uint8_t *data, uint8_t len) {
  int ret;
  uint8_t count = 3;
  do {
    ret = (i2cbus_->i2c_write_buff(i2cPMICdev_, regAddr, data, len) == ESP_OK) ? 0 : -1;
    if (ret == 0)
      break;
    vTaskDelay(pdMS_TO_TICKS(100));
    count--;
  } while (count);
  return ret;
}

void Custom_PmicPortInit(I2cMasterBus *i2cbus, uint8_t dev_addr) {
  if (i2cbus_ == NULL) {
    i2cbus_ = i2cbus;
  }
  if (i2cPMICdev_ == NULL) {
    i2c_master_bus_handle_t BusHandle = i2cbus_->Get_I2cBusHandle();
    i2c_device_config_t dev_cfg = {};
    dev_cfg.dev_addr_length = I2C_ADDR_BIT_LEN_7;
    dev_cfg.scl_speed_hz = 300000;
    dev_cfg.device_address = dev_addr;
    ESP_ERROR_CHECK(i2c_master_bus_add_device(BusHandle, &dev_cfg, &i2cPMICdev_));
    i2cPMICAddress_ = dev_addr;
  }
  if (axp2101.begin(i2cPMICAddress_, AXP2101_SLAVE_Read, AXP2101_SLAVE_Write)) {
    ESP_LOGI(TAG, "Init PMU SUCCESS!");
  } else {
    ESP_LOGE(TAG, "Init PMU FAILED!");
  }
}

void Custom_PmicRegisterInit(void) {
  if (axp2101.getALDO4Voltage() != 3300) {
    axp2101.setALDO4Voltage(3300);
    ESP_LOGW("axp2101_init_log", "Set ALDO4 to output 3V3");
  }
  if (axp2101.getALDO3Voltage() != 3300) {
    axp2101.setALDO3Voltage(3300);
    ESP_LOGW("axp2101_init_log", "Set ALDO3 to output 3V3");
  }
  /*read reg*/
  uint8_t reg = axp2101.readRegister(0x30);
  if(!(reg & 0x01)) {
    axp2101.enableBattVoltageMeasure();
  }
  printf("reg 30 : 0x%02x\n",reg);
  reg = axp2101.readRegister(0x68);
  if(!(reg & 0x01)) {
    axp2101.enableBattDetection();
  }
  printf("reg 68 : 0x%02x\n",reg);
}

void Axp2101_isChargingTask(void *arg) {
  for (;;) {
    vTaskDelay(pdMS_TO_TICKS(20000));
    ESP_LOGI(TAG, "isCharging: %s", axp2101.isCharging() ? "YES" : "NO");
    uint8_t charge_status = axp2101.getChargerStatus();
    if (charge_status == XPOWERS_AXP2101_CHG_TRI_STATE) {
      ESP_LOGI(TAG, "Charger Status: tri_charge");
    } else if (charge_status == XPOWERS_AXP2101_CHG_PRE_STATE) {
      ESP_LOGI(TAG, "Charger Status: pre_charge");
    } else if (charge_status == XPOWERS_AXP2101_CHG_CC_STATE) {
      ESP_LOGI(TAG, "Charger Status: constant charge");
    } else if (charge_status == XPOWERS_AXP2101_CHG_CV_STATE) {
      ESP_LOGI(TAG, "Charger Status: constant voltage");
    } else if (charge_status == XPOWERS_AXP2101_CHG_DONE_STATE) {
      ESP_LOGI(TAG, "Charger Status: charge done");
    } else if (charge_status == XPOWERS_AXP2101_CHG_STOP_STATE) {
      ESP_LOGI(TAG, "Charger Status: not charge");
    }
    ESP_LOGI(TAG, "getBattVoltage: %d mV", axp2101.getBattVoltage());
  }
}

void axp_basic_sleep_start(void) {
  axp2101.disableIRQ(XPOWERS_AXP2101_ALL_IRQ);
  axp2101.clearIrqStatus();
  /*log输出*/
  int power_value = axp2101.readRegister(0x26);
  printf("reg_26:0x%02x\n", power_value);
  /*唤醒之后的电源设置为睡眠前的*/
  if (!(power_value & 0x04)) {
    axp2101.wakeupControl(XPOWERS_AXP2101_WAKEUP_DC_DLO_SELECT, true);
    printf("The power setting after waking up is the same as that before going to sleep.\n");
  }
  /*设置唤醒操作时,pwrok,不需要拉低*/
  if ((power_value & 0x08)) {
    axp2101.wakeupControl(XPOWERS_AXP2101_WAKEUP_PWROK_TO_LOW, false);
    printf("When setting the wake-up operation, pwrok does not need to be pulled down.\n");
  }
  /*设置唤醒源,axp2101的中断引脚*/
  if (!(power_value & 0x10)) {
    axp2101.wakeupControl(XPOWERS_AXP2101_WAKEUP_IRQ_PIN_TO_LOW, true);
    printf("Set the wake-up source, the interrupt pin of axp2101.\n");
  }
  
  uint8_t reg = axp2101.readRegister(0x30);
  if(reg & 0x01) {
    axp2101.disableBattVoltageMeasure();
  }
  reg = axp2101.readRegister(0x68);
  if(reg & 0x01) {
    axp2101.disableBattDetection();
  }

  /*使能进入睡眠模式*/
  axp2101.enableSleep();
  /*log输出*/
  power_value = axp2101.readRegister(0x26);
  printf("reg_26:0x%02x\n", power_value);

  /*Disable the relevant power supply*/
  axp2101.disableDC2();
  axp2101.disableDC3();
  axp2101.disableDC4();
  axp2101.disableDC5();
  axp2101.disableALDO1();
  axp2101.disableALDO2();
  axp2101.disableBLDO1();
  axp2101.disableBLDO2();
  axp2101.disableCPUSLDO();
  axp2101.disableDLDO1();
  axp2101.disableDLDO2();
  axp2101.disableALDO4();
  axp2101.disableALDO3();
}

/*****************************sdcard****************************/
sdmmc_card_t *card_host = NULL;

void Custom_SDcardInit(void) {
  esp_vfs_fat_sdmmc_mount_config_t mount_config = {};
  mount_config.format_if_mount_failed = false;
  mount_config.max_files = 5;
  mount_config.allocation_unit_size = 16 * 1024 * 3;

  sdmmc_host_t host = SDMMC_HOST_DEFAULT();
  host.max_freq_khz = SDMMC_FREQ_HIGHSPEED;

  sdmmc_slot_config_t slot_config = SDMMC_SLOT_CONFIG_DEFAULT();
  slot_config.width = 4;
  slot_config.clk = SDMMC_CLK_PIN;
  slot_config.cmd = SDMMC_CMD_PIN;
  slot_config.d0 = SDMMC_D0_PIN;
  slot_config.d1 = SDMMC_D1_PIN;
  slot_config.d2 = SDMMC_D2_PIN;
  slot_config.d3 = SDMMC_D3_PIN;

  ESP_ERROR_CHECK_WITHOUT_ABORT(esp_vfs_fat_sdmmc_mount(SDlist, &host, &slot_config, &mount_config, &card_host));

  if (card_host != NULL) {
    sdmmc_card_print_info(stdout, card_host);
  }
}
/*****************************Led****************************/
#define LED_ALL_OFF_PIN 255
#define LED_ON 0
#define LED_OFF 1

void Led_set(uint8_t led, uint8_t mode) {
  gpio_set_level((gpio_num_t)led, mode);
}

void Led_Init(void) {
  gpio_config_t gpio_conf = {};
  gpio_conf.intr_type = GPIO_INTR_DISABLE;
  gpio_conf.mode = GPIO_MODE_OUTPUT;
  gpio_conf.pin_bit_mask = (0x1ULL << LED_PIN_Red) | (0x1ULL << LED_PIN_Green);
  gpio_conf.pull_down_en = GPIO_PULLDOWN_DISABLE;
  gpio_conf.pull_up_en = GPIO_PULLUP_ENABLE;

  ESP_ERROR_CHECK_WITHOUT_ABORT(gpio_config(&gpio_conf));
  Led_set(LED_PIN_Red, LED_OFF);
  Led_set(LED_PIN_Green, LED_OFF);
}


/*****************************ePaper****************************/

class ePaperPort {
private:
  spi_device_handle_t spi;
  uint32_t i2c_data_pdMS_TICKS = 0;
  uint32_t i2c_done_pdMS_TICKS = 0;
  int mosi_;
  int scl_;
  int dc_;
  int cs_;
  int rst_;
  int busy_;
  int width_;
  int height_;
  int dispwidth_;
  int dispheight_;
  const char *TAG = "EPD";
  uint8_t *DispBuffer = NULL;
  int Rotate = 180;
  int Mirror = 0x00;

  void reset_set_false(void) {
    gpio_set_level((gpio_num_t)rst_, false);
  }

  void reset_set_true(void) {
    gpio_set_level((gpio_num_t)rst_, true);
  }

  void cs_set_false(void) {
    gpio_set_level((gpio_num_t)cs_, false);
  }

  void cs_set_true(void) {
    gpio_set_level((gpio_num_t)cs_, true);
  }

  void dc_set_false(void) {
    gpio_set_level((gpio_num_t)dc_, false);
  }

  void dc_set_true(void) {
    gpio_set_level((gpio_num_t)dc_, true);
  }

  uint8_t get_busy_status(void) {
    return gpio_get_level((gpio_num_t)busy_);
  }

  void EPD_Reset(void) {
    reset_set_true();
    vTaskDelay(pdMS_TO_TICKS(50));
    reset_set_false();
    vTaskDelay(pdMS_TO_TICKS(20));
    reset_set_true();
    vTaskDelay(pdMS_TO_TICKS(50));
  }

  void EPD_LoopBusy(void) {
    while (1) {
      if (get_busy_status()) {
        return;
      }
      vTaskDelay(pdMS_TO_TICKS(10));
    }
  }

  void SPI_Write(uint8_t data) {
    esp_err_t ret;
    spi_transaction_t t;
    memset(&t, 0, sizeof(t));
    t.length = 8;
    t.tx_buffer = &data;
    ret = spi_device_polling_transmit(spi, &t);
    assert(ret == ESP_OK);
  }

  void EPD_SendCommand(uint8_t Reg) {
    dc_set_false();
    cs_set_false();
    SPI_Write(Reg);
    cs_set_true();
  }

  void EPD_SendData(uint8_t Data) {
    dc_set_true();
    cs_set_false();
    SPI_Write(Data);
    cs_set_true();
  }

  void EPD_Sendbuffera(uint8_t *Data, int len) {
    dc_set_true();
    cs_set_false();
    esp_err_t ret;
    spi_transaction_t t;
    memset(&t, 0, sizeof(t));
    int len_scl = len / 5000;
    int len_dcl = len % 5000;
    uint8_t *ptr = Data;
    while (len_scl) {
      t.length = 8 * 5000;
      t.tx_buffer = ptr;
      ret = spi_device_polling_transmit(spi, &t);
      assert(ret == ESP_OK);
      len_scl--;
      ptr += 5000;
    }
    t.length = 8 * len_dcl;
    t.tx_buffer = ptr;
    ret = spi_device_polling_transmit(spi, &t);
    assert(ret == ESP_OK);
    cs_set_true();
  }

  void EPD_TurnOnDisplay(void) {

    EPD_SendCommand(0x04);  // POWER_ON
    EPD_LoopBusy();

    //Second setting
    EPD_SendCommand(0x06);
    EPD_SendData(0x6F);
    EPD_SendData(0x1F);
    EPD_SendData(0x17);
    EPD_SendData(0x49);

    EPD_SendCommand(0x12);  // DISPLAY_REFRESH
    EPD_SendData(0x00);
    EPD_LoopBusy();

    EPD_SendCommand(0x02);  // POWER_OFF
    EPD_SendData(0X00);
    EPD_LoopBusy();
  }

public:
  ePaperPort(int mosi, int scl, int dc, int cs, int rst, int busy, int width, int height, spi_host_device_t spihost = SPI3_HOST)
    : mosi_(mosi), scl_(scl), dc_(dc), cs_(cs), rst_(rst), busy_(busy), width_(width), height_(height) {
    esp_err_t ret;
    spi_bus_config_t buscfg = {};
    int transfer = width_ * height_;
    dispwidth_ = width_ / 2;
    dispheight_ = height_;
    DispBuffer = (uint8_t *)heap_caps_malloc(dispwidth_ * dispheight_, MALLOC_CAP_SPIRAM);
    assert(DispBuffer);
    buscfg.miso_io_num = -1;
    buscfg.mosi_io_num = mosi;
    buscfg.sclk_io_num = scl;
    buscfg.quadwp_io_num = -1;
    buscfg.quadhd_io_num = -1;
    buscfg.max_transfer_sz = transfer;
    spi_device_interface_config_t devcfg = {};
    devcfg.spics_io_num = -1;
    devcfg.clock_speed_hz = 10 * 1000 * 1000;  //Clock out at 10 MHz
    devcfg.mode = 0;                           //SPI mode 0
    devcfg.queue_size = 7;                     //We want to be able to queue 7 transactions at a time
    devcfg.flags = SPI_DEVICE_HALFDUPLEX;
    ret = spi_bus_initialize(spihost, &buscfg, SPI_DMA_CH_AUTO);
    ESP_ERROR_CHECK(ret);
    ret = spi_bus_add_device(spihost, &devcfg, &spi);
    ESP_ERROR_CHECK(ret);

    gpio_config_t gpio_conf = {};
    gpio_conf.intr_type = GPIO_INTR_DISABLE;
    gpio_conf.mode = GPIO_MODE_OUTPUT;
    gpio_conf.pin_bit_mask = (0x1ULL << rst_) | (0x1ULL << dc_) | (0x1ULL << cs_);
    gpio_conf.pull_down_en = GPIO_PULLDOWN_DISABLE;
    gpio_conf.pull_up_en = GPIO_PULLUP_ENABLE;
    ESP_ERROR_CHECK_WITHOUT_ABORT(gpio_config(&gpio_conf));

    gpio_conf.intr_type = GPIO_INTR_DISABLE;
    gpio_conf.mode = GPIO_MODE_INPUT;
    gpio_conf.pin_bit_mask = (0x1ULL << busy_);
    gpio_conf.pull_down_en = GPIO_PULLDOWN_DISABLE;
    gpio_conf.pull_up_en = GPIO_PULLUP_ENABLE;
    ESP_ERROR_CHECK_WITHOUT_ABORT(gpio_config(&gpio_conf));

    reset_set_true();
  }

  ~ePaperPort() {}

  void EPD_Init() {
    EPD_Reset();
    EPD_LoopBusy();
    vTaskDelay(pdMS_TO_TICKS(50));

    EPD_SendCommand(0xAA);
    EPD_SendData(0x49);
    EPD_SendData(0x55);
    EPD_SendData(0x20);
    EPD_SendData(0x08);
    EPD_SendData(0x09);
    EPD_SendData(0x18);

    EPD_SendCommand(0x01);
    EPD_SendData(0x3F);

    EPD_SendCommand(0x00);
    EPD_SendData(0x5F);
    EPD_SendData(0x69);

    EPD_SendCommand(0x03);
    EPD_SendData(0x00);
    EPD_SendData(0x54);
    EPD_SendData(0x00);
    EPD_SendData(0x44);

    EPD_SendCommand(0x05);
    EPD_SendData(0x40);
    EPD_SendData(0x1F);
    EPD_SendData(0x1F);
    EPD_SendData(0x2C);

    EPD_SendCommand(0x06);
    EPD_SendData(0x6F);
    EPD_SendData(0x1F);
    EPD_SendData(0x17);
    EPD_SendData(0x49);

    EPD_SendCommand(0x08);
    EPD_SendData(0x6F);
    EPD_SendData(0x1F);
    EPD_SendData(0x1F);
    EPD_SendData(0x22);

    EPD_SendCommand(0x30);
    EPD_SendData(0x03);

    EPD_SendCommand(0x50);
    EPD_SendData(0x3F);

    EPD_SendCommand(0x60);
    EPD_SendData(0x02);
    EPD_SendData(0x00);

    EPD_SendCommand(0x61);
    EPD_SendData(0x03);
    EPD_SendData(0x20);
    EPD_SendData(0x01);
    EPD_SendData(0xE0);

    EPD_SendCommand(0x84);
    EPD_SendData(0x01);

    EPD_SendCommand(0xE3);
    EPD_SendData(0x2F);

    EPD_SendCommand(0x04);
    EPD_LoopBusy();
  }

  void EPD_DispClear(uint8_t *Image, uint8_t color) {
    EPD_SendCommand(0x10);
    for (int j = 0; j < dispheight_ * dispwidth_; j++) {
      Image[j] = (color << 4) | color;
    }
    EPD_Sendbuffera(Image, dispheight_ * dispwidth_);
    EPD_TurnOnDisplay();
  }

  void EPD_Display(uint8_t *Image) {
    EPD_SendCommand(0x10);
    EPD_Sendbuffera(Image, dispheight_ * dispwidth_);
    EPD_TurnOnDisplay();
  }

  uint8_t *EPD_GetIMGBuffer() {
    return DispBuffer;
  }

  void EPD_SetPixel(uint16_t Xpoint, uint16_t Ypoint, uint16_t Color) {
    uint16_t X, Y;
    switch (Rotate) {
      case 0:
        X = Xpoint;
        Y = Ypoint;
        break;
      case 90:
        X = width_ - Ypoint - 1;
        Y = Xpoint;
        break;
      case 180:
        X = width_ - Xpoint - 1;
        Y = height_ - Ypoint - 1;
        break;
      case 270:
        X = Ypoint;
        Y = height_ - Xpoint - 1;
        break;
      default:
        return;
    }

    switch (Mirror) {
      case 0x00:
        break;
      case 0x01:
        X = width_ - X - 1;
        break;
      case 0x02:
        Y = height_ - Y - 1;
        break;
      case 0x03:
        X = width_ - X - 1;
        Y = height_ - Y - 1;
        break;
      default:
        return;
    }

    uint32_t Addr = X / 2 + Y * dispwidth_;
    uint8_t Rdata = DispBuffer[Addr];
    Rdata = Rdata & (~(0xF0 >> ((X % 2) * 4)));
    DispBuffer[Addr] = Rdata | ((Color << 4) >> ((X % 2) * 4));
  }

  uint8_t EPD_SDcardBmpShakingColor(const char *path) {
    FILE *fp;
    BMPFILEHEADER bmpFileHeader;
    BMPINFOHEADER bmpInfoHeader;

    if ((fp = fopen(path, "rb")) == NULL) {
      ESP_LOGE(TAG, "Cann't open the file!");
      return 0;
    }
    fseek(fp, 0, SEEK_SET);
    fread(&bmpFileHeader, sizeof(BMPFILEHEADER), 1, fp);  //sizeof(BMPFILEHEADER) must be 14
    fread(&bmpInfoHeader, sizeof(BMPINFOHEADER), 1, fp);  //sizeof(BMPFILEHEADER) must be 50
    ESP_LOGW(TAG, "(WIDTH:HEIGHT) = (%ld:%ld)", bmpInfoHeader.biWidth, bmpInfoHeader.biHeight);
    if (bmpInfoHeader.biWidth * bmpInfoHeader.biHeight != 384000) {
      ESP_LOGE(TAG, "Incorrect resolution");
      return 0;
    }
    int ImageLen = bmpInfoHeader.biWidth * bmpInfoHeader.biHeight * 3;
    uint8_t *Image = (uint8_t *)heap_caps_malloc(ImageLen * sizeof(uint8_t), MALLOC_CAP_SPIRAM);
    assert(Image);
    int readbyte = bmpInfoHeader.biBitCount;
    if (readbyte != 24) {
      ESP_LOGE(TAG, "Bmp image is not 24 bitmap!");
      return 0;
    }
    uint16_t x, y;
    uint8_t Rdata[3];
    fseek(fp, bmpFileHeader.bOffset, SEEK_SET);
    for (y = 0; y < bmpInfoHeader.biHeight; y++) {
      for (x = 0; x < bmpInfoHeader.biWidth; x++) {
        if (fread((char *)Rdata, 1, 1, fp) != 1) {
          ESP_LOGW(TAG, "No such file or directory");
          break;
        }
        if (fread((char *)Rdata + 1, 1, 1, fp) != 1) {
          ESP_LOGW(TAG, "No such file or directory");
          break;
        }
        if (fread((char *)Rdata + 2, 1, 1, fp) != 1) {
          ESP_LOGW(TAG, "No such file or directory");
          break;
        }

        if (Rdata[0] == 0 && Rdata[1] == 0 && Rdata[2] == 0) {
          Image[x + (y * bmpInfoHeader.biWidth)] = 0;  //Black
        } else if (Rdata[0] == 255 && Rdata[1] == 255 && Rdata[2] == 255) {
          Image[x + (y * bmpInfoHeader.biWidth)] = 1;  //White
        } else if (Rdata[0] == 0 && Rdata[1] == 255 && Rdata[2] == 255) {
          Image[x + (y * bmpInfoHeader.biWidth)] = 2;  //Yellow
        } else if (Rdata[0] == 0 && Rdata[1] == 0 && Rdata[2] == 255) {
          Image[x + (y * bmpInfoHeader.biWidth)] = 3;  //Red
        } else if (Rdata[0] == 255 && Rdata[1] == 0 && Rdata[2] == 0) {
          Image[x + (y * bmpInfoHeader.biWidth)] = 5;  //Blue
        } else if (Rdata[0] == 0 && Rdata[1] == 255 && Rdata[2] == 0) {
          Image[x + (y * bmpInfoHeader.biWidth)] = 6;  //Green
        }
      }
    }
    fclose(fp);
    for (y = 0; y < bmpInfoHeader.biHeight; y++) {
      for (x = 0; x < bmpInfoHeader.biWidth; x++) {
        if (x > width_ || y > height_) {
          break;
        }
        EPD_SetPixel(x, y, Image[bmpInfoHeader.biHeight * bmpInfoHeader.biWidth - 1 - (bmpInfoHeader.biWidth - x - 1 + (y * bmpInfoHeader.biWidth))]);
      }
    }
    heap_caps_free(Image);
    Image = NULL;
    return 1;
  }
};