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

dac_resolution = 8  # resolution in bits
num_samples = 1000 # number of ADC samples for INL/DNL analysis

resolution = dac_resolution  # default resolution 

def write_dac(value):
  spi.xfer([value])  # write DAC register 

def sar_loop(resolution = dac_resolution):
  dac_register_array = []                      # array for storing intermediate DAC register values for plotting
  dac_register = 0                             # initialize DAC value 
  res_offest = dac_resolution-resolution       # offset between max. resolution and selected resolution
  dac_bit_list = range(res_offest, dac_resolution) # list of DAC bits          
  for dac_bit in reversed(dac_bit_list):       # successive approximation loop from bit n-1 down to bit 0
    dac_register |= 1 << (dac_bit)             # set next DAC register bit 
    write_dac(dac_register)                    # update DAC register
    dac_register_array.append(dac_register >> res_offest)    # store current dac register value for later plotting
    time.sleep(0.001)                          # wait for comparator to settle
    comp_out = GPIO.input(COMP)                # read comparator output
    if (not comp_out):                         # subtract current DAC bit if DAC voltage is higher than input voltage
      dac_register -= 1 << (dac_bit)           
  write_dac(dac_register)                      # final DAC register update
  return (dac_register >> res_offest), dac_register_array

def read_adc(resolution = dac_resolution):
  resolution = min(dac_resolution, resolution)
  GPIO.output(SAMPLE, GPIO.HIGH) # close sample switch (sample mode)
  time.sleep(0.0001)
  GPIO.output(SAMPLE, GPIO.LOW)  # open sample switch (hold mode)
  return sar_loop(resolution)

def adc_analysis(resolution = dac_resolution):
  adc_samples = np.zeros(num_samples) # create array to store the ADC data

  # loop for number of samples
  for i in tqdm(range(num_samples)):
    adc_value, __ = read_adc(resolution)
    adc_samples[i] = adc_value #  write ADC value to sample array

  # count histogram
  bin_count = 1 << resolution
  adc_hist, bin_edges = np.histogram(adc_samples, bins = range(bin_count))

  # set limits (cut the over- and underflow bins)
  lower_bound = 10 # int(bin_count / 20)
  upper_bound = 250 # bin_count - 2

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
  plt.ion()       # interactive plot mode
  figure, plot = plt.subplots(3, 1)
  plot[0].stairs(adc_hist, bin_edges, fill=True)
  plot[0].set_xticks(range(0, bin_count, bin_count>>3))
  plot[0].set_ylabel("Counts")
  plot[0].axvline(x=lower_bound, color='red', linestyle='--')
  plot[0].axvline(x=upper_bound, color='red', linestyle='--')
  plot[1].stairs(adc_dnl, bin_edges, label = "std = %.2f" % adc_dnl_std)
  plot[1].set_ylim(-2, 2)
  plot[1].set_xticks(range(0, bin_count,  bin_count>>3))
  plot[1].set_ylabel("DNL")
  plot[1].legend()
  plot[2].stairs(adc_inl, bin_edges)
  plot[2].set_ylim(-5, 5)
  plot[2].set_xticks(range(0, bin_count,  bin_count>>3))
  plot[2].set_ylabel("INL")
  plt.show()

def dac_analysis(dac_binary_voltages_list):
  # plot dac transfer function from mesaured output voltages
  dac_bits  = len(dac_binary_voltages_list)  # number of bits
  dac_steps = 1 << dac_bits                  # number of DAC codes
  x = [i for i in (range(dac_steps))]        # dac code array
  dac_voltage_list = []                      # prepare output voltage array

  for i in range(dac_steps):                 # calculate DAC output voltages from binray weights
    dac_voltage = 0
    for bit in range(dac_bits):
      dac_voltage = dac_voltage + (0x01 & (i >> bit)) * dac_binary_voltages_list[bit]
    dac_voltage_list.append(dac_voltage)

  dac_diff = np.diff(dac_voltage_list)       # difference between voltage steps
  dac_diff_avg = np.average(dac_diff)        # average difference
  dac_dnl = (dac_diff - dac_diff_avg)/dac_diff_avg  # calculate DNL
  dac_inl = np.cumsum(dac_dnl)               # calcultae INL

  #plt.ion()
  fig, plot = plt.subplots(3,1)
  plot[0].set(ylabel='DAC output voltage', title='DAC Analysis')
  plot[0].grid()
  plot[0].step(x, dac_voltage_list, where='mid')
  plot[0].set_xticks(range(0, dac_steps+1,  dac_steps>>3))  
  plot[1].set(ylabel='DNL')
  plot[1].grid()
  plot[1].step(x[1:], dac_dnl, where='mid')  
  plot[1].set_xticks(range(0, dac_steps+1,  dac_steps>>3))  
  plot[2].set(xlabel='DAC code', ylabel='INL')
  plot[2].grid()
  plot[2].step(x[1:], dac_inl, where='mid')  
  plot[2].set_xticks(range(0, dac_steps+1,  dac_steps>>3))  
  plt.show()


while 1:
  print("Select:\n[1] Write DAC\n[2] Read ADC\n[3] DAC loop\n[4] Read ADC and plot\n\
[5] Analyze ADC INL / DNL\n[6] Set resolution (default = 8)\n[7] Analyze DAC INL / DNL\n[q] Exit")
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
      result, __ = read_adc(resolution)
      print(result)
  
  if (x == '3'):
    while 1:
      y = input("Press enter to loop DAC values ('CTRL+c' to exit): ")
      while 1:
        for i in range(255):
          write_dac(i)
  
  if (x == '4'): 
    plt.ion()
    fig, ax = plt.subplots()
    ax.set(xlabel='Conversion cycle', ylabel='DAC register', title='Successive Approximation')
    ax.set_ylim(0, 255)
    ax.grid()
    value, array = read_adc(resolution)
    x = [i for i in (range(len(array)))]
    result_line = ax.axhline(y=value, color='red', linestyle='--')
    plot, = ax.step(x, array, where='mid', label = "result = %.d" % value)
    ax.set_yticks(range(0, (1 << resolution)+1,  (1 << (resolution-3))))  
    ax.legend()
    plt.show()
    while 1:  # loop to update plot interactively
      y = input("Press enter to read ADC value and plot ('q' to exit): ")
      if (y == 'q'):
        plt.close()
        break
      value, array = read_adc(resolution)
      result_line.set_ydata(value)
      plot.set_ydata(array)
      plot.set_label("result = %.d" % value)

  if (x == '5'):
    while 1:
      y = input("Enter sample number to run INL/DNL analysis ('q' to exit): ")
      if (y == 'q'):
        break    
      num_samples = int(y)
      adc_analysis(resolution)

  if (x == '6'):
      y = int(input("Set ADC/DAC resolution (1-8)"))
      if y in range(1,8):
        resolution = y
        print("Resolution set to %", y)
  
  if (x == '7'):
      dac_voltage_list = [float(item) for item in input("Enter measured DAC output voltages (LSB to MSB):").split()]
      print(dac_voltage_list)
      dac_analysis(dac_voltage_list)

  if (x =='q'):  
    break

GPIO.cleanup()


