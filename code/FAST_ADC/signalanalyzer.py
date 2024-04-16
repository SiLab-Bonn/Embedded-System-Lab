import ctypes
import time
import matplotlib.pyplot as plt
import csv
import os
from threading import Thread
from queue import Queue
import numpy as np
from i2cdev import I2C
import RPi.GPIO as GPIO

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
# EXT_TRG = 4 # GPIO4 controls external trigger
# GPIO.setup(EXT_TRG, GPIO.IN) # disable output 

# access to c-library for fast ADC access with DMA support
# set return type for time base getter
ADC = ctypes.CDLL("/home/pi/Embedded-System-Lab/code/lib/fast_adc.so")  
ADC.get_time_base.restype = ctypes.c_float 

# some constants
SAMPLE_RATE_200k = 1  # 5 us
SAMPLE_RATE_500k = 2  # 2 us
SAMPLE_RATE_1M   = 3  # 1 us
SAMPLE_RATE_2M   = 4  # 0.5 us
SAMPLE_RATE_5M   = 5  # 0.25 us

# operation mode
OSC_MODE = 1
LSA_MODE = 0
LSA_CHANNELS = 4

# init DAC to set trigger threshold
TRG_THR= I2C(0x30, 1) # init DAC as I2C bus device
TRG_THR.write(b'\20') # set trigger threshold [0..255]

# init ADC: data array, number of samples, sample rate, trigger mode
n_samples = 1000 # number of samples 

# trigger modes
AUTO_TRIGGER   = 0 # free-running acquisition 
NORMAL_TRIGGER = 1 # wait for hardware trigger (jumper TRG on the base board selects trigger source)
trigger_mode = NORMAL_TRIGGER
adc_data = (ctypes.c_uint16 * n_samples)() # array to store ADC data
ADC.set_resolution(LSA_CHANNELS)
ADC.init_device(adc_data, n_samples, SAMPLE_RATE_5M, trigger_mode)
ADC.set_time_base(1, trigger_mode)

# prepare time data series
time_base = ADC.get_time_base()
time_data = np.arange(0, n_samples * time_base, time_base)  
cal_adc_data = np.array(n_samples)

# prepare waveform display
plt.ion() # interactive mode
fig, waveform = plt.subplots(num = 'Logic Signal Analyzer')
waveform.set_xlabel('t [us]')
waveform.set_xlim(0, n_samples * time_base)
waveform.set_ylabel('Channel')
waveform.set_ylim(-0.1, LSA_CHANNELS - 0.4)
waveform.set_yticks(np.arange(0, LSA_CHANNELS, 1))  # Set interval to desired value
waveform.grid()

# trigger ADC conversion and initialize plot
ADC.take_data(LSA_MODE)
#plot1, = waveform.plot(time_data, adc_data)
int_array = np.array(adc_data).newbyteorder('S')
byte_array = int_array.view(np.uint8)
bit_array = np.unpackbits(byte_array)

lines = []

for i in range(LSA_CHANNELS):
  line, = waveform.plot(time_data, i + 0.5*bit_array[i::16])
  lines.append(line)

# define thread function 
def updatePlot(queue):
  global time_data, n_samples, trigger_mode, cal_adc_data
  stop_received = False
  while not stop_received:
    if not queue.empty():
      data = queue.get()
      if data == 'q':
        stop_received = True
        break
      if (data.isdigit() and int(data) in range(1, 6)):
        ADC.set_time_base(int(data), trigger_mode)
        time_base = ADC.get_time_base()
        time_data = np.arange(0, n_samples * time_base, time_base)  
        waveform.set_xlim(0, n_samples * time_base)
    
    ADC.take_data(LSA_MODE)

    int_array = np.array(adc_data).newbyteorder('S')
    byte_array = int_array.view(np.uint8)
    bit_array = np.unpackbits(byte_array)

    #print(int_array[0], bit_array[0:16])
    
    for i, line in enumerate(lines):
      line.set_data(time_data, i + 0.5*bit_array[(15-i)::16])

# add queue to pass data between main and plotting thread
queue = Queue()

# prepare and start plotting thread
updateThread = Thread(target=updatePlot, args=(queue,))
updateThread.start()

while True:
  os.system('cls||clear')
  print(
'Commands:\n\
  Set sample frequency [0.2, 0.5, 1, 2, 5] MHz: <1,2,3,4,5>\n\
  Save plot image (png): <i>\n\
  Save waveform data (cvs): <d>\n\
  Quit: <q>')
  key = input()
  queue.put(key)
  
  if key == 'q':
    break
  
  if key == 'i':
    filename = input("Enter file name:")
    fig.savefig(filename + '.png')
  
  if key == 'd':
    filename = input("Enter file name:")
    new_list = zip(time_data, cal_adc_data)
    with open(filename + '.csv', 'w+') as csvfile:
      filewriter = csv.writer(csvfile)
      filewriter.writerows(new_list)

updateThread.join()
plt.close()
ADC.close_device()
GPIO.cleanup()
TRG_THR.close()
