import ctypes
import time
import RPi.GPIO as GPIO
# GPIO.setmode(GPIO.BOARD) # pin header numbering
GPIO.setmode(GPIO.BCM) # GPIO port numbering

ADC = ctypes.CDLL("./adc.so")

TRIGGER = 4
GPIO.setup(TRIGGER, GPIO.OUT)
GPIO.output(TRIGGER, GPIO.LOW)

ADC.Hello.restype = ctypes.c_char_p
print(ADC.Hello().decode())

n_samples = 10
time_base = 3 # 1 Msps
wait_for_trigger = 0
adc_data = (ctypes.c_uint16 * n_samples)()

ADC.init_device(adc_data, n_samples, time_base, wait_for_trigger)

GPIO.output(TRIGGER, GPIO.HIGH)
ADC.take_data()
GPIO.output(TRIGGER, GPIO.LOW)


ADC.close_device()

for i in range(n_samples):
    print((adc_data[i]))

