import ctypes
import matplotlib.pyplot as plt
import numpy as np
import time


# access to c-library for enhanced GPIO access 
GPIO = ctypes.CDLL("../lib/gpio_clib.so")  

BLUE_LED = 27

GPIO.setup()

GPIO.set_gpio_mode(BLUE_LED, 1)#GPIO.GPIO_MODE_OUT)
GPIO.set_gpio_out(BLUE_LED, 1)
time.sleep(1)
GPIO.set_gpio_out(BLUE_LED, 0)


GPIO.cleanup()