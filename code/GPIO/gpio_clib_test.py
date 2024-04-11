import ctypes
import matplotlib.pyplot as plt
import numpy as np
import time

# access to c-library for enhanced GPIO access 
GPIO_CLIB = ctypes.CDLL("/home/pi/Embedded-System-Lab/code/lib/gpio_clib.so")  

GPIO_MODE_IN   = 0 
GPIO_MODE_OUT  = 1 
GPIO_MODE_ALT0 = 4 

BLUE_LED = 27
CLK      = 4    # GPIO pin for clock output
frequency = 15  # [kHz]

# initialize GPIO register access
GPIO_CLIB.setup()

GPIO_CLIB.set_gpio_mode(BLUE_LED, GPIO_MODE_OUT)
GPIO_CLIB.set_gpio_mode(CLK, GPIO_MODE_ALT0) 
GPIO_CLIB.set_gpclk_freq(frequency) 
GPIO_CLIB.set_gpio_out(BLUE_LED, 1)
input('Hit enter to exit')
GPIO_CLIB.set_gpio_out(BLUE_LED, 0)
GPIO_CLIB.set_gpclk_freq(0) # freq = 0 switches the clock off

# restore default GPIO mode (input)
GPIO_CLIB.set_gpio_mode(BLUE_LED, GPIO_MODE_IN)
GPIO_CLIB.set_gpio_mode(CLK, GPIO_MODE_IN) 