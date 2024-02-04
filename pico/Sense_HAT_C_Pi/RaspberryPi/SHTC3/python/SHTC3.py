#!/usr/bin/python
# -*- coding:utf-8 -*-
import time
import lgpio as sbc

SHTC3_I2C_ADDRESS   = 0x70

SHTC3_ID            = 0xEFC8
CRC_POLYNOMIAL      = 0x0131
SHTC3_WakeUp        = 0x3517
SHTC3_Sleep         = 0xB098
SHTC3_Software_RES  = 0x805D
SHTC3_NM_CD_ReadTH  = 0x7866
SHTC3_NM_CD_ReadRH  = 0x58E0

class SHTC3():
    def __init__(self,sbc,bus,address,flags = 0):
        self._sbc = sbc
        self._fd = self._sbc.i2c_open(bus, address, flags)
        self.SHTC_SOFT_RESET()

    def SHTC3_CheckCrc(self,data,len,checksum):
        crc = 0xFF
        for byteCtr in range(0,len):
            crc = crc ^ data[byteCtr]
            for bit in range(0,8):
                if crc & 0x80:
                    crc = (crc << 1) ^ CRC_POLYNOMIAL
                else:
                    crc = crc << 1
        if crc == checksum:
            return True
        else:
            return False
    
    def SHTC3_WriteCommand(self,cmd):
        self._sbc.i2c_write_byte_data(self._fd,cmd >> 8,cmd & 0xFF)
    
    def SHTC3_WAKEUP(self):
        self.SHTC3_WriteCommand(SHTC3_WakeUp) # write wake_up command
        time.sleep(0.01) # Prevent the system from crashing 
    
    def SHTC3_SLEEP(self):
        self.SHTC3_WriteCommand(SHTC3_Sleep) # Write sleep command
        time.sleep(0.01)
    
    def SHTC_SOFT_RESET(self):
        self.SHTC3_WriteCommand(SHTC3_Software_RES) # Write reset command
        time.sleep(0.01)
    
    def SHTC3_Read_TH(self): # Read temperature 
        self.SHTC3_WAKEUP()
        self.SHTC3_WriteCommand(SHTC3_NM_CD_ReadTH)
        time.sleep(0.02)
        (count,buf) = self._sbc.i2c_read_device(self._fd,3)
        if self.SHTC3_CheckCrc(buf,2,buf[2]):
            return (buf[0]<<8|buf[1]) * 175 / 65536 - 45.0 # Calculate temperature value
        else:
            return 0 # Error
    
    def SHTC3_Read_RH(self): # Read humidity 
        self.SHTC3_WAKEUP()
        self.SHTC3_WriteCommand(SHTC3_NM_CD_ReadRH)
        time.sleep(0.02)
        (count,buf) = self._sbc.i2c_read_device(self._fd,3)
        if self.SHTC3_CheckCrc(buf,2,buf[2]) :
            return 100 * (buf[0]<<8|buf[1]) / 65536 # Calculate humidity value
        else:
            return 0  # Error

if __name__ == "__main__":
    try:
        shtc3 = SHTC3(sbc, 1, SHTC3_I2C_ADDRESS)
        
        while True:
            print("Temperature = %6.2f°C , Humidity = %6.2f%%"%(shtc3.SHTC3_Read_TH(),shtc3.SHTC3_Read_RH()))
    except:
        print ("\nProgram end")
        exit()