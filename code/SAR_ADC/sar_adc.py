import time
import RPi.GPIO as GPIO
import spidev as SPI
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import sys
from tqdm import tqdm

sys.path.insert(1, '/home/pi/Embedded-System-Lab/code/SMU')
from smu_class import SMU

# voltage source with current measurement
smu = SMU()
cvm = smu.ch[0]
cvm.enable_autorange()



# SPI bus setup
spi = SPI.SpiDev()
spi.open(0,0)  # (bus, device)
spi.mode = 0
spi.max_speed_hz = 100000

# GPIO ports setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
SAMPLE = 4 # GPIO4 controls sample switch
COMP   = 5 # GPIO5 reads the comparator output
GPIO.setup(COMP, GPIO.IN)
GPIO.setup(SAMPLE, GPIO.OUT) 
GPIO.output(SAMPLE, GPIO.LOW) # open switch



cvm.set_voltage(1500) # mV units

def write_dac(value):
  spi.xfer([value])  # write DAC register




# # prepare plots for Exercise 4
# adc_hist = [10,8,10,12]
# bin_edges = [1,2,3,4,5]
# lower_bound = 2
# upper_bound = 4
# figure, plot = plt.subplots(1, 1)
# plot.stairs(adc_hist, bin_edges, fill=True)
# plot.set_xticks(range(0, 260, 32))
# plot.set_ylabel("Counts")
# plot.axvline(x=lower_bound, color='red', linestyle='--')
# plot.axvline(x=upper_bound, color='red', linestyle='--')

# plt.show()

GPIO.cleanup()


