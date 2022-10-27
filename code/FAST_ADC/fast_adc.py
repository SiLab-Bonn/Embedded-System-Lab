import ctypes
import time
import matplotlib.pyplot as plt
import numpy as np
import RPi.GPIO as GPIO
from tqdm import tqdm

GPIO.setmode(GPIO.BCM) # GPIO port numbering
GPIO.setwarnings(False)

ADC = ctypes.CDLL("../lib/fast_adc.so")

TRIGGER = 4
GPIO.setup(TRIGGER, GPIO.OUT)
GPIO.output(TRIGGER, GPIO.LOW)

# ADC.Hello.restype = ctypes.c_char_p
# print(ADC.Hello().decode())

n_samples = 1
time_base = 5 # 1 Msps
wait_for_trigger = 0
adc_data = (ctypes.c_uint16 * n_samples)()
adc_data_array = np.array([])

ADC.init_device(adc_data, n_samples, time_base, wait_for_trigger)

for i in tqdm(range(100000)):
  ADC.take_data()
  adc_data_array = np.append(adc_data_array, adc_data)
  
plt.ylabel('ADU')
plt.xlabel('t[us]')
plt.plot(adc_data)
plt.show()

ADC.close_device()