import ctypes
import time
import matplotlib.pyplot as plt
import numpy as np
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM) # GPIO port numbering
GPIO.setwarnings(False)

ADC = ctypes.CDLL("./adc.so")

TRIGGER = 4
GPIO.setup(TRIGGER, GPIO.OUT)
GPIO.output(TRIGGER, GPIO.LOW)

# ADC.Hello.restype = ctypes.c_char_p
# print(ADC.Hello().decode())

n_samples = 20000
time_base = 3 # 1 Msps
wait_for_trigger = 0
adc_data = (ctypes.c_uint16 * n_samples)()
adc_data_array = np.array([])

ADC.init_device(adc_data, n_samples, time_base, wait_for_trigger)

for i in range(100):
  #GPIO.output(TRIGGER, GPIO.HIGH)
  ADC.take_data()
  #GPIO.output(TRIGGER, GPIO.LOW)
  adc_data_array = np.append(adc_data_array, adc_data)

plt.ylabel('ADU')
plt.xlabel('t[us]')
plt.plot(adc_data)
#plt.show()
# ADC.close_device()

# ADC.init_device(adc_data, 1000, time_base, wait_for_trigger)

# GPIO.output(TRIGGER, GPIO.HIGH)
# ADC.take_data()
# GPIO.output(TRIGGER, GPIO.LOW)

# set limits (cut the over- and underflow bins)
lower_bound =  100
upper_bound = 3300

# count histogram
adc_hist, bin_edges = np.histogram(adc_data_array, bins=upper_bound-lower_bound, range=(lower_bound,upper_bound-1))

# average bin height 
adc_hist_avg = np.average(adc_hist)

# differential non-linearity
adc_dnl = (adc_hist-adc_hist_avg)/adc_hist_avg

# integral non-linearity
adc_inl = np.cumsum(adc_dnl)

# prepare plots
figure, plot = plt.subplots(3, 1)
plot[0].stairs(adc_hist, bin_edges, fill=True)
plot[0].set_xticks(range(0, 4100, 512))
plot[0].set_ylabel("Counts")
plot[1].stairs(adc_dnl, bin_edges)
plot[1].set_ylim(-2, 2)
plot[1].set_xticks(range(0, 4100, 512))
plot[1].set_ylabel("DNL")
plot[2].stairs(adc_inl, bin_edges)
plot[2].set_ylim(-20, 20)
plot[2].set_xticks(range(0, 4100, 512))
plot[2].set_ylabel("INL")
plt.show()

ADC.close_device()