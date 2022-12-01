import time
from i2cdev import I2C
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

# source voltage DAC
DAC = I2C(0x60, 1)  # init DAC as I2C bus device
DAC.write(b'\x40\x00\x05') # external VREF, unbuffered
DAC.write(b'\x50\x00\x00') # gain = 1
#DAC.write(b'\x50\x03\x00') # gain = 2
#DAC.write(b'\x00\x00\x03') # set output of channel 0
#DAC.write(b'\x08\x07\xff') # set output of channel 1

#DAC.close() # close device