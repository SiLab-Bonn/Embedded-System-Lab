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
  # MCP4822/11 DAC samples *first* 16 bits after CS falling edge (MSB first)
  # CPLD SPI shift register *samples* last 8 bits before CS rising edge (MSB first)
  # Both device connect in parallel to the MOSI line (not daisy chained!)

  dac_cmd_a      = 0x3000 # channel A, DAC enable, gain = 1: VDAC = [0..2047]mV, 0.5 mV LSB
  dac_cmd_b      = 0xb000 # channel B, DAC enable, gain = 1: VDAC = [0..2047]mV, 0.5 mV LSB

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

charge    = 300
threshold = 2800

GPIO.output(INJECT, GPIO.LOW)


def threshold_scan(charge, threshold_range, time_constant_range):
  fig, ax = plt.subplots()
  hit_data = []
  threshold_data = []
  for time_constant in time_constant_range:
    for threshold in tqdm(reversed(threshold_range)):
      threshold_data.append(threshold)
    #for charge in range(40, 80, 1):
      update_spi_regs(threshold, charge, time_constant)
      hit_count = 0
      for i in range (100): 
        GPIO.output(INJECT, GPIO.HIGH)
        time.sleep(0.0004) 
        if (GPIO.input(COMP)):
          hit_count = hit_count + 1
        GPIO.output(INJECT, GPIO.LOW)
        time.sleep(0.0008)
      hit_data.append(hit_count)
    ax.plot(threshold_data, hit_data, label=time_constant)
    threshold_data = []
    hit_data = []

  ax.set(xlabel='threshold (DAC)', ylabel='hit count', title='S-Curve')
  ax.legend(title="time constant")
  ax.grid()
  #fig.savefig("test.png")
  plt.show()

def infinite_inject_loop():
  update_spi_regs(2700, 300, 3)
  while True: 
    GPIO.output(INJECT, GPIO.HIGH)
    time.sleep(0.0002) 
    GPIO.output(INJECT, GPIO.LOW)
    time.sleep(0.0002)


threshold_scan(100, range(2200, 2700, 10), range(0,7))



spi.close()
GPIO.cleanup()