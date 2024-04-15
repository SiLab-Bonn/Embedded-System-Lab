import ctypes
import matplotlib.pyplot as plt
import numpy as np
from i2cdev import I2C
import RPi.GPIO as GPIO

# GPIO ports setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
EXT_TRG = 4 # GPIO4 controls external trigger
GPIO.setup(EXT_TRG, GPIO.IN) # disable output 

TRG_THR= I2C(0x30, 1)  

# access to c-library for fast ADC access with DMA support
ADC = ctypes.CDLL("/home/pi/Embedded-System-Lab/code/lib/fast_adc.so")  
# set return type for time base getter
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
# signal comparator with programmable threshold (jumper INPUT) or GPIO trigger/echo (jumper GPIO4 / GPIO5)

# ADC.Hello.restype = ctypes.c_char_p
# print(ADC.Hello().decode())

n_samples = 10000 # number of samples 
adc_data = (ctypes.c_uint16 * n_samples)() # array to store ADC data

# set trigger threshold [0..255]
#TRG_THR.write(bytes([100])) 
TRG_THR.write(b'\20') 

# init ADC: data array, number of samples, sample rate, trigger mode
ADC.init_device(adc_data, n_samples, SAMPLE_RATE_1M, TRIGGER_ADC)

# prepare data series
time_base = ADC.get_time_base()
time_data = np.arange(0, n_samples * time_base, time_base)

# run the ADC
ADC.take_data()

# prepare waveform display
fig, plot = plt.subplots()
plot.plot(time_data, adc_data)
plot.set_ylabel('ADU')
plot.set_xlabel('t[us]')

# waveform display
plt.show()

ADC.close_device()
TRG_THR.close()
GPIO.cleanup()
print("exiting...")