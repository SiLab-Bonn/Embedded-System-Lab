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



GPIO.cleanup()


