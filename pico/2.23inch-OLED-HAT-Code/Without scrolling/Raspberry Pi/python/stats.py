import time
import sys
import os
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'drive')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging    
from drive import SSD1305

from PIL import Image,ImageDraw,ImageFont

import subprocess

# 128x32 display with hardware SPI:
disp = SSD1305.SSD1305()


# Initialize library.
disp.Init()

# Clear display.
logging.info("clear display")
disp.clear()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))
# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,width,height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = 0
top = padding
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0


# Load default font.
#font = ImageFont.load_default()

# Alternatively load a TTF font.  Make sure the .ttf font file is in the same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype('04B_08__.TTF',8)

while True:
    try:
        # Draw a black filled box to clear the image.
        draw.rectangle((0,0,width,height), outline=0, fill=0)

        # Shell scripts for system monitoring from here : https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
        cmd = "hostname -I | cut -d\' \' -f1"
        IP = subprocess.check_output(cmd, shell = True )
        cmd = "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"
        CPU = subprocess.check_output(cmd, shell = True )
        cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%sMB %.2f%%\", $3,$2,$3*100/$2 }'"
        MemUsage = subprocess.check_output(cmd, shell = True )
        cmd = "df -h | awk '$NF==\"/\"{printf \"Disk: %d/%dGB %s\", $3,$2,$5}'"
        Disk = subprocess.check_output(cmd, shell = True )

        # Write two lines of text.
        draw.text((x, top),       "IP: " + str(IP.decode('utf-8')),  font=font, fill=255)
        draw.text((x, top+8),     str(CPU.decode('utf-8')), font=font, fill=255)
        draw.text((x, top+16),    str(MemUsage.decode('utf-8')),  font=font, fill=255)
        draw.text((x, top+24),    str(Disk.decode('utf-8')),  font=font, fill=255)
        # Display image.
        disp.getbuffer(image)
        disp.ShowImage()
        time.sleep(.1)
    except(KeyboardInterrupt):
        print("\n")
        break


