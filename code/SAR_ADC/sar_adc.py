import time
import RPi.GPIO as GPIO
import spidev as SPI
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm


# SPI bus setup
spi = SPI.SpiDev()
spi.open(0,0)  # (bus, device)
spi.mode = 0
spi.max_speed_hz = 1000000

# GPIO ports setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
SAMPLE = 4 # GPIO4 controls sample switch
COMP   = 5 # GPIO5 reads the comparator output
GPIO.setup(COMP, GPIO.IN)
GPIO.setup(SAMPLE, GPIO.OUT)
GPIO.output(SAMPLE, GPIO.LOW)


# prepare plots
adc_hist = [10,8,10,12]
bin_edges = [1,2,3,4,5]
lower_bound = 2
upper_bound = 4
figure, plot = plt.subplots(1, 1)
plot[0].stairs(adc_hist, bin_edges, fill=True)
plot[0].set_xticks(range(0, 260, 32))
plot[0].set_ylabel("Counts")
plot[0].axvline(x=lower_bound, color='red', linestyle='--')
plot[0].axvline(x=upper_bound, color='red', linestyle='--')

plt.show()




