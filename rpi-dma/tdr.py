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
spi.max_speed_hz = 1000000

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
delay_size = 1 # number of delay steps

dac_cmd      = 0x3000 # DAC enable, gain = 1: VDAC = [0..2047]mV
threshold    = 2048
pulse_delay  =  0
sample_delay =    0
max_delay    =  1023  
max_threshold = 4095
delay_unit   =    5

# update_spi_regs(3000, pulse_delay, sample_delay)
# GPIO.output(TRIGGER, GPIO.HIGH)
# GPIO.output(TRIGGER, GPIO.LOW)

amplitude_data = np.array([])
time_steps = np.array([])

for sample_delay in tqdm(range(max_delay)):
  time_steps = np.append(time_steps, [sample_delay * delay_unit])
  threshold = 2048 # start with mid-level DAC output for SAR ADC conversion

  for dac_bit in reversed(range(dac_resolution)): # SAR conversion from MSB to LSB
    #set DAC value
    threshold |= 1 << (dac_bit)
    # update comparator threshold
    update_spi_regs(threshold, pulse_delay, sample_delay)

    # trigger pulse step
    GPIO.output(TRIGGER, GPIO.HIGH)
    time.sleep(0.0005)
    # sample comparator result
    result = GPIO.input(COMP)
    # reset pulse output
    GPIO.output(TRIGGER, GPIO.LOW)

    if result: # set next DAC bit
      threshold -= 1 << (dac_bit)

  amplitude_data = np.append(amplitude_data, [max_threshold - threshold])

# plot the waveform data
fig, waveform = plt.subplots(2,1)
waveform[0].plot(time_steps, amplitude_data)
waveform[0].set_xlabel("time [ps]")
waveform[0].set_ylabel("voltage [#DAC]")
waveform[0].set_ylim(2500, 4500)
waveform[1].plot(time_steps, amplitude_data)
waveform[1].set_xlabel("time [ps]")
waveform[1].set_ylabel("voltage [#DAC]")
waveform[1].set_ylim(3500, 4000)

plt.show()


spi.close()


