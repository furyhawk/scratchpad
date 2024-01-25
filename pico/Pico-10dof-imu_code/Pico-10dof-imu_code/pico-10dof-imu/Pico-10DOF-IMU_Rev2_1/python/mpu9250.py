# coding: utf-8
## @package MPU9250
#  This is a MPU9250 library for the Pico-10DOF-IMU Rev2.1 I2C Brick.
#
#  
#
#  
#
#  
#
#  

import machine
from machine import Pin, I2C
import math
import time
import sys

Gyro  = [0,0,0]
Accel = [0,0,0]
Mag   = [0,0,0]
gyroOffset=[0,0,0]
magOffset=[0,0,0]
pitch = 0.0
roll  = 0.0
yaw   = 0.0
Ki = 1.0
Kp = 4.50
q0 = 1.0
q1=q2=q3=0.0

## MPU9250 Default I2C slave address
SLAVE_ADDRESS        = 0x68
## AK8963 I2C slave address
AK8963_SLAVE_ADDRESS = 0x0C
## Device id
DEVICE_ID            = 0x71

''' MPU-9250 Register Addresses '''
## sample rate driver
SMPLRT_DIV     = 0x19
CONFIG         = 0x1A
GYRO_CONFIG    = 0x1B
ACCEL_CONFIG   = 0x1C
ACCEL_CONFIG_2 = 0x1D
LP_ACCEL_ODR   = 0x1E
WOM_THR        = 0x1F
FIFO_EN        = 0x23
I2C_MST_CTRL   = 0x24
I2C_MST_STATUS = 0x36
INT_PIN_CFG    = 0x37
INT_ENABLE     = 0x38
INT_STATUS     = 0x3A
ACCEL_OUT      = 0x3B
TEMP_OUT       = 0x41
GYRO_OUT       = 0x43

I2C_MST_DELAY_CTRL = 0x67
SIGNAL_PATH_RESET  = 0x68
MOT_DETECT_CTRL    = 0x69
USER_CTRL          = 0x6A
PWR_MGMT_1         = 0x6B
PWR_MGMT_2         = 0x6C
FIFO_R_W           = 0x74
WHO_AM_I           = 0x75

## Gyro Full Scale Select 250dps
GFS_250  = 0x00
## Gyro Full Scale Select 500dps
GFS_500  = 0x01
## Gyro Full Scale Select 1000dps
GFS_1000 = 0x02
## Gyro Full Scale Select 2000dps
GFS_2000 = 0x03
## Accel Full Scale Select 2G
AFS_2G   = 0x00
## Accel Full Scale Select 4G
AFS_4G   = 0x01
## Accel Full Scale Select 8G
AFS_8G   = 0x02
## Accel Full Scale Select 16G
AFS_16G  = 0x03

# AK8963 Register Addresses
AK8963_ST1        = 0x02
AK8963_MAGNET_OUT = 0x03
AK8963_CNTL1      = 0x0A
AK8963_CNTL2      = 0x0B
AK8963_ASAX       = 0x10

# CNTL1 Mode select
## Power down mode
AK8963_MODE_DOWN   = 0x00
## One shot data output
AK8963_MODE_ONE    = 0x01

## Continous data output 8Hz
AK8963_MODE_C8HZ   = 0x02
## Continous data output 100Hz
AK8963_MODE_C100HZ = 0x06

# Magneto Scale Select
## 14bit output
AK8963_BIT_14 = 0x00
## 16bit output
AK8963_BIT_16 = 0x01

## smbus
bus = I2C(1,scl=Pin(7),sda=Pin(6),freq=400_000)

## MPU9250 I2C Controll class
class MPU9250:

    ## Constructor
    #  @param [in] address MPU-9250 I2C slave address default:0x68
    def __init__(self, address=SLAVE_ADDRESS):
        self.address = address
        self.configMPU9250(GFS_250, AFS_2G)
        self.configAK8963(AK8963_MODE_C8HZ, AK8963_BIT_16)
        self.readGyroOffset()
        self.magCalib()

    ## Search Device
    #  @param [in] self The object pointer.
    #  @retval true device connected
    #  @retval false device error
    def searchDevice(self):
        who_am_i = bus.readfrom_mem(int(self.address), int(WHO_AM_I),1)
        if(who_am_i == DEVICE_ID):
            return true
        else:
            return false

    ## Configure MPU-9250
    #  @param [in] self The object pointer.
    #  @param [in] gfs Gyro Full Scale Select(default:GFS_250[+250dps])
    #  @param [in] afs Accel Full Scale Select(default:AFS_2G[2g])
    def configMPU9250(self, gfs, afs):
        if gfs == GFS_250:
            self.gres = 250.0/32768.0
        elif gfs == GFS_500:
            self.gres = 500.0/32768.0
        elif gfs == GFS_1000:
            self.gres = 1000.0/32768.0
        else:  # gfs == GFS_2000
            self.gres = 2000.0/32768.0

        if afs == AFS_2G:
            self.ares = 2.0/32768.0
        elif afs == AFS_4G:
            self.ares = 4.0/32768.0
        elif afs == AFS_8G:
            self.ares = 8.0/32768.0
        else: # afs == AFS_16G:
            self.ares = 16.0/32768.0

        # sleep off
        bus.writeto_mem(int(self.address), int(PWR_MGMT_1), b'\x00')
        time.sleep(0.1)
        # auto select clock source
        bus.writeto_mem(int(self.address), int(PWR_MGMT_1), b'\x01')
        time.sleep(0.1)
        # DLPF_CFG
        bus.writeto_mem(int(self.address), int(CONFIG), b'\x03')
        # sample rate divider
        bus.writeto_mem(int(self.address), int(SMPLRT_DIV), b'\x04')
        # gyro full scale select
        bus.writeto_mem(int(self.address), int(GYRO_CONFIG), bytes([gfs << 3]) )
        # accel full scale select
        bus.writeto_mem(int(self.address), int(ACCEL_CONFIG), bytes([afs << 3]) )
        # A_DLPFCFG
        bus.writeto_mem(int(self.address), int(ACCEL_CONFIG_2), b'\x03')
        # BYPASS_EN
        bus.writeto_mem(int(self.address), int(INT_PIN_CFG), b'\x02')
        time.sleep(0.1)

    ## Configure AK8963
    #  @param [in] self The object pointer.
    #  @param [in] mode Magneto Mode Select(default:AK8963_MODE_C8HZ[Continous 8Hz])
    #  @param [in] mfs Magneto Scale Select(default:AK8963_BIT_16[16bit])
    def configAK8963(self, mode, mfs):
        if mfs == AK8963_BIT_14:
            self.mres = 4912.0/8190.0
        else: #  mfs == AK8963_BIT_16:
            self.mres = 4912.0/32760.0

        bus.writeto_mem(int(AK8963_SLAVE_ADDRESS), int(AK8963_CNTL1), b'\x00')
        time.sleep(0.01)

        # set read FuseROM mode
        bus.writeto_mem(int(AK8963_SLAVE_ADDRESS), int(AK8963_CNTL1), b'\x0F')
        time.sleep(0.01)

        # read coef data
        data = bus.readfrom_mem(int(AK8963_SLAVE_ADDRESS), int(AK8963_ASAX), 3)

        self.magXcoef = (data[0] - 128) / 256.0 + 1.0
        self.magYcoef = (data[1] - 128) / 256.0 + 1.0
        self.magZcoef = (data[2] - 128) / 256.0 + 1.0

        # set power down mode
        bus.writeto_mem(int(AK8963_SLAVE_ADDRESS), int(AK8963_CNTL1), b'\x00')
        time.sleep(0.01)

        # set scale&continous mode
        bus.writeto_mem(int(AK8963_SLAVE_ADDRESS), int(AK8963_CNTL1), bytes([mfs<<4|mode]) )
        time.sleep(0.01)

    ## brief Check data ready
    #  @param [in] self The object pointer.
    #  @retval true data is ready
    #  @retval false data is not ready
    def checkDataReady(self):
        drdy = bus.readfrom_mem( int(self.address), int(INT_STATUS), 1 )
        if drdy[0] & 0x01:
            return True
        else:
            return False

    ## Read accelerometer
    #  @param [in] self The object pointer.
    #  @retval x : x-axis data
    #  @retval y : y-axis data
    #  @retval z : z-axis data
    def readAccel(self):
        data = bus.readfrom_mem( int(self.address), int(ACCEL_OUT), 6)
        Accel[0] = self.dataConv(data[1], data[0])
        Accel[1] = self.dataConv(data[3], data[2])
        Accel[2] = self.dataConv(data[5], data[4])

    ## Read gyro
    #  @param [in] self The object pointer.
    #  @retval x : x-gyro data
    #  @retval y : y-gyro data
    #  @retval z : z-gyro data
    def readGyro(self):
        data = bus.readfrom_mem(int(self.address), int(GYRO_OUT), 6)
        Gyro[0] = self.dataConv(data[1], data[0]) - gyroOffset[0]
        Gyro[1] = self.dataConv(data[3], data[2]) - gyroOffset[1]
        Gyro[2] = self.dataConv(data[5], data[4]) - gyroOffset[2]

    ## Read magneto
    #  @param [in] self The object pointer.
    #  @retval x : X-magneto data
    #  @retval y : y-magneto data
    #  @retval z : Z-magneto data
    def readMagnet(self):
        # check data ready
        drdy = bus.readfrom_mem( int(AK8963_SLAVE_ADDRESS), int(AK8963_ST1), 1 )
        if drdy[0] & 0x01 :
            data = bus.readfrom_mem( int(AK8963_SLAVE_ADDRESS), int(AK8963_MAGNET_OUT) , 7 )
            # check overflow
            if (data[6] & 0x08)!=0x08:
                Mag[0] = self.dataConv(data[0], data[1]) - magOffset[0]
                Mag[1] = self.dataConv(data[2], data[3]) - magOffset[1]
                Mag[2] = self.dataConv(data[4], data[5]) - magOffset[2]
                
    def readGyroOffset(self):
        s32TempGx = 0
        s32TempGy = 0
        s32TempGz = 0
        for i in range(0,32):
            self.readGyro()
            s32TempGx += Gyro[0]
            s32TempGy += Gyro[1]
            s32TempGz += Gyro[2]
            time.sleep(0.01)
        gyroOffset[0] = s32TempGx >> 5
        gyroOffset[1] = s32TempGy >> 5
        gyroOffset[2] = s32TempGz >> 5

    ## Read temperature
    #  @param [out] temperature temperature(degrees C)
    def readTemperature(self):
        data = bus.readfrom_mem( int(self.address), int(TEMP_OUT), 2 )
        temp = self.dataConv(data[1], data[0])

        temp = round((temp / 333.87 + 21.0), 3)
        return temp

    ## Data Convert
    # @param [in] self The object pointer.
    # @param [in] data1 LSB
    # @param [in] data2 MSB
    # @retval Value MSB+LSB(int 16bit)
    def dataConv(self, data1, data2):
        value = data1 | (data2 << 8)
        if(value & (1 << 16 - 1)):
            value -= (1<<16)
        return value
    
    def magCalib(self):
        magTemp=[0,0,0,0,0,0,0,0,0]
        print("\nkeep 10dof-imu device horizontal and it will read x y z axis offset value after 4 seconds\n")
        time.sleep(4)
        print("start read all axises offset value \n")
        self.readMagnet()
        magTemp[0] = Mag[0]
        magTemp[1] = Mag[1]
        magTemp[2] = Mag[2]
        
        print("rotate z axis 180 degrees and it will read all axises offset value after 4 seconds\n")
        time.sleep(4)
        print("start read all axises offset value\n")
        self.readMagnet()
        magTemp[3] = Mag[0]
        magTemp[4] = Mag[1]
        magTemp[5] = Mag[2]
        
        print("flip 10dof-imu device and keep it horizontal and it will read all axises offset value after 4 seconds\n")
        time.sleep(4)
        print("start read all axises offset value\n")
        self.readMagnet()
        magTemp[6] = Mag[0]
        magTemp[7] = Mag[1]
        magTemp[8] = Mag[2]
        
        magOffset[0] = (magTemp[0]+magTemp[3])/2
        magOffset[1] = (magTemp[1]+magTemp[4])/2
        magOffset[2] = (magTemp[5]+magTemp[8])/2
        

    def imuAHRSupdate(self,gx, gy,gz,ax,ay,az,mx,my,mz):    
        norm=0.0
        hx = hy = hz = bx = bz = 0.0
        vx = vy = vz = wx = wy = wz = 0.0
        exInt = eyInt = ezInt = 0.0
        ex=ey=ez=0.0 
        halfT = 0.024
        global q0
        global q1
        global q2
        global q3
        q0q0 = q0 * q0
        q0q1 = q0 * q1
        q0q2 = q0 * q2
        q0q3 = q0 * q3
        q1q1 = q1 * q1
        q1q2 = q1 * q2
        q1q3 = q1 * q3
        q2q2 = q2 * q2   
        q2q3 = q2 * q3
        q3q3 = q3 * q3          

        norm = float(1/math.sqrt(ax * ax + ay * ay + az * az))     
        ax = ax * norm
        ay = ay * norm
        az = az * norm

        norm = float(1/math.sqrt(mx * mx + my * my + mz * mz))      
        mx = mx * norm
        my = my * norm
        mz = mz * norm

        # compute reference direction of flux
        hx = 2 * mx * (0.5 - q2q2 - q3q3) + 2 * my * (q1q2 - q0q3) + 2 * mz * (q1q3 + q0q2)
        hy = 2 * mx * (q1q2 + q0q3) + 2 * my * (0.5 - q1q1 - q3q3) + 2 * mz * (q2q3 - q0q1)
        hz = 2 * mx * (q1q3 - q0q2) + 2 * my * (q2q3 + q0q1) + 2 * mz * (0.5 - q1q1 - q2q2)         
        bx = math.sqrt((hx * hx) + (hy * hy))
        bz = hz     

        # estimated direction of gravity and flux (v and w)
        vx = 2 * (q1q3 - q0q2)
        vy = 2 * (q0q1 + q2q3)
        vz = q0q0 - q1q1 - q2q2 + q3q3
        wx = 2 * bx * (0.5 - q2q2 - q3q3) + 2 * bz * (q1q3 - q0q2)
        wy = 2 * bx * (q1q2 - q0q3) + 2 * bz * (q0q1 + q2q3)
        wz = 2 * bx * (q0q2 + q1q3) + 2 * bz * (0.5 - q1q1 - q2q2)  

        # error is sum of cross product between reference direction of fields and direction measured by sensors
        ex = (ay * vz - az * vy) + (my * wz - mz * wy)
        ey = (az * vx - ax * vz) + (mz * wx - mx * wz)
        ez = (ax * vy - ay * vx) + (mx * wy - my * wx)

        if (ex != 0.0 and ey != 0.0 and ez != 0.0):
            exInt = exInt + ex * Ki * halfT
            eyInt = eyInt + ey * Ki * halfT  
            ezInt = ezInt + ez * Ki * halfT

            gx = gx + Kp * ex + exInt
            gy = gy + Kp * ey + eyInt
            gz = gz + Kp * ez + ezInt

        q0 = q0 + (-q1 * gx - q2 * gy - q3 * gz) * halfT
        q1 = q1 + (q0 * gx + q2 * gz - q3 * gy) * halfT
        q2 = q2 + (q0 * gy - q1 * gz + q3 * gx) * halfT
        q3 = q3 + (q0 * gz + q1 * gy - q2 * gx) * halfT  

        norm = float(1/math.sqrt(q0 * q0 + q1 * q1 + q2 * q2 + q3 * q3))
        q0 = q0 * norm
        q1 = q1 * norm
        q2 = q2 * norm
        q3 = q3 * norm
    
mpu9250 = MPU9250()

try:
    while True:
        mpu9250.readAccel()
        mpu9250.readGyro()
        mpu9250.readMagnet()
        mpu9250.imuAHRSupdate(Gyro[0]/32.8*0.0175, Gyro[1]/32.8*0.0175,Gyro[2]/32.8*0.0175,
                Accel[0],Accel[1],Accel[2], Mag[0], Mag[0], Mag[2])
        pitch = math.asin(-2 * q1 * q3 + 2 * q0* q2)* 57.3
        roll  = math.atan2(2 * q2 * q3 + 2 * q0 * q1, -2 * q1 * q1 - 2 * q2* q2 + 1)* 57.3
        yaw   = math.atan2(-2 * q1 * q2 - 2 * q0 * q3, 2 * q2 * q2 + 2 * q3 * q3 - 1) * 57.3
        print("\r\n /-------------------------------------------------------------/ \r\n")
        print('\r\n Roll = %.2f , Pitch = %.2f , Yaw = %.2f\r\n'%(roll,pitch,yaw))
        print('\r\nAcceleration:  X = %d , Y = %d , Z = %d\r\n'%(Accel[0],Accel[1],Accel[2]))  
        print('\r\nGyroscope:     X = %d , Y = %d , Z = %d\r\n'%(Gyro[0],Gyro[1],Gyro[2]))
        print('\r\nMagnetic:      X = %d , Y = %d , Z = %d'%((Mag[0]),Mag[1],Mag[2]))
        time.sleep(0.1)

except KeyboardInterrupt:
    sys.exit()

