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
  spi_data = ((threshold | dac_cmd) << 24) + \
             ((0x3ff & reverse_bits(pulse_delay,  10)) << 10) + \
             ((0x3ff & reverse_bits(sample_delay, 10)) << 0)
  #print(bin(spi_data))
  spi.xfer(bytearray(spi_data.to_bytes(5, byteorder='big')))

dac_resolution = 12 # resolution in bits
delay_size = 1 # numer of delay steps

spi_array = bytearray(6)
dac_value   = 0
delay_value = 0
spi_array = [dac_value >> 8, dac_value & 0xff, delay_value >> 8, delay_value & 0xff]
 

TRIGGER = 4
GPIO.setup(TRIGGER, GPIO.OUT)
GPIO.output(TRIGGER, GPIO.LOW)

COMP = 5
GPIO.setup(COMP, GPIO.IN)

for t in range(delay_size):
  #set delay value
  delay_value = t
  spi_array = [dac_value >> 8, dac_value & 0xff, delay_value >> 8, delay_value & 0xff]
  spi.xfer(spi_array)
  #reset dac output 
  dac_value = 0

  for dac_bit in reversed(range(dac_resolution)):
    #set DAC value
    dac_value |= 1 << (dac_bit)
    spi_array = [dac_value >> 8, dac_value & 0xff, delay_value >> 8, delay_value & 0xff]
    spi.xfer(spi_array)

    # trigger pulse step
    GPIO.output(TRIGGER, GPIO.HIGH)
    GPIO.output(TRIGGER, GPIO.LOW)

    result = 253 >= dac_value #GPIO.input(COMP)
    print(dac_bit, dac_value, result)
    if not result:
      dac_value -= 1 << (dac_bit)
print("dac_value", dac_value)




