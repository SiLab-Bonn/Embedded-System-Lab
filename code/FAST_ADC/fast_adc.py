import ctypes
import time
import matplotlib.pyplot as plt
import numpy as np
import RPi.GPIO as GPIO
from tqdm import tqdm

GPIO.setmode(GPIO.BCM) # GPIO port numbering
GPIO.setwarnings(False)

ADC = ctypes.CDLL("../lib/fast_adc.so")  # access to c-library for fast ADC access with DMA support
ADC.get_time_base.restype = ctypes.c_float # set return type for time base getter

time_dict={
  "200k" : 1,
  "500k" : 2,
  "1M"   : 3,
  "2M"   : 4,
  "5M"   : 5
}

TRIGGER = 4
GPIO.setup(TRIGGER, GPIO.OUT)
GPIO.output(TRIGGER, GPIO.LOW)

# ADC.Hello.restype = ctypes.c_char_p
# print(ADC.Hello().decode())

n_samples = 10000 # number of samples 
#time_base = 1 # [1, 2, 3, 4, 5] = [200k, 500k 1M, 2M, 5M] samples per second
wait_for_trigger = 0 # 0: take data immediately, 1: wait for line 24 (DREQ) to go high
adc_data = (ctypes.c_uint16 * n_samples)()

ADC.init_device(adc_data, n_samples, 4, wait_for_trigger)
ADC.take_data()

time_base = ADC.get_time_base()
time_data = np.arange(0, n_samples * time_base, time_base)
adc_data  = np.array(adc_data)

# plot ADC waveform data 
plt.ylabel('ADU')
plt.xlabel('t[us]')
plt.plot(time_data, adc_data)
plt.show()

ADC.close_device()