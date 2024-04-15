import ctypes
import matplotlib.pyplot as plt
import numpy as np
import time

# access to c-library for enhanced GPIO access 
GPIO_CLIB = ctypes.CDLL("/home/pi/Embedded-System-Lab/code/lib/gpio_clib.so")  

GPIO_MODE_IN   = 0 
GPIO_MODE_OUT  = 1 
GPIO_MODE_ALT0 = 4 

# SPI clock
SCK   = 11
MOSI  = 10
MISO  = 9
CS0_B = 8

GPIO_CLIB.setup()

GPIO_CLIB.set_gpio_mode(SCK,   GPIO_MODE_ALT0)
GPIO_CLIB.set_gpio_mode(MOSI,  GPIO_MODE_ALT0) 
GPIO_CLIB.set_gpio_mode(MISO,  GPIO_MODE_ALT0) 
GPIO_CLIB.set_gpio_mode(CS0_B, GPIO_MODE_ALT0)
