import machine
import sdcard
import uos

# Assign chip select (CS) pin (and start it high)
cs = machine.Pin(23, machine.Pin.OUT)

# Intialize SPI peripheral (start with 1 MHz)
spi = machine.SPI(id=0,
                  baudrate=10000000,
                  polarity=0,
                  phase=0,
                  bits=8,
                  firstbit=machine.SPI.MSB,
                  sck=machine.Pin(18),
                  mosi=machine.Pin(19),
                  miso=machine.Pin(20))

# Initialize SD card
sd = sdcard.SDCard(spi, cs,baudrate=5_000_000)

# Mount filesystem
uos.mount(sd, '/sd')

