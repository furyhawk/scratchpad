#!/usr/bin/python
#coding=utf-8
import time
import math
import smbus
from gpiozero import *

#GPIO 
INT_PORT= 26

TCS34087_R_Coef     = 0.136 
TCS34087_G_Coef     = 1.000
TCS34087_B_Coef     = -0.444
TCS34087_GA         = 1.0
TCS34087_DF         = 310.0
TCS34087_CT_Coef    = 3810.0
TCS34087_CT_Offset  =1391.0

TCS34087_G_Offset   = 0.92
TCS34087_B_Offset   = 0.73
class TCS34087:
    Gain_t = 0
    IntegrationTime_t = 0
    Atime = 0
    rgb_offset_C = 0

    TCS34087_ENABLE         = 0x80
    TCS34087_ENABLE_FDEN    = 0x40    # Flicker Detection Enable -  Writing a 1 activates flicker detection  
    TCS34087_ENABLE_WEN     = 0x08    # Wait enable - Writing 1 activates the wait timer  
    TCS34087_ENABLE_AEN     = 0x02    # ALS Enable - Writing a 1 enables ALS/Color  
    TCS34087_ENABLE_PON     = 0x01    # Power ON. When asserted, the internal oscillator is activated, allowing timers and ADC channels to operate.
    # PON: Only set this bit after all other registers have been initialized by the host.
    TCS34087_ATIME          = 0x81    # ALS integration time 
    TCS34087_ATIME_Time0    = 0x00    # ATIME = ASTEP 
    TCS34087_ATIME_Time5    = 0x00    # ATIME = ASTEP × (n+1)  n=5
    TCS34087_ATIME_Time41   = 0x41    # ATIME = ASTEP × (n+1)  n=65
    TCS34087_ATIME_TimeFF   = 0xFF    # ATIME = 256 × ASTEP 

    TCS34087_ASTEP          = 0x82    # ALS Integration Time Step Size 

    TCS34087_WTIME          = 0x83    # Wait time (if TCS34087_ENABLE_WEN is asserted)   
    
    TCS34087_AILTL          = 0x84    # ALS interrupt low threshold  
    TCS34087_AILTH          = 0x85
    TCS34087_AIHTL          = 0x86    # ALS interrupt high threshold 
    TCS34087_AIHTH          = 0x87
    
    TCS34087_AUXID          = 0x90    # Auxiliary identification 0x4A
    TCS34087_REVID          = 0x91    # Revision identification 0X53
    TCS34087_ID             = 0x92    # Device identification 0x18 = TCS34087

    TCS34087_STATUS         = 0x93    # Device status one 
    TCS34087_STATUS_ASAT    = 0x80    # ALS and Flicker Detect Saturation 
    TCS34087_STATUS_AINT    = 0x04    # ALS Interrupt 
    TCS34087_STATUS_CINT    = 0x02    # Calibration Interrupt 
    TCS34087_STATUS_SINT    = 0x01    # System Interrupt 

    TCS34087_ASTATUS        = 0x94    # ALS status 
    TCS34087_ASTATUS_ASAT_STATUS  = 0x80 # ALS Saturation Status 
    TCS34087_ASTATUS_AGAIN_STATUS = 0x00 # ALS Gain Status 

    TCS34087_ADATA0L        = 0x95    # ALS channel zero data Clear
    TCS34087_ADATA0H        = 0x96

    TCS34087_ADATA1L        = 0x97    # ALS channel one data Red
    TCS34087_ADATA1H        = 0x98

    TCS34087_ADATA2L        = 0x99    # ALS channel two data Green
    TCS34087_ADATA2H        = 0x9A

    TCS34087_ADATA3L        = 0x9B    # ALS channel three data Blue
    TCS34087_ADATA3H        = 0x9C

    TCS34087_ADATA4L        = 0x9D    # ALS channel four data WIDEBAND data
    TCS34087_ADATA4H        = 0x9E

    TCS34087_ADATA5L        = 0x9F    # ALS channel five data  FLICKER data
    TCS34087_ADATA5H        = 0xA0

    TCS34087_STATUS2        = 0xA3    # Device status two 
    TCS34087_AVALID         = 0x40    # ALS Valid 
    TCS34087_ASAT_DIGITAL   = 0x10    # ALS Digital Saturation 
    TCS34087_ASAT_ANALOG    = 0x80    # ALS Analog Saturation 
    TCS34087_FDSAT_ANALOG   = 0x02    # Flicker Detect Analog Saturation 
    TCS34087_FDSAT_DIGITAL  = 0x01    # Flicker Detect Digital Saturation 

    TCS34087_STATUS3        = 0xA4    # Device status three 
    TCS34087_STATUS3_AINT_AIHT = 0x20  # ALS Interrupt High 
    TCS34087_STATUS3_AINT_AILT = 0x10  # ALS Interrupt Low 

    TCS34087_STATUS5         = 0xA6    # Device status five 
    TCS34087_STATUS5_SINT_FD = 0x08    # Flicker Detect Interrupt 

    TCS34087_STATUS6         = 0xA7    # Device status six 
    TCS34087_STATUS6_OVTEMP_DETECTED   = 0x20   # Over Temperature Detected 
    TCS34087_STATUS6_FD_TRIGGER_ERROR  = 0x10   # Flicker Detect Trigger Error 
    TCS34087_STATUS6_ALS_TRIGGER_ERROR = 0x04   # ALS Trigger Error 
    TCS34087_STATUS6_SAI_ACTIVE        = 0x02   # Sleep After Interrupt Active 
    TCS34087_STATUS6_INIT_BUSY         = 0x01   # Initialization Busy 

    TCS34087_CFG0               = 0xA9 # Configuration zero 
    TCS34087_CFG0_LOWPOWER_IDLE = 0x40 # Low Power Idle 
    TCS34087_CFG0_ALS_TRIGGER_LONG = 0x04 # ALS Trigger Long 
    TCS34087_CFG0_RAM_BANK   = 0x00   # RAM Bank Selection 

    TCS34087_CFG1            = 0xAA   # Configuration one 
    TCS34087_CFG1_AGAIN      = 0x09   # ALS Gain. Sets the ALS sensitivity. 
    #Value = 0x00~0x0C Value = 0x00 GAIN = 0.5x GAIN = 2^(Value-1)

    TCS34087_CFG3            = 0xAC   # Configuration three 
    TCS34087_CFG3_SAI        = 0x10   # Sleep After Interrupt 

    TCS34087_CFG4            = 0xAD   # Configuration four 
    TCS34087_CFG4_INT_PINMAP = 0x40   # Interrupt Pin Map 
    TCS34087_CFG4_INT_INVERT = 0x08   # Interrupt Invert 

    TCS34087_CFG6            = 0xAF   # Configuration six 
    TCS34087_CFG6_ALS_AGC_MAX_GAIN_START = 0x40 # Figure 35 

    TCS34087_CFG8            = 0xB1   # Configuration eight 
    TCS34087_CFG8_ALS_AGC_ENABLE = 0x04 # ALS AGC Enable 

    TCS34087_CFG9            = 0xB2   # Configuration nine 
    TCS34087_CFG9_SIEN_FD    = 0x40   # System Interrupt Flicker Detection 

    TCS34087_CFG10           = 0xB3   # Configuration ten 
    TCS34087_CFG10_ALS_AGC_HIGH_HYST = 0xC0 # ALS AGC High Hysteresis 
    TCS34087_CFG10_ALS_AGC_LOW_HYST  = 0x30 # ALS AGC Low Hysteresis 
    TCS34087_CFG10_FD_PERS    = 0x02  # Flicker Detect Persistence 


    TCS34087_CFG11           = 0xB4   # Configuration eleven 
    TCS34087_CFG11_AINT_DIRECT = 0x80 # ALS Interrupt Direct 

    TCS34087_CFG12           = 0xB5    # Configuration twelve 
    TCS34087_CFG12_ALS_TH_CHANNEL = 0x00 # ALS Thresholds Channel 

    TCS34087_PERS           = 0xBD  # Persistence register - basic SW filtering mechanism for interrupts  
    TCS34087_PERS_NONE      = 0x00  # Every RGBC cycle generates an interrupt                                 
    TCS34087_PERS_1_CYCLE   = 0x01  # 1 clean channel value outside threshold range generates an interrupt    
    TCS34087_PERS_2_CYCLE   = 0x02  # 2 clean channel values outside threshold range generates an interrupt   
    TCS34087_PERS_3_CYCLE   = 0x03  # 3 clean channel values outside threshold range generates an interrupt   
    TCS34087_PERS_5_CYCLE   = 0x04  # 5 clean channel values outside threshold range generates an interrupt   
    TCS34087_PERS_10_CYCLE  = 0x05  # 10 clean channel values outside threshold range generates an interrupt  
    TCS34087_PERS_15_CYCLE  = 0x06  # 15 clean channel values outside threshold range generates an interrupt  
    TCS34087_PERS_20_CYCLE  = 0x07  # 20 clean channel values outside threshold range generates an interrupt  
    TCS34087_PERS_25_CYCLE  = 0x08  # 25 clean channel values outside threshold range generates an interrupt  
    TCS34087_PERS_30_CYCLE  = 0x09  # 30 clean channel values outside threshold range generates an interrupt  
    TCS34087_PERS_35_CYCLE  = 0x0A  # 35 clean channel values outside threshold range generates an interrupt  
    TCS34087_PERS_40_CYCLE  = 0x0B  # 40 clean channel values outside threshold range generates an interrupt  
    TCS34087_PERS_45_CYCLE  = 0x0C  # 45 clean channel values outside threshold range generates an interrupt  
    TCS34087_PERS_50_CYCLE  = 0x0D  # 50 clean channel values outside threshold range generates an interrupt  
    TCS34087_PERS_55_CYCLE  = 0x0E  # 55 clean channel values outside threshold range generates an interrupt  
    TCS34087_PERS_60_CYCLE  = 0x0F  # 60 clean channel values outside threshold range generates an interrupt  
    
    TCS34087_ASTEPL         = 0xCA    # ALS integration step size 
    TCS34087_ASTEPH         = 0xCB    

    TCS34087_AGC_GAIN_MAX   = 0xCF    # Maximum AGC gains 
    TCS34087_AGC_GAIN_MAX_AGC_FD_GAIN_MAX = 0x90 # Flicker Detection AGC Gain Max 
    TCS34087_AGC_GAIN_MAX_AGC_AGAIN_MAX   = 0x09 # ALS AGC Gain Max 

    TCS34087_AZ_CONFIG      = 0xD6    # Autozero configuration  
    TCS34087_AZ_CONFIG_AZ_NTH_ITERATION = 0xFF # ALS Autozero Frequency 

    TCS34087_FD_STATUS      = 0xDB    # Flicker detection configuration zero 
    TCS34087_FD_STATUS_FD_MEASUREMENT_VALID   = 0x20  # Flicker Detection Measurement Valid 
    TCS34087_FD_STATUS_FD_SATURATION_DETECTED = 0x10  # Flicker Saturation Detected 
    TCS34087_FD_STATUS_FD_120HZ_FLICKER_VALID = 0x08  # Flicker Detection 120Hz Flicker Valid 
    TCS34087_FD_STATUS_FD_100HZ_FLICKER_VALID = 0x04  # Flicker Detection 100Hz Flicker Valid 
    TCS34087_FD_STATUS_FD_120HZ_FLICKER       = 0x02  # Flicker Detected at 120Hz 
    TCS34087_FD_STATUS_FD_100HZ_FLICKER       = 0x01  # Flicker Detected at 100Hz 


    TCS34087_INTENAB         = 0xF9    # Enable interrupts 
    TCS34087_INTENAB_ASIEN   = 0x80    # ALS and Flicker Detect Saturation Interrupt Enable 
    TCS34087_INTENAB_AIEN    = 0x04    # ALS Interrupt Enable 
    TCS34087_INTENAB_SIEN    = 0x01    # System Interrupt Enable 

    TCS34087_CONTROL         = 0xFA    # Control 
    TCS34087_CONTROL_ALS_MANUAL_AZ    = 0x04 # ALS Manual Autozero 
    TCS34087_CONTROL_CLEAR_SAI_ACTIVE = 0x01 # Clear Sleep-After-Interrupt Active 

    # Lum
    LUM_0  = 36   #<  Clear channel < 30000   
    LUM_1  = 48   #<  Clear channel < 40000  
    LUM_2  = 65   #<  Clear channel < 50000    
    LUM_3  = 80   #<  Clear channel < 60000  
    LUM_4  = 104   #<  Clear channel < 65535   

    #Integration Time
    TCS34725_INTEGRATIONTIME_2_78US  = 0x00   #<  STEP SIZE = 2.78us  VALUE = 0   
    TCS34725_INTEGRATIONTIME_nMS     = 0x01   #<  STEP SIZE = 2.78us x (n+1)  VALUE = n  
    TCS34725_INTEGRATIONTIME_1_67MS  = 0x02   #<  STEP SIZE = 1.67ms    VALUE = 599    
    TCS34725_INTEGRATIONTIME_2_78MS  = 0x03   #<  STEP SIZE = 2.78ms   VALUE = 999  
    TCS34725_INTEGRATIONTIME_50MS    = 0x04   #<  STEP SIZE = 50ms   VALUE = 17999   
    TCS34725_INTEGRATIONTIME_182MS   = 0x05    #<  STEP SIZE = 182ms   VALUE = 65535  

    #Gain
    TCS34087_GAIN_0_5X              = 0x00   #<  0.5x gain  
    TCS34087_GAIN_1X                = 0x01   #<  No gain  
    TCS34087_GAIN_4X                = 0x03   #<  4x gain  
    TCS34087_GAIN_8X                = 0x04   #<  8x gain  
    TCS34087_GAIN_16X               = 0x05   #<  16x gain 
    TCS34087_GAIN_64X               = 0x07   #<  64x gain 
    TCS34087_GAIN_128X              = 0x08   #<  128x gain 
    TCS34087_GAIN_256X              = 0x09   #<  256x gain 
    TCS34087_GAIN_512X              = 0x0A   #<  512x gain 
    TCS34087_GAIN_1024X             = 0x0B   #<  1024x gain 
    TCS34087_GAIN_2048X             = 0x0C   #<  2048x gain  
    

    def __init__(self, address=0x29, debug=False):
        self.i2c = smbus.SMBus(1)
        self.address = address
        self.debug = debug
        #Set GPIO mode
        self.INT = DigitalInputDevice(INT_PORT,pull_up=True,active_state=None)
        if (self.debug):
          print("Reseting TCS34087")

    def Write_Byte(self, reg, value):
        # "Writes an 8-bit value to the specified register/address"
        self.i2c.write_byte_data(self.address, reg, value)
        if (self.debug):
          print("I2C: Write 0x%02X to register 0x%02X" % (value, reg))
          
    def Write_Word(self, reg, value):
        # "Writes an 16-bit value to the specified register/address"
        self.i2c.write_word_data(self.address, reg, value)
        if (self.debug):
          print("I2C: Write 0x%02X to register 0x%02X" % (value, reg))
          
    def Read_Byte(self, reg):
        # "Read an unsigned byte from the I2C device"
        result = self.i2c.read_byte_data(self.address, reg)
        if (self.debug):
          print("I2C: Device 0x%02X returned 0x%02X from reg 0x%02X" % (self.address, result & 0xFF, reg))
        return result
        
    def Read_Word(self, reg):
        # "Read an unsigned byte from the I2C device"
        result = self.i2c.read_word_data(self.address, reg)
        if (self.debug):
          print("I2C: Device 0x%02X returned 0x%02X from reg 0x%02X" % (self.address, result & 0xFF, reg))
        return result
        
    def Set_Gain(self, gain):
        self.Write_Byte(self.TCS34087_CFG1, gain)
        self.Gain_t = gain

    def Set_Integration_Time(self,AT,T):
        self.Write_Byte(self.TCS34087_ATIME, AT)
        # Update the timing register 
        self.Write_Word(self.TCS34087_ASTEP, 0xE700 | T)
        self.Atime = AT
        self.IntegrationTime_t = T

    def Enable(self):
        self.Write_Byte(self.TCS34087_ENABLE,self.TCS34087_ENABLE_FDEN | self.TCS34087_ENABLE_PON | self.TCS34087_ENABLE_AEN)
        time.sleep(0.01) 

    def Disable(self):
        #Turn the device off to save power 
        reg = self.Read_Byte(self.TCS34087_ENABLE)
        self.Write_Byte(self.TCS34087_ENABLE, reg & ~(self.TCS34087_ENABLE_FDEN | TCS34087_ENABLE_PON | TCS34087_ENABLE_AEN))
     
    def Interrupt_Enable(self):
        reg = self.Read_Byte(self.TCS34087_ENABLE)
        self.Write_Byte(self.TCS34087_ENABLE, reg | self.TCS34087_INTENAB_AIEN)

    def Interrupt_Disable(self):
        reg = self.Read_Byte(self.TCS34087_ENABLE)
        self.Write_Byte(self.TCS34087_ENABLE, reg & (~self.TCS34087_INTENAB_AIEN))

    def Set_Interrupt_Persistence_Reg(self, PER):
        if(PER < 0x10):
            self.Write_Byte(self.TCS34087_PERS, PER)
        else :
            self.Write_Byte(self.TCS34087_PERS, self.TCS34087_PERS_60_CYCLE)

    def Set_Interrupt_Threshold(self, Threshold_H,  Threshold_L):
        self.Write_Byte(self.TCS34087_AILTL, Threshold_L & 0xff)
        self.Write_Byte(self.TCS34087_AILTH, Threshold_L >> 8)
        self.Write_Byte(self.TCS34087_AIHTL, Threshold_H & 0xff)
        self.Write_Byte(self.TCS34087_AIHTH, Threshold_H >> 8)

    def Clear_Interrupt_Flag(self):
        self.Write_Byte(self.TCS34087_STATUS,self.TCS34087_STATUS_ASAT)

    def TCS34087_init(self):
        ID = self.Read_Byte(self.TCS34087_ID)
        if(ID != 0x18):
            return 1
        self.Set_Integration_Time(self.TCS34087_ATIME_Time41,self.TCS34725_INTEGRATIONTIME_2_78MS)
        self.Set_Gain(self.TCS34087_GAIN_128X)
        self.IntegrationTime_t = self.TCS34725_INTEGRATIONTIME_2_78MS
        self.Gain_t = self.TCS34087_GAIN_128X
        self.Enable()
        self.Interrupt_Enable()
        self.Set_Interrupt_Threshold(0xff00, 0x00ff)
        self.Set_Interrupt_Persistence_Reg(self.TCS34087_PERS_2_CYCLE)
        self.rgb_offset_C = self.LUM_1
        return 0


    def GetLux_Interrupt(self):
        if(self.INT.value == 0):
            self.Clear_Interrupt_Flag()
            return 1
        
        return 0

    def Read_ID(self):
        return self.Read_Byte(self.TCS34087_ID)

    def Get_RGBData(self):
        self.C = self.Read_Word(self.TCS34087_ADATA0L)
        self.R = self.Read_Word(self.TCS34087_ADATA1L)
        self.G = self.Read_Word(self.TCS34087_ADATA2L)
        self.B = self.Read_Word(self.TCS34087_ADATA3L)
        self.W = self.Read_Word(self.TCS34087_ADATA4L)
        self.F = self.Read_Word(self.TCS34087_ADATA5L)

        if(self.IntegrationTime_t == self.TCS34725_INTEGRATIONTIME_2_78US):
            # time.sleep(0.01)
            pass
        elif(self.IntegrationTime_t == self.TCS34725_INTEGRATIONTIME_nMS):
            time.sleep(0.00278*(Atime + 1))
        elif(self.IntegrationTime_t == self.TCS34725_INTEGRATIONTIME_1_67MS):
            time.sleep(0.016)
        elif(self.IntegrationTime_t == self.TCS34725_INTEGRATIONTIME_2_78MS):
            time.sleep(0.03)
        elif(self.IntegrationTime_t == self.TCS34725_INTEGRATIONTIME_50MS):
            time.sleep(0.05)
        elif(self.IntegrationTime_t == self.TCS34725_INTEGRATIONTIME_182MS):
            time.sleep(0.18)  

    #Convert read data to RGB888 format
    def GetRGB888(self):
        if(self.rgb_offset_C!=0):
            self.RGB888_R = self.R // self.rgb_offset_C
            self.RGB888_G = self.G // self.rgb_offset_C // TCS34087_G_Offset
            self.RGB888_B = self.B // self.rgb_offset_C // TCS34087_B_Offset

        if(self.RGB888_R > 30):
            self.RGB888_R = self.RGB888_R - 30
        if(self.RGB888_G > 30):
            self.RGB888_G = self.RGB888_G - 30
        if(self.RGB888_B > 30):
            self.RGB888_B = self.RGB888_B - 30
        
        self.RGB888_R = int(self.RGB888_R * 255 // 225)
        self.RGB888_G = int(self.RGB888_G * 255 // 225)
        self.RGB888_B = int(self.RGB888_B * 255 // 225)

        if self.RGB888_R>255:
            self.RGB888_R = 255
        if self.RGB888_G>255:
            self.RGB888_G = 255 
        if self.RGB888_B>255:
            self.RGB888_B = 255

        self.RGB888 = (self.RGB888_R << 16) | (self.RGB888_G << 8) | (self.RGB888_B)
    def GetRGB565(self):
        if(self.rgb_offset_C!=0):
            self.RGB565_R = self.R // self.rgb_offset_C
            self.RGB565_G = self.G // self.rgb_offset_C // TCS34087_G_Offset
            self.RGB565_B = self.B // self.rgb_offset_C // TCS34087_B_Offset

        if(self.RGB565_R > 30):
            self.RGB565_R = self.RGB565_R - 30
        if(self.RGB565_G > 30):
            self.RGB565_G = self.RGB565_G - 30
        if(self.RGB565_B > 30):
            self.RGB565_B = self.RGB565_B - 30
        
        self.RGB565_R = int(self.RGB565_R * 255 // 225)
        self.RGB565_G = int(self.RGB565_G * 255 // 225)
        self.RGB565_B = int(self.RGB565_B * 255 // 225)

        if self.RGB565_R>255:
            self.RGB565_R = 255
        if self.RGB565_G>255:
            self.RGB565_G = 255 
        if self.RGB565_B>255:
            self.RGB565_B = 255

        self.RG565 = (((self.RGB565_R>>3) << 11) | ((self.RGB565_G>>2) << 5) | (self.RGB565_B>>3 ))&0xffff

    def Get_Lux(self):
        atime_ms = ((256 - self.IntegrationTime_t) * 2.4)
        if(self.R + self.G + self.B > self.C):
            ir =  (self.R + self.G + self.B - self.C) / 2 
        else:
            ir = 0
        r_comp = self.R - ir
        g_comp = self.G - ir
        b_comp = self.B - ir
        Gain_temp = 1
        if(self.Gain_t == self.TCS34087_GAIN_0_5X):
            Gain_temp = 0.5
        elif(self.Gain_t == self.TCS34087_GAIN_1X):
            Gain_temp = 1
        elif(self.Gain_t == self.TCS34087_GAIN_4X):
            Gain_temp = 4
        elif(self.Gain_t == self.TCS34087_GAIN_8X):
            Gain_temp = 8
        elif(self.Gain_t == self.TCS34087_GAIN_16X):
            Gain_temp = 16
        elif(self.Gain_t == self.TCS34087_GAIN_64X):
            Gain_temp = 64
        elif(self.Gain_t == self.TCS34087_GAIN_128X):
            Gain_temp = 128
        elif(self.Gain_t == self.TCS34087_GAIN_256X):
            Gain_temp = 256
        elif(self.Gain_t == self.TCS34087_GAIN_512X):
            Gain_temp = 512
        elif(self.Gain_t == self.TCS34087_GAIN_1024X):
            Gain_temp = 1024
        elif(self.Gain_t == self.TCS34087_GAIN_2048X):
            Gain_temp = 2048
 
        cpl = (atime_ms * Gain_temp) / (TCS34087_GA * TCS34087_DF)
        lux = (TCS34087_R_Coef * (float)(r_comp) + TCS34087_G_Coef * \
            (float)(g_comp) +  TCS34087_B_Coef * (float)(b_comp)) / cpl
        return lux
        
    def Get_ColorTemp(self):
        ir=1.0
        if(self.R + self.G + self.B > self.C):
            ir =  (self.R + self.G + self.B - self.C - 1) / 2 
        else:
            ir = 0
        r_comp = self.R - ir
        b_comp = self.B - ir
        cct=TCS34087_CT_Coef * (float)(b_comp) / (float)(r_comp) + TCS34087_CT_Offset
        return cct


        
        
        
        
        
        
        
        
        
        
        
        
