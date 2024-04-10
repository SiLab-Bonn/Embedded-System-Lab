import ctypes
import time
import matplotlib.pyplot as plt
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
ADC = ctypes.CDLL("../lib/fast_adc.so")  
ADC.get_time_base.restype = ctypes.c_float 

# some constants
SAMPLE_RATE_200k = 1
SAMPLE_RATE_500k = 2
SAMPLE_RATE_1M   = 3
SAMPLE_RATE_2M   = 4
SAMPLE_RATE_5M   = 5

# trigger threshold DAC
TRG_THR= I2C(0x30, 1)  # init DAC as I2C bus device
TRG_THR.write(b'\20') # set trigger threshold [0..255]
TRG_THR.close() # close device

# init ADC: data array, number of samples, sample rate, trigger mode
n_samples = 4000 # number of samples 
# trigger modes
AUTO_TRIGGER   = 0 # free-running acquisition 
NORMAL_TRIGGER = 1 # wait for hardware trigger (jumper TRG on the base board selects trigger source)
trigger_mode = NORMAL_TRIGGER
adc_data = (ctypes.c_uint16 * n_samples)() # array to store ADC data
ADC.init_device(adc_data, n_samples, SAMPLE_RATE_5M, trigger_mode)
ADC.set_time_base(1, trigger_mode)

# prepare time data series
time_base = ADC.get_time_base()
time_data = np.arange(0, n_samples * time_base, time_base)  

# prepare waveform display
plt.ion() # interactive mode
fig, waveform = plt.subplots()
waveform.set_ylabel('ADU')
waveform.set_xlabel('t[us]')
waveform.set_ylim(0, 4096)
waveform.set_xlim(0, n_samples * time_base)
waveform.grid()

# trigger ADC conversion and initialize plot
ADC.take_data()
plot1, = waveform.plot(time_data, adc_data)

# define thread function to capture user input
def updatePlot(queue):
  global time_data, n_samples, trigger_mode
  while True:
    if not queue.empty():
      data = queue.get()
      if (data.isdigit() and int(data) in range(1, 6)):
        ADC.set_time_base(int(data), trigger_mode)
        time_base = ADC.get_time_base()
        time_data = np.arange(0, n_samples * time_base, time_base)  
        waveform.set_xlim(0, n_samples * time_base)
    ADC.take_data()
    plot1.set_data(time_data, adc_data)
    time.sleep(0.01)

# add queue to pass data between main and plotting thread
queue = Queue()

# prepare and start user input thread
updateThread = Thread(target=updatePlot, args=(queue,))
updateThread.daemon = True
updateThread.start()

while True:
  print('Press [1,2,3,4,5] to adjust horizontal scale or q to exit.')
  key = input()
  if key == 'q':
    break
  queue.put(key)

plt.close()
ADC.close_device()
GPIO.cleanup()
TRG_THR.close()