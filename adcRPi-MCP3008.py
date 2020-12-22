import os, busio, digitalio, board, sys, re, json, timeit
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
from time import time

# modes - a = writing appended (a+ writing/reading)  #
#         w = writing from beginning of file.  Will create file (w+ writing/reading)  #
#         r+ = reading/writing from beginning of file. Raises I/O error if doesn't exist  #
#         b means binary  #

dataFile = "pi3a-joystick.csv"
with open(dataFile, "w+") as f:       #  create data file and fill out header  #
  f.write("file,sensor,type,data\n")

def valmap(value, istart, istop, ostart, ostop):  #  function for converting from raw ADC  #
  return ostart + (ostop - ostart) * ((value - istart) / (istop - istart))

#  vref = 5
numOfChannels = 2                     #  two channels; one for X and Y directions  #
chan = [x for x in range(numOfChannels)]  
numOfSamples = 10                     #  collect multiple data samples and average to reduce noise  #
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI) #  create the spi bus  #
cs = digitalio.DigitalInOut(board.D7) #  create the cs (chip select) using a specific pin  #
mcp = MCP.MCP3008(spi, cs)            #  create the mcp object  #
chan = [AnalogIn(mcp, MCP.P0),        #  create analog input channel on pins, but only using two  #
        AnalogIn(mcp, MCP.P1),
        AnalogIn(mcp, MCP.P2),
        AnalogIn(mcp, MCP.P3),
        AnalogIn(mcp, MCP.P4),
        AnalogIn(mcp, MCP.P5),
        AnalogIn(mcp, MCP.P6),
        AnalogIn(mcp, MCP.P7)]
sensorAve = [x for x in range(numOfChannels)]  # initialize sensorAve list
sensorLastRead = [x for x in range(numOfChannels)]  #  store the last reading for noise filter  #
for x in range(numOfChannels):              #  initialize the first read for comparison later  #
  sensorLastRead[x] = chan[x].value
  sensorLastRead[x] = valmap(sensorLastRead[x], 0, 65535, 0, 4095)
adcValue = [x for x in range(numOfChannels)]
sensor = [[x for x in range(0, numOfSamples)] for x in range(0, numOfChannels)]

def readADC(x, chan):                       #  function for getting analog value8  #
  return chan[x].value

sampleInterval = 0.1                        #  check every 100ms for a joystick movement  #
time0 = time()                              #  initialize time zero  #
okToRun = True                              #  initialize flag used to stop wile loop after all readings collected  #
numOfReadings = 0                           #  initialize counter for how many readings collected  #
maxNumOfReadings = 1000                     #  max number of readings to collect (stop the loop)  #
while okToRun:
    if time() - time0 > sampleInterval:
      time0 = time()
      for x in range(numOfChannels):        #  loop thru each channel, X nd Y for joystick  #
        for i in range(numOfSamples):       #  get samples points from analog pin and average out noise  #
          t0 = time()                       #  initialize time pre reading  #
          sensor[x][i] = readADC(x, chan)   #  read analog value  #
          analogInTime = (time() - t0)*1000 #  calculate time it took to read joysticks  #
          sensor[x][i] = valmap(sensor[x][i], 0, 65535, 0, 4095) #  convrt from raw ADC value  #
          numOfReadings += 1                #  increment readings counter  #
          with open(dataFile, "a") as f:    #  update txt file with raw joystick value and time required  #
              f.write(dataFile + "," + str(x) + ",raw," + str(sensor[x][i]) + "\n")
              f.write(dataFile + "," + str(x) + ",time," + str(analogInTime) + "\n")
        sensorAve[x] = sum(sensor[x])/len(sensor[x])   #  average out noise
        with open(dataFile, "a") as f:      #  update txt file with ave joystick value and delta from last reading  #
            f.write(dataFile + "," + str(x) + ",ave," + str(sensorAve[x]) + "\n")
        with open(dataFile, "a") as f:
            f.write(dataFile + "," + str(x) + ",delta," + str(abs(sensorAve[x] - sensorLastRead[x])) + "\n")
        sensorLastRead[x] = sensorAve[x]    #  update last reading to be current  #
    if numOfReadings > maxNumOfReadings:    #  when max number of readings collected exit  #
      okToRun = False