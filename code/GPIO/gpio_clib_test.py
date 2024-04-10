import ctypes
import matplotlib.pyplot as plt
import numpy as np
import time


# access to c-library for enhanced GPIO access 
GPIO = ctypes.CDLL("../lib/gpio_clib.so")  

BLUE_LED = 27
CLK = 4            # GPIO pin for clock output
GPIO_MODE_ALT0 = 4 # GPIO alternative mode 0 (GPCLK0 on GPIO 4)
frequency = 100 # [kHz]
GPIO.setup()

GPIO.set_gpio_mode(BLUE_LED, 1)#GPIO.GPIO_MODE_OUT)
GPIO.set_gpio_mode(CLK, GPIO_MODE_ALT0) 
GPIO.set_gpclk_freq(int(frequency)) 
GPIO.set_gpio_out(BLUE_LED, 1)
input('Hit enter to exit')
GPIO.set_gpio_out(BLUE_LED, 0)

GPIO.set_gpclk_freq(0) # switch off
GPIO.cleanup(0)