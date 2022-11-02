import ctypes
import time
import matplotlib.pyplot as plt
import numpy as np
import RPi.GPIO as GPIO
from i2cdev import I2C
from tqdm import tqdm

GPIO.setmode(GPIO.BCM) # GPIO port numbering
GPIO.setwarnings(False)

THR_DAC = I2C(0x30, 1)

THR_DAC.write(bytes([255]))
THR_DAC.close()

ADC = ctypes.CDLL("../lib/fast_adc.so")  # access to c-library for fast ADC access with DMA support
ADC.get_time_base.restype = ctypes.c_float # set return type for time base getter

SAMPLE_RATE_200k = 1
SAMPLE_RATE_500k = 2
SAMPLE_RATE_1M   = 3
SAMPLE_RATE_2M   = 4
SAMPLE_RATE_5M   = 5

TRIGGER = 4
GPIO.setup(TRIGGER, GPIO.OUT)
GPIO.output(TRIGGER, GPIO.HIGH)

# ADC.Hello.restype = ctypes.c_char_p
# print(ADC.Hello().decode())

n_samples = 5000 # number of samples 
wait_for_trigger = 1 # 0: take data immediately, 1: wait for line 24 (DREQ) to go high
adc_data = (ctypes.c_uint16 * n_samples)()

ADC.init_device(adc_data, n_samples, SAMPLE_RATE_200k, wait_for_trigger)
ADC.take_data()

# prepare data series
time_base = ADC.get_time_base()
time_data = np.arange(0, n_samples * time_base, time_base)
adc_data  = np.array(adc_data)

# plot ADC waveform data 
plt.ylabel('ADU')
plt.xlabel('t[us]')
plt.plot(time_data, adc_data)
plt.show()

ADC.close_device()