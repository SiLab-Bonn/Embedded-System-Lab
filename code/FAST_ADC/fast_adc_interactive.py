import ctypes
import matplotlib.pyplot as plt
import numpy as np
from i2cdev import I2C
import RPi.GPIO as GPIO

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
EXT_TRG = 4 # GPIO4 controls external trigger
GPIO.setup(EXT_TRG, GPIO.IN) # disable output 

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
# trigger modes
FREE_RUN_ADC = 0 # take data immediately
TRIGGER_ADC  = 1 # wait for GPIO 24 (DREQ) rising edge, controlled by 
# signal comparator with programmable threshold (jumper INT) or GPIO 4 (jumper EXT)

# trigger threshold DAC
TRG_THR= I2C(0x30, 1)  # init DAC as I2C bus device
TRG_THR.write(b'\200') # set trigger threshold [0..255]
TRG_THR.close() # close device

# init ADC: data array, number of samples, sample rate, trigger mode
n_samples = 1000 # number of samples 
adc_data = (ctypes.c_uint16 * n_samples)() # array to store ADC data
ADC.init_device(adc_data, n_samples, SAMPLE_RATE_5M, TRIGGER_ADC)

# prepare time data series
time_base = ADC.get_time_base()
time_data = np.arange(0, n_samples * time_base, time_base)  

# prepare waveform display
plt.ion() # interactive mode
fig, waveform = plt.subplots()
waveform.set_ylabel('ADU')
waveform.set_xlabel('t[us]')
ADC.take_data()
plot1, = waveform.plot(time_data, adc_data)

# loop ADC acquisition and waveform display update
try:
  while True:
    ADC.take_data()
    plot1.set_data(time_data, adc_data)
    fig.canvas.draw()
    fig.canvas.flush_events()
except:
  pass
  ADC.close_device()
  print("exiting...")