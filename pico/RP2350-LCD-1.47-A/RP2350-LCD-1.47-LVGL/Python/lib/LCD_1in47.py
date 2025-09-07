from machine import Pin, SPI, PWM
import time

# Pin definition  
DC = 16
CS = 17
SCK = 18
MOSI = 19
MISO = None
RST = 20
BL = 21

# LCD Driver  
class LCD_1in47(object):
    def __init__(self): # SPI initialization
        self.width = 320
        self.height = 172
        
        self.cs = Pin(CS,Pin.OUT)
        self.rst = Pin(RST,Pin.OUT)     
        
        self.cs(1)
        self.spi = SPI(0,230_000_000,polarity=0, phase=0,bits= 8,sck=Pin(SCK),mosi=Pin(MOSI),miso=None)
        self.dc = Pin(DC,Pin.OUT)
        self.dc(1)
        self.init_display()

        self.pwm = PWM(Pin(BL))
        self.pwm.freq(5000) # Turn on the backlight
        
    # Write command 
    def write_cmd(self, cmd): 
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    # Write data 
    def write_data(self, buf): 
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(bytearray([buf]))
        self.cs(1)
    
    # Set screen brightness
    def set_bl_pwm(self,duty):    
        self.pwm.duty_u16(duty) # max 65535
        
    # LCD initialization  
    def init_display(self): 
        """Initialize dispaly"""  
        self.rst(1)
        time.sleep(0.01)
        self.rst(0)
        time.sleep(0.01)
        self.rst(1)
        time.sleep(0.05)
        
        self.write_cmd(0x36)
        self.write_data(0x70)

        self.write_cmd(0x3A) 
        self.write_data(0x05)

        self.write_cmd(0xB2)
        self.write_data(0x0C)
        self.write_data(0x0C)
        self.write_data(0x00)
        self.write_data(0x33)
        self.write_data(0x33)

        self.write_cmd(0xB7)
        self.write_data(0x35)
        
        self.write_cmd(0xBB)
        self.write_data(0x35) 

        self.write_cmd(0xC0)
        self.write_data(0x2C)

        self.write_cmd(0xC2)
        self.write_data(0x01)

        self.write_cmd(0xC3)
        self.write_data(0x13)   

        self.write_cmd(0xC4)
        self.write_data(0x20)

        self.write_cmd(0xC6)
        self.write_data(0x0F) 

        self.write_cmd(0xD0)
        self.write_data(0xA4)
        self.write_data(0xA1)
        
        self.write_cmd(0xD6)
        self.write_data(0xA1) 

        self.write_cmd(0xE0)
        self.write_data(0xF0)
        self.write_data(0x00)
        self.write_data(0x04)
        self.write_data(0x04)
        self.write_data(0x05)
        self.write_data(0x29)
        self.write_data(0x33)
        self.write_data(0x3E)
        self.write_data(0x38)
        self.write_data(0x12)
        self.write_data(0x12)
        self.write_data(0x28)
        self.write_data(0x30)

        self.write_cmd(0xE1)
        self.write_data(0xF0)
        self.write_data(0x07)
        self.write_data(0x0A)
        self.write_data(0x0D)
        self.write_data(0x0B)
        self.write_data(0x07)
        self.write_data(0x28)
        self.write_data(0x33)
        self.write_data(0x3E)
        self.write_data(0x36)
        self.write_data(0x14)
        self.write_data(0x14)
        self.write_data(0x29)
        self.write_data(0x23)
        
        self.write_cmd(0x21)

        self.write_cmd(0x11)

        self.write_cmd(0x29)
    
    # Set windows
    def setWindows(self,Xstart,Ystart,Xend,Yend): 
        self.write_cmd(0x2A);
        self.write_data(Xstart >> 8);
        self.write_data(Xstart);
        self.write_data((Xend - 1) >> 8);
        self.write_data(Xend - 1);

        self.write_cmd(0x2B);
        self.write_data(Ystart >> 8);
        self.write_data(Ystart + 0x22);
        self.write_data((Yend - 1 + 0x22) >> 8);
        self.write_data(Yend - 1 + 0x22);

        self.write_cmd(0X2C);
        
        