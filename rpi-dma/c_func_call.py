import ctypes
import time

so_file = "/home/pi/piLab/rpi/c_func.so"
c_func = ctypes.CDLL(so_file)

#c_func.Hello.restype = ctypes.c_char_p
#print(c_func.Hello().decode())

n_samples = 20
time_base = 3 # 1 Msps
adc_data = (ctypes.c_int16 * n_samples)()

c_func.ADC_init(adc_data, n_samples, time_base)
#for i in range(10):
c_func.ADC_take_data()
c_func.ADC_close()

for i in range(n_samples):
    print(adc_data[i])

