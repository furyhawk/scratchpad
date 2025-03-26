import serial

ser = serial.Serial("/dev/ttyUSB0", 115200, timeout=1)  # open serial port
print(ser.name)  # check which port was really used
ser.write(b"$<")  # write a string
s = ser.read(100)  # read up to ten bytes (timeout)
print(s)
ser.close()  # close port
