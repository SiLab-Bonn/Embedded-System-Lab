import time
import RPi.GPIO as GPIO
import spidev as SPI
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

spi = SPI.SpiDev()
spi.open(0,0)  # (bus, device)
spi.mode = 0
spi.max_speed_hz = 5000000

COMP = 5
GPIO.setup(COMP, GPIO.IN)
TRIGGER = 4
GPIO.setup(TRIGGER, GPIO.OUT)
GPIO.output(TRIGGER, GPIO.LOW)

dac_resolution =  10 # threshold DAC resolution
max_threshold = 1024 # maximum threshold value DAC counts 
pulse_delay   =    0 # keep constant at 0
sample_delay  =    0 # parameter to scan the sampling time
max_delay     = 1024 # maximum sampling time delay
delay_step    =    5 # delay step in ps
Z0            =   50 # characteristic impedance of the system

def reverse_bits(num, bits):
    result = 0
    for i in range(bits):
        result = (result << 1) + (num & 1)
        num >>= 1
    return result

def update_spi_regs(threshold, pulse_delay, sample_delay):
  # MCP4811 DAC samples first 16 bits after CS falling edge (MSB first)
  # SY89297 delay line samples last 20 bits before CS rising edge (LSB first)
  # Both device connect in parallel to the MOSI line (not daisy chained!)
  dac_cmd  = 0x3000 # DAC enable, gain = 1: VDAC = [0..2047]mV
  spi_data = ((((0x3ff & threshold) << 2)| dac_cmd) << 24) + \
             ((0x3ff & reverse_bits(pulse_delay,  10)) << 10) + \
             ((0x3ff & reverse_bits(sample_delay, 10)) << 0)
  #print(bin(spi_data))
  spi.xfer(bytearray(spi_data.to_bytes(5, byteorder='big')))

GPIO.output(TRIGGER, GPIO.LOW)

sample_delay = 0 # for static measurement of the low level
#sample_delay = 1000 # for static measurement of the high level


# SAR loop
threshold = 512 # start SAR ADC conversion with MSB set to '1'
for dac_bit in reversed(range(dac_resolution)): # SAR conversion from MSB to LSB
  # set DAC value
  threshold |= 1 << (dac_bit)
  # update comparator threshold
  update_spi_regs(threshold, pulse_delay, sample_delay)
  # trigger comparator
  GPIO.output(TRIGGER, GPIO.HIGH)
  # read comparator result
  result = GPIO.input(COMP)
  if result: # set next DAC bit, VTHR ~ 3.1V - VDAC/k
    threshold -= 1 << (dac_bit)
  # reset trigger
  GPIO.output(TRIGGER, GPIO.LOW)

print("VRX = %d [DAC]" %(threshold))

# clean up
spi.close()
GPIO.cleanup()

