import time
import datetime

while(True):
    CurrentTime = datetime.datetime.now()

    with open(r"/sys/class/thermal/thermal_zone0/temp") as File:
        CurrentTemp = File.readline()

    print(str(CurrentTime) + " - " + str(float(CurrentTemp) / 1000))

    time.sleep(1)