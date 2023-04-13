import time
import RPi.GPIO as GPIO
import spidev as SPI
import logging
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm


#logging.basicConfig(level = logging.DEBUG, format='%(message)s')
#logging.debug("logging is on")

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
num_samples = 1000 # number of ADC samples

adc_samples = np.zeros(num_samples) # create array to store the ADC data

def write_dac(value):
  spi.xfer([value])  # write DAC register 

def sar_loop(resolution):
  dac_register_array = []                     # array for storing intermediate DAC register values for plotting
  dac_register = 0                             # initialize DAC value 
  for dac_bit in reversed(range(resolution)):  # successive approximation loop from bit n-1 down to bit 0
    dac_register |= 1 << (dac_bit)             # set next DAC register bit 
    write_dac(dac_register)                    # update DAC register
    dac_register_array.append(dac_register)
    time.sleep(0.0001)                         # wait for comparator to settle
    comp_out = GPIO.input(COMP)                # read comparator output
    if (not comp_out):                         # subtract current DAC bit if DAC voltage is higher than input voltage
      dac_register -= 1 << (dac_bit)           
  write_dac(dac_register)                      # final DAC register update
  return dac_register, dac_register_array

def plot_dac_register_array(value, array):
  fig, ax = plt.subplots()
  x = [i for i in (range(len(array)))]
  ax.step(x, array, where='mid')
  ax.set(xlabel='Conversion cycle', ylabel='DAC register',
        title='Successive Approximation')
  ax.set_ylim(0, 255)
  ax.axhline(y=value, color='red', linestyle='--')
  ax.grid()
  #fig.savefig("test.png")
  plt.show()
  

def read_adc():
  GPIO.output(SAMPLE, GPIO.HIGH) # close sample switch (sample mode)
  time.sleep(0.0001)
  GPIO.output(SAMPLE, GPIO.LOW)  # open sample switch (hold mode)
  adc_value = sar_loop(8)
  return adc_value

def nl_analysis():
  # loop for number of samples
  for i in tqdm(range(num_samples)):
    adc_value = read_adc()
    adc_samples[i] = adc_value #  write ADC value to sample array

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



while 1:
  print("Select: write_dac[1], read_adc[2], dac_loop[3], read_adc with plot[4], exit[q] ")
  x = input()
  if (x == '1'):
    while 1:
      y = input("Enter DAC value ('q' to exit): ")
      if (y == 'q'):
        break
      write_dac(int(y,0))
  if (x == '2'): 
    while 1:
      y = input("Press enter to read ADC value ('q' to exit): ")
      if (y == 'q'):
        break
      print(read_adc())
  if (x == '3'):
    while 1:
      y = input("Press enter to loop DAC values ('CTRL+c' to exit): ")
      while 1:
        for i in range(255):
          write_dac(i)
  if (x == '4'): 
    while 1:
      y = input("Press enter to read ADC value ('q' to exit): ")
      if (y == 'q'):
        break
      value, array = read_adc()
      plot_dac_register_array(value, array)

  if (x=='q'):  
    break





