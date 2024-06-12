import time
import RPi.GPIO as GPIO
import spidev as SPI
import matplotlib.pyplot as plt
import numpy as np
import scipy
from scipy.optimize import curve_fit
from tqdm import tqdm


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

spi = SPI.SpiDev()
spi.open(0,0)  # (bus, device)
spi.mode = 0
spi.max_speed_hz = 5000000

COMP = 5
GPIO.setup(COMP, GPIO.IN)
INJECT = 4
GPIO.setup(INJECT, GPIO.OUT)
GPIO.output(INJECT, GPIO.LOW)

time_constants_list = [0.1, 0.2, 0.5, 1, 2, 5, 10, 20]
out_mux_dict = {
  'csa':  0, 
  'hpf':  1, 
  'sha':  2, 
  'comp': 3}

def update_spi_regs(threshold, injected_signal, time_constant, out_mux):
  # the SPI bus connects to two devices:
  #  - Dual channel 12-bit DAC that controlls the threshold voltage and the injected signal level
  #  - A shift register in the CPLD that controls the selection bits for the shaper time constant 
  #    and the output multiplexer
  #
  # MCP4822 DAC samples *first* 16 bits after CS falling edge (MSB first)
  # CPLD SPI shift register *samples* last 8 bits before CS rising edge (MSB first)
  # Both device connect in parallel to the MOSI line (not daisy chained!)

  dac_cmd_a      = 0x3000 # channel A, DAC enable, gain = 1: VDAC = [0..2047]mV, 0.5 mV LSB
  dac_cmd_b      = 0xb000 # channel B, DAC enable, gain = 1: VDAC = [0..2047]mV, 0.5 mV LSB

  out_mux_val = out_mux_dict[out_mux]

  #set DAC channel A (threshold voltage)
  spi_data = ((((0xfff & int(threshold)) | dac_cmd_a) << 8) + \
                ( 0x07 & time_constant) | ((0x03 & out_mux_val) << 3))
  #print(bin(spi_data)[2:].zfill(24))
  spi.xfer(bytearray(spi_data.to_bytes(3, byteorder='big')))

  #set DAC channel B (injection signal)
  spi_data = ((((0xfff & int(injected_signal)) | dac_cmd_b) << 8) + \
                ( 0x07 & time_constant) | ((0x03 & out_mux_val) << 3))
  #print(bin(spi_data)[2:].zfill(24))
  spi.xfer(bytearray(spi_data.to_bytes(3, byteorder='big')))

charge    = 180
threshold = 2600
time_constant = 5
n_injections = 100
monitor = 'sha'

update_spi_regs(threshold, charge, time_constant, monitor)
hit_count = 0
for i in range(n_injections): 
  GPIO.output(INJECT, GPIO.HIGH) # inject charge
  time.sleep(0.0001) 
  if (GPIO.input(COMP)):         # read latched comparator output
    hit_count = hit_count + 1    
  GPIO.output(INJECT, GPIO.LOW)  # reset charge injection and hit latch 
  time.sleep(0.0001)

print('Hit probability: ', hit_count/n_injections)


spi.close()
GPIO.cleanup()