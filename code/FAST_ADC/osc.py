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

# sample frequencies
sample_freq_list = [0, 0.2, 0.5, 1, 2, 5, 10, 25]
freq_index = 3
max_freq_index = 5

# operation mode
OSC_MODE = 0
DSA_MODE = 1

# init DAC to set trigger threshold
TRG_THR= I2C(0x30, 1) # init DAC as I2C bus device
TRG_THR.write(b'\20') # set trigger threshold [0..255]

# init ADC: data array, number of samples, sample rate, trigger mode
n_samples = 4000 # number of samples 
trigger_mode_single = False
trigger_armed = True
adc_data = (ctypes.c_uint16 * n_samples)() # array to store ADC data
ADC.set_resolution(12)
ADC_LSB = 5000.0/4096 # 12 bit ADC, 5000 mV full range
ADC.init_device(adc_data, n_samples, 3, OSC_MODE)

# prepare time data series
time_base = ADC.get_time_base()
time_data = np.arange(0, n_samples * time_base, time_base)  
cal_adc_data = np.array(n_samples)

# prepare waveform display
plt.ion() # interactive mode
fig, waveform = plt.subplots(num = 'Oscilloscope')
waveform.set_xlabel('t [us]')
waveform.set_xlim(0, n_samples * time_base)
waveform.set_ylabel('ADC input voltage [mV]')
waveform.set_ylim(0, 5000)
waveform.grid()

# trigger ADC conversion and initialize plot
ADC.take_data()
plot1, = waveform.plot(time_data, adc_data)

# define thread function 
def updatePlot(queue):
  global time_data, n_samples, cal_adc_data, time_base, freq_index, trigger_armed, trigger_mode_single
  stop_received = False
  trigger_received = False
  while not stop_received:
    if not queue.empty():
      data = queue.get()
      
      if data == 'stop':
        stop_received = True
        break

      if data == 'update':
        # time base setting
        ADC.set_time_base(int(freq_index))
        time_base = ADC.get_time_base()
        time_data = np.arange(0, n_samples * time_base, time_base)  
        waveform.set_xlim(0, n_samples * time_base)
    
    # data taking
    if (trigger_armed):
      if (ADC.take_data() == 0):
        trigger_received = True
      else:
        trigger_received = False
      cal_adc_data = np.array(adc_data) * ADC_LSB 
      plot1.set_data(time_data, cal_adc_data)
      time.sleep(0.01)
      
      # don't re-arm trigger in single mode when trigger has been received
      if (trigger_mode_single and trigger_received):
        trigger_armed = False

# add queue to pass data between main and plotting thread
queue = Queue()

# prepare and start plotting thread
updateThread = Thread(target=updatePlot, args=(queue,))
updateThread.start()

while True:
  os.system('cls||clear')
  print('\033[1m' + 'Oscilloscope' + '\033[0m' + '\n')
  print('Sample frequency: %.1f MHz' % sample_freq_list[freq_index])
  print('Trigger mode: %s' % ('Auto' if not trigger_mode_single else 'Single'))
  print(
'\nCommands:\n\
  <1..7>  Sample frequency [0.2, 0.5, 1, 2, 5] MHz\n\
  <a>     Auto trigger mode\n\
  <s>     Single trigger mode\n\
  <i>     Save plot image (png)\n\
  <d>     Save waveform data (cvs)\n\
  <q>     Quit')
  key = input('Enter command:')
  
  if (key.isdigit() and int(key) in range(1, max_freq_index + 1)):
    freq_index = int(key) 
    queue.put('update')

  # auto trigger mode, loop continuously
  if (key == 'a'):
    trigger_mode_single = False
    trigger_armed = True
    queue.put('update')
      
  # wait for single trigger
  if (key == 's'):
    trigger_mode_single = True
    trigger_armed = True    
    queue.put('update')

  if key == 'q':
    queue.put('stop')
    break
  
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
