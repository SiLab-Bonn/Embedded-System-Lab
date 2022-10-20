import time
import RPi.GPIO as GPIO
import spidev as SPI
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

GPIO.setmode(GPIO.BCM)

spi = SPI.SpiDev()
spi.open(0,0)  # (bus, device)
spi.mode = 0
spi.max_speed_hz = 1000000

dac_resolution = 8 # resolution in bits

SAMPLE = 4 # GPIO4
GPIO.setwarnings(False)
GPIO.setup(SAMPLE, GPIO.OUT)
GPIO.output(SAMPLE, GPIO.LOW)

COMP = 5  # GPIO5
GPIO.setup(COMP, GPIO.IN)

adc_data = np.array([])

for i in tqdm(range(10000)):
  # trigger sample switch
  GPIO.output(SAMPLE, GPIO.HIGH)
  time.sleep(0.0001)
  GPIO.output(SAMPLE, GPIO.LOW)

  # reset dac value
  dac_value = 0

  # successive approximation loop from bit 7 (MSB) down to bit 0 (LSB)
  for dac_bit in reversed(range(dac_resolution)):
    # set next DAC bit value
    dac_value |= 1 << (dac_bit) 
    # write DAC value 
    spi.xfer([dac_value])
    #time.sleep(0.0001) # settling time for DAC and comparator

    # get result from comparator 
    result = GPIO.input(COMP)
    if not (result): # input voltage is lower than DAC voltage
      dac_value -= 1 << (dac_bit)  # subtract DAC bit value
    #print(dac_bit, dac_value, result)

  spi.xfer([dac_value]) # write final DAC value with correct LSB
  adc_data = np.append(adc_data, [dac_value])
  #time.sleep(0.1)

# set limits (cut the over- and underflow bins)
lower_bound = 10
upper_bound = 254

# count histogram
adc_hist, bin_edges = np.histogram(adc_data, bins=upper_bound-lower_bound, range=(lower_bound,upper_bound-1))

# average bin height 
adc_hist_avg = np.average(adc_hist)

# differential non-linearity
adc_dnl = (adc_hist-adc_hist_avg)/adc_hist_avg

# integral non-linearity
adc_inl = np.cumsum(adc_dnl)

# prepare plots
figure, plot = plt.subplots(3, 1)
plot[0].stairs(adc_hist, bin_edges, fill=True)
plot[0].set_xticks(range(0, 260, 32))
plot[0].set_ylabel("Counts")
plot[1].stairs(adc_dnl, bin_edges)
plot[1].set_ylim(-2, 2)
plot[1].set_xticks(range(0, 260, 32))
plot[1].set_ylabel("DNL")
plot[2].stairs(adc_inl, bin_edges)
plot[2].set_ylim(-2, 2)
plot[2].set_xticks(range(0, 260, 32))
plot[2].set_ylabel("INL")
plt.show()




