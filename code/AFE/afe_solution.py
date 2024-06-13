import time
import RPi.GPIO as GPIO
import spidev as SPI
import matplotlib.pyplot as plt
import numpy as np
import scipy
from scipy.optimize import curve_fit
import csv
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

def err_func(x,a,b):
   return 0.5*scipy.special.erf((x-b)/a)+0.5

charge    = 300
threshold = 2800
out_mux = 0

GPIO.output(INJECT, GPIO.LOW)

# simple injection loop, returns the detected hit probability
def inject(threshold, charge, time_constant, n_injections, monitor = 'sha'):
  update_spi_regs(threshold, charge, time_constant, monitor)
  hit_count = 0
  for i in range(n_injections): 
    GPIO.output(INJECT, GPIO.HIGH) # inject charge
    time.sleep(0.0001) 
    if (GPIO.input(COMP)):         # read latched comparator output
      hit_count = hit_count + 1    
    GPIO.output(INJECT, GPIO.LOW)  # reset charge injection and hit latch 
    time.sleep(0.0001)
  return (hit_count/n_injections)  # return measured hit probability

# scan the injection charge range and return the resulting s-curve fit parameters
def threshold_scan(threshold, charge_range, time_constant, n_injections = 100, monitor = 'sha', show_plot = False):
  hit_data = np.empty(0, int)
  for charge in tqdm(charge_range):        # scan range of injected charges
    hit_probability = inject(threshold, charge, time_constant, n_injections, monitor)
    hit_data=np.append(hit_data, hit_probability)
  popt, pcov = curve_fit(err_func, charge_range, hit_data, bounds=([10,30], [100, 500])) # fir error function to data (still DAC units!)
  print(popt)
  if (show_plot == True):
    fig, ax = plt.subplots()
    label_text = 'tau=%s, sigma=%.1f, thr=%.1f [INJ_DAC], thr=%.1f [VTHR_DAC]' % (time_constants_list[time_constant], popt[0], popt[1], threshold)
    ax.plot(charge_range, hit_data, label=label_text)
    ax.plot(charge_range, err_func(charge_range, *popt))
    ax.set(xlabel='Injected charge (DAC)', ylabel='Hit probability', title='Threshold scan')
    ax.legend()
    ax.grid()
    plt.show()
  return popt, hit_data

# multiple s-curve measurements with varying threshold voltage, extract the fitted threshold values
def parametric_threshold_scan_1(threshold_range, charge_range, time_constant, n_injections = 100, monitor = 'sha'):
  hit_data = np.empty(0, int)  
  fitted_threshold_data = np.empty(0, int)
  fig, ax = plt.subplots(2,1)
  for threshold in threshold_range:          # scan range of threshold voltages
    popt, hit_data = threshold_scan(threshold, charge_range, time_constant, n_injections, monitor)
    fitted_threshold_data = np.append(fitted_threshold_data, popt[1])
    label_text = 'tau=%s, sigma=%.1f, thr=%.1f [INJ_DAC], thr=%.1f [VTHR_DAC]' % (time_constants_list[time_constant], popt[0], popt[1], threshold)
    ax[0].plot(charge_range, hit_data, label=label_text)    # plot hit probability vs. injected charge
    ax[0].plot(charge_range, err_func(charge_range, *popt)) # plot fitted error-function
  ax[0].set(xlabel='Injected charge (DAC)', ylabel='Hit probability', title='Threshold scan')
  ax[0].legend()
  ax[0].grid()
  print(fitted_threshold_data)
  slope, offset = np.polyfit(fitted_threshold_data, threshold_range, 1)
  label_text = 'slope=%.2f, offset=%.1f' % (slope, offset)
  ax[1].plot(fitted_threshold_data, threshold_range, label=label_text) # plot measured vs set. threshold
  ax[1].set(xlabel='Measured threshold [INJ_DAC]', ylabel='Set threshold [VTHR_DAC]')
  ax[1].legend()
  ax[1].grid()
  plt.show()

# multiple s-curve measurements with varying time constant, extract the fitted noise values
def parametric_threshold_scan_2(threshold, charge_range, time_constant_range, n_injections = 100, monitor = 'sha'):
  hit_data = np.empty(0, int)  
  fitted_noise_data = np.empty(0, int)  
  shaping_time_data = np.empty(0, float)
  fig, ax = plt.subplots(2,1)
  for time_constant_index in time_constant_range:    # scan range of shaper time constants **or**
    popt, hit_data = threshold_scan(threshold, charge_range, time_constant_index, n_injections, monitor)
    fitted_noise_data = np.append(fitted_noise_data, popt[0])
    shaping_time_data = np.append(shaping_time_data, time_constants_list[time_constant_index])
    label_text = 'tau=%s µs, sigma=%.1f, thr=%.1f [INJ_DAC], thr=%.1f [VTHR_DAC]' % (time_constants_list[time_constant_index], popt[0], popt[1], threshold)
    ax[0].plot(charge_range, hit_data, label=label_text)    # plot hit probability vs. injected charge
    ax[0].plot(charge_range, err_func(charge_range, *popt)) # plot fittd error-function
  ax[0].set(xlabel='Injected charge [INJ_DAC]', ylabel='Hit probability', title='Threshold scan')
  ax[0].legend()
  ax[0].grid()
  print(fitted_noise_data)
  #label_text = 'tau=%s, sigma=%.1f, thr=%.1f [INJ_DAC], thr=%.1f [VTHR_DAC]' % (time_constants_list[time_constant], popt[0], popt[1], threshold)
  ax[1].plot(shaping_time_data, fitted_noise_data, label='some detector capacitance...') # plot noise vs shaping time constant
  ax[1].set(xlabel='Shaping time [us]', ylabel='Noise [INJ_DAC]', title='Noise vs. shaping time')
  ax[1].legend()
  ax[1].grid()
  plt.show()
  
def sha_pulse_func(t, t0, tau, a, b):
  return np.where(t > t0, a * np.exp(1) * (t-t0)/tau * np.exp(-(t-t0)/tau) + b, b)


def analyze_waveform(filename):
  with open(filename, 'r') as file:
    reader = csv.reader(file)
    data = list(reader)
    data = np.array(data[:1000]).astype(float)
    
    popt, pcov = curve_fit(sha_pulse_func, data[:,0], data[:,1], bounds=([50, 1, 200, 900], [80, 25, 1500, 1100])) 
    label_text = 't0=%.1f, tau=%.1f, a=%.1f, b=%.1f' % (popt[0], popt[1], popt[2], popt[3])

    fig, ax = plt.subplots()
    ax.plot(data[:,0], data[:,1])
    ax.plot(data[:,0], sha_pulse_func(data[:,0], *popt), label=label_text)
    ax.set(xlabel='Time [us]', ylabel='Voltage [mV]', title='SHA pulse')
    ax.legend()
    plt.show()

baseline = 2430  # adjust for actual baseline of the individual AFE module (DAC units)
threshold_range_min = baseline + 200
threshold_range_max = baseline + 600
charge_range = np.arange(50, 401, 10, dtype=int)
charge = 200
threshold_range = np.arange(threshold_range_min, threshold_range_max, 100, dtype=int)
threshold = baseline + 400 
time_constant_range = range(2,8)
time_constant = 6

#inject(threshold, charge, time_constant, n_injections = 1000, monitor = 'sha')
#threshold_scan(threshold, charge_range, time_constant, monitor='sha', show_plot = True)
#parametric_threshold_scan_1(threshold_range, charge_range, time_constant, monitor='sha')
parametric_threshold_scan_2(threshold, charge_range, time_constant_range, monitor='sha')
#analyze_waveform('code/AFE/test.csv')

spi.close()
GPIO.cleanup()