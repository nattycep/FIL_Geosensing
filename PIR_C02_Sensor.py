#####################################################
# Passive Infrared Car Counter and CO2 measurements #
#####################################################
# Authors:                                          #
# Benjamin Meyer                                    #
# Morris Grüter                                     #
# Dominik Gerber                                    #
#####################################################

import machine
import time
from scd30 import SCD30
from machine import Timer
from machine import Pin
import os

def measureC02():
    global carCount
    m = scd30.read_measurement()
    if m is not None:
        file = open(numberedfilename,"a")
        date = time.localtime()
        file.write("\n"+formatTime(date)+","+('%.2f' % m[0])+","+('%.2f' % m[1])+","+str(carCount))
        file.close()
        resetCarCounter()
        
def resetCarCounter():
    global carCount
    carCount = 0

def lookForPIRActivity():
    global carCount
    if sensor_pir.value() == 1:
        print("wow es outo")
        carCount += 1
        time.sleep_ms(2000)

def formatTime(date):
    return (str(date[1])+"-"+str(date[2])+"-"+str(date[0])+" "+str(date[3])+":"+str(date[4])+":"+str(date[5]))

def createUniqueFile(filename):
    counter = 2
    originalname = filename
    nochange = True

    while filename + " (" + str(counter-1) + ")" + ".txt" in os.listdir():
        newfilename = filename + " (" + str(counter) + ")" + ".txt"
        counter += 1
        nochange = False
        
    if nochange:
        return originalname + " (1).txt"
    else:
        return newfilename
    
    
#setup PIR
sensor_pir = machine.Pin(28, machine.Pin.IN, machine.Pin.PULL_DOWN)

#setup I2C
sda=machine.Pin(6)
scl=machine.Pin(7)
i2c = machine.I2C(1, sda=sda, scl=scl, freq=400000)

#SCD30 initialization
scd30 = SCD30(i2c, 0x61)
scd30.set_measurement_interval(2)
scd30.start_continous_measurement()

#setup carCounter
carCount = 0

#timer for CO2 measurement
timer = Timer(-1)
timer.init(period=300000, mode=Timer.PERIODIC, callback=lambda t:measureC02())

#create file
numberedfilename = createUniqueFile("Data")
file = open(numberedfilename, "w")
file.write("Date,CO2(ppm),Temp(°C),CarCount")
file.close()

#led when program starts
led = Pin(25,Pin.OUT)
led.value(1)
time.sleep(0.5)
led.value(0)

#main loop
while True:
    lookForPIRActivity()

        