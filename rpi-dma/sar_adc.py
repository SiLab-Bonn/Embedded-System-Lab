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
GPIO.setup(SAMPLE, GPIO.OUT)
GPIO.output(SAMPLE, GPIO.LOW)
COMP = 5  # GPIO5 reads the comparator output
GPIO.setup(COMP, GPIO.IN)

dac_resolution = 8 # resolution in bits
num_samples = 10000 # number of ADC samples

adc_samples = np.zeros(num_samples) # create array to store the ADC data

# loop for number of samples
for i in tqdm(range(num_samples)):
  GPIO.output(SAMPLE, GPIO.HIGH) # close sample switch for the next step (sample mode)
  time.sleep(0.0001)
  GPIO.output(SAMPLE, GPIO.LOW) # disconnect sample capacitor from the input (hold mode)
  dac_value = 0  # reset DAC value

  # successive approximation loop from bit 7 (MSB) down to bit 0 (LSB)
  for dac_bit in reversed(range(dac_resolution)):
    dac_value |= 1 << (dac_bit) # set next DAC bit value
    spi.xfer([dac_value])  # write DAC value 
    #time.sleep(0.0001)
    result = GPIO.input(COMP) # get result from comparator 
    if not (result): # input voltage is lower than DAC voltage
      dac_value -= 1 << (dac_bit)  # subtract DAC bit value
    #print(dac_bit, dac_value, result)

  spi.xfer([dac_value]) # write final DAC value with correct LSB
  adc_samples[i] = dac_value #  write ADC value to sample array

# count histogram
bin_count = 1 << dac_resolution
adc_hist, bin_edges = np.histogram(adc_samples, bins = range(bin_count))

# set limits (cut the over- and underflow bins)
lower_bound =  10
upper_bound = 254

# average bin height 
adc_hist_avg = np.average(adc_hist[lower_bound:upper_bound])

# differential non-linearity
adc_dnl = (adc_hist-adc_hist_avg)/adc_hist_avg
adc_dnl[upper_bound:] = 0
adc_dnl[:lower_bound] = 0
adc_dnl_std = np.std(adc_dnl)
print(adc_dnl_std)

# integral non-linearity
adc_inl = np.cumsum(adc_dnl)

# prepare plots
figure, plot = plt.subplots(3, 1)
plot[0].stairs(adc_hist, bin_edges, fill=True)
plot[0].set_xticks(range(0, 260, 32))
plot[0].set_ylabel("Counts")
plot[0].axvline(x=lower_bound, color='red', linestyle='--')
plot[0].axvline(x=upper_bound, color='red', linestyle='--')
plot[1].stairs(adc_dnl, bin_edges, label = "std = %.2f" % adc_dnl_std)
plot[1].set_ylim(-2, 2)
plot[1].set_xticks(range(0, 260, 32))
plot[1].set_ylabel("DNL")
plot[1].legend()
plot[2].stairs(adc_inl, bin_edges)
plot[2].set_ylim(-2, 2)
plot[2].set_xticks(range(0, 260, 32))
plot[2].set_ylabel("INL")
plt.show()




