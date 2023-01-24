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
INJECT = 4
GPIO.setup(INJECT, GPIO.OUT)
GPIO.output(INJECT, GPIO.LOW)

def update_spi_regs(threshold, injected_signal, time_constant):
  # MCP4822/11 DAC samples first 16 bits after CS falling edge (MSB first)
  # SN74HCS594 shift register samples last 8 bits before CS rising edge (MSB first)
  # Both device connect in parallel to the MOSI line (not daisy chained!)

  dac_cmd_a      = 0x1000 # channel A, DAC enable, gain = 2: VDAC = [0..4095]mV
  dac_cmd_b      = 0x9000 # channel B, DAC enable, gain = 2: VDAC = [0..4095]mV

  #set DAC channel A (threshold voltage)
  spi_data = ((((0xfff & threshold) | dac_cmd_a) << 8) + \
                ( 0x07 & time_constant))
  #print(bin(spi_data)[2:].zfill(24))
  spi.xfer(bytearray(spi_data.to_bytes(3, byteorder='big')))

  #set DAC channel B (injection signal)
  spi_data = ((((0xfff & injected_signal) | dac_cmd_b) << 8) + \
                ( 0x07 & time_constant))
  #print(bin(spi_data)[2:].zfill(24))
  spi.xfer(bytearray(spi_data.to_bytes(3, byteorder='big')))

update_spi_regs(600, 100, 6)

while True:
  for tau in range(8):
    update_spi_regs(450, 150, tau)
    for i in range (1000): 
      GPIO.output(INJECT, GPIO.HIGH)
      time.sleep(0.0005)
      GPIO.output(INJECT, GPIO.LOW)
      time.sleep(0.0005)

spi.close()