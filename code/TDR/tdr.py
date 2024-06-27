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
  spi_data = ((((0x3ff & threshold) << 2)| dac_cmd) << 24) + \
             ((0x3ff & reverse_bits(pulse_delay,  10)) << 10) + \
             ((0x3ff & reverse_bits(sample_delay, 10)) << 0)
  #print(bin(spi_data))
  spi.xfer(bytearray(spi_data.to_bytes(5, byteorder='big')))

dac_resolution = 10 # resolution in bits

dac_cmd      = 0x3000 # DAC enable, gain = 1: VDAC = [0..2047]mV
threshold    =  512
pulse_delay  =    0
sample_delay =    0
max_delay    =  1024  
max_threshold = 1024
delay_unit   =    5
average = 1

amplitude_data = np.zeros(max_delay)
time_steps = np.zeros(max_delay)

# plot the waveform data
plt.ion()
fig, waveform = plt.subplots(2,1)
plot1, = waveform[0].plot(time_steps, amplitude_data)
waveform[0].set_xlabel("time [ps]")
waveform[0].set_ylabel("voltage [#DAC]")
waveform[0].set_xlim(0, max_delay * delay_unit)
waveform[0].set_ylim(0, 1100)
plot2, = waveform[1].plot(time_steps, amplitude_data)
waveform[1].set_xlabel("time [ps]")
waveform[1].set_ylabel("voltage [#DAC]")
waveform[1].set_xlim(0, max_delay * delay_unit)
waveform[1].set_ylim(350, 850)


while True:
  amplitude_data = [0]
  time_steps = [0]
  for sample_delay in tqdm(range(max_delay)):
    time_steps = np.append(time_steps, [sample_delay * delay_unit])
    average_threshold = 0

    for avg in range(average):
      threshold = 512 # start SAR ADC conversion with MSB set to '1'

      for dac_bit in reversed(range(dac_resolution)): # SAR conversion from MSB to LSB
        #set DAC value
        threshold |= 1 << (dac_bit)
        # update comparator threshold
        update_spi_regs(threshold, pulse_delay, sample_delay)
        # trigger pulse step
        GPIO.output(TRIGGER, GPIO.HIGH)
        # read comparator result
        result = GPIO.input(COMP)
        # reset pulse output
        GPIO.output(TRIGGER, GPIO.LOW)

        if result: # set next DAC bit, VTHR ~ 3.1V - VDAC/k
          threshold -= 1 << (dac_bit)
      
      average_threshold += threshold/average

    amplitude_data = np.append(amplitude_data, [max_threshold - average_threshold])


  plot1.set_data(time_steps, amplitude_data)
  plot2.set_data(time_steps, amplitude_data)
  fig.canvas.draw()
  fig.canvas.flush_events()




