from machine import Pin, ADC
from time import time
import utime, ujson, uos

#.modes - a = writing appended (a+ writing/reading) .#
#.        w = writing from beginning of file.  Will create file (w+ writing/reading) .#
#.        r+ = reading/writing from beginning of file. Raises I/O error if doesn't exist .#
#.        b means binary

dataFile = "esp32-joystick.csv"
mode = "wb" if dataFile in uos.listdir() else "r+" #. Create data file and write out header .#
with open(dataFile, "wb") as f:
  f.write("file,sensor,type,data\n")


#. vref = 3.3 .#
numOfChannels = 2
chan = [x for x in range(numOfChannels)]   #. use two channels, 1 for X and 1 for Y direction .#
chan[0] = ADC(Pin(35))
chan[1] = ADC(Pin(34))
chan[0].atten(ADC.ATTN_11DB) #. Full range: 3.3V .#
chan[1].atten(ADC.ATTN_11DB) #. Full range: 3.3V    .#
numOfSamples = 10
sensorAve = [x for x in range(numOfChannels)]
sensorLastRead = [x for x in range(numOfChannels)]
for x in range(numOfChannels): #. initialize the first read for comparison later .#
    sensorLastRead[x] = chan[x].read()
adcValue = [x for x in range(numOfChannels)]
sensor = [[x for x in range(0, numOfSamples)] for x in range(0, numOfChannels)]

    
def valmap(self, value, istart, istop, ostart, ostop):
    return ostart + (ostop - ostart) * ((value - istart) / (istop - istart))

sampleInterval = 0.1 * 1000000             #. interval in seconds to check for update .#
time0 = utime.ticks_us()                   #. time 0 .#
okToRun = True
numOfReadings = 0
maxNumOfReadings = 1000                     #. number of readings to take before exiting .#
while okToRun:
    if utime.ticks_us() - time0 > sampleInterval:
        time0 = utime.ticks_us()
        for x in range(numOfChannels):
            for i in range(numOfSamples):  #. get samples points from analog pin and average .#
                t = utime.ticks_us()           #. pre reading time capture .#
                sensor[x][i] = chan[x].read()  #. get analog reading .#
                numOfReadings += 1
                delta = utime.ticks_diff(utime.ticks_us(), t) #. calculate how long it took to get reading .#
                analogInTime = delta/1000
                with open(dataFile, "ab") as f:               #. write to the datafile raw analog and time to measure .#
                    f.write(dataFile + "," + str(x) + ",raw," + str(sensor[x][i])+"\n")
                    f.write(dataFile + "," + str(x) + ",time," + str(analogInTime)+"\n")
            sensorAve[x] = sum(sensor[x])/len(sensor[x])      #. average out the readings to remove noise .#
            with open(dataFile, "ab") as f:                   #. write to datafile average and delta sensor reading .#
                f.write(dataFile + "," + str(x) + ",ave," + str(sensorAve[x]) + "\n")
            with open(dataFile, "ab") as f:
                f.write(dataFile + "," + str(x) + ",delta," + str(abs(sensorAve[x] - sensorLastRead[x])) + "\n")
            sensorLastRead[x] = sensorAve[x]
    if numOfReadings > maxNumOfReadings:
        okToRun = False