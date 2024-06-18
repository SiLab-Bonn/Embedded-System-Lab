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

# some constants and AFE circuit parameters
tot_period  = 25e-3  # [µs], 40 MHz TOT counter clock
q_e   = 1.602e-19 # elementary charge
C_f   = 1.39e-12  # 1 pF mounted + 0.39 pF parasitic capacitance (from Rf mainly)
C_inj = 0.1e-12   # 0.1 pF injection capacitance   
A_sha = 1000/np.exp(1) # shaping amplifier gain

time_constants_list = [0.1, 0.2, 0.5, 1, 2, 5, 10, 20] # [µs]
out_mux_dict = {
  'csa':  0, 
  'hpf':  1, 
  'sha':  2, 
  'comp': 3}

# main function for communication with the AFE module via the SPI bus
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
  return spi.xfer(bytearray(spi_data.to_bytes(3, byteorder='big')))

# calculate sensitivity and calibration constants (DAC LSB sizes in electrons)
def calculate_calibration_constants():

  sensitivity_fC = 1/C_f * A_sha * 1e-12     # total AFE chain sensitivity [mV/fC]
  sensitivity_e  = 1/C_f * A_sha * q_e * 1e3 # total AFE chain sensitivity [mV/e]
  injection_fc   = 0.1 * C_inj * 1e12        # charge injection conversion factor [fC/mV]
  injection_e    = 0.1 * C_inj * 1e-3 / q_e  # charge injection conversion factor [e/mV]

  vthr_dac_lsb_electrons = 0.5 / sensitivity_e # 0.5 mV (DAC LSB) / AFE sensitivity [e/DAC_LSB]
  vinj_dac_lsb_electrons = 0.5 * injection_e   # 0.5 mV (DAC LSB) * injection conversion factor [e/DAC_LSB]

  print('AFE sensitivity: %.1f [mV/fC]' % sensitivity_fC)
  print('AFE sensitivity: %.3f [mV/e]' % sensitivity_e)
  print('VTHR DAC LSB: %.2f [e]' % vthr_dac_lsb_electrons)
  print('VINJ DAC LSB: %.2f [e]' % vinj_dac_lsb_electrons)
  print('VINJ DAC LSB/VTHR DAC LSB: %.2f' % (vinj_dac_lsb_electrons/vthr_dac_lsb_electrons))

  return vthr_dac_lsb_electrons, vinj_dac_lsb_electrons

# normalized error function for threshold scan fit
def err_func(x,a,b):
   return 0.5*(scipy.special.erf((x-b)/(np.sqrt(2)*a))+1)  # normalized error function

# shaper pulse waveform function (equal low and high pass filter time constants)
def sha_pulse_func(t, t0, tau, a, b):
  return np.where(t > t0, a * np.exp(1) * (t-t0)/tau * np.exp(-(t-t0)/tau) + b, b)

# shaper pulse waveform function (individual low and high pass filter time constants) 
def sha_pulse2_func(t, t0, tau1, tau2, a, b):
  return np.where(t > t0, a * np.exp(1) * 1/(tau1-tau2) * (np.exp(-(t-t0)/tau2) - (tau2/tau1) * np.exp(-(t-t0)/tau1)) + b, b)

# simple injection loop, returns the detected hit probability
def inject(threshold, charge, time_constant, n_injections = 100, monitor = 'sha'):
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

# single injection, returns TOT value
def inject_read_tot(threshold, charge, time_constant, monitor = 'sha'):
  tot = 0 # in case no hit was detected
  update_spi_regs(threshold, charge, time_constant, monitor)
  GPIO.output(INJECT, GPIO.HIGH) # inject charge
  time.sleep(0.0001) 
  if (GPIO.input(COMP)):   # read latched comparator output, read TOT value if hit detected
    time.sleep(0.001)     # wait for counter to stop
    tot = update_spi_regs(threshold, charge, time_constant, monitor)[0]  # read TOT value from CPLD   
  GPIO.output(INJECT, GPIO.LOW)  # reset charge injection, hit latch, and TOT counter
  time.sleep(0.0001)
  return tot  # return measured TOT

# scan the injection charge range and return the resulting s-curve fit parameters
def threshold_scan(threshold, charge_range, time_constant, n_injections = 100, monitor = 'sha', show_plot = False, use_calibration = False):
  hit_data = np.empty(0, int)
  for charge in tqdm(charge_range):        # scan range of injected charges
    hit_probability = inject(threshold, charge, time_constant, n_injections, monitor)
    hit_data=np.append(hit_data, hit_probability)
    a_min = 1
    a_max = 100
    b_min = 30
    b_max = 500
  if (use_calibration == True):
    charge_range = charge_range * vinj_dac_lsb_electrons
    a_min = a_min * vinj_dac_lsb_electrons
    a_max = a_max * vinj_dac_lsb_electrons
    b_min = b_min * vinj_dac_lsb_electrons
    b_max = b_max * vinj_dac_lsb_electrons
  popt, pcov = curve_fit(err_func, charge_range, hit_data, bounds=([a_min,b_min], [a_max, b_max])) # fit error function to data (DAC units)
  if (show_plot == True):
    fig, ax = plt.subplots()
    if (use_calibration == True):
      label_text = 'tau=%s µs, sigma=%.0f [e], thr(inj)=%.1f [e], thr(set)=%.1f [e]' % (time_constants_list[time_constant], popt[0], popt[1], (threshold-baseline)*vthr_dac_lsb_electrons)
    else:
      label_text = 'tau=%s µs, sigma=%.1f, thr=%.1f [INJ_DAC], thr=%.1f [VTHR_DAC]' % (time_constants_list[time_constant], popt[0], popt[1], threshold)
    ax.plot(charge_range, hit_data, label=label_text)
    ax.plot(charge_range, err_func(charge_range, *popt))
    if (use_calibration == True):
      ax.set(xlabel='Injected charge (e)', ylabel='Hit probability', title='Threshold scan')
    else:
      ax.set(xlabel='Injected charge (DAC)', ylabel='Hit probability', title='Threshold scan')
    ax.legend()
    ax.grid()
    #plt.show()
  return popt, hit_data

# multiple s-curve measurements with varying threshold voltage, extract the fitted threshold values
def parametric_threshold_scan_1(threshold_range, charge_range, time_constant, n_injections = 100, monitor = 'sha', use_calibration = False):
  hit_data = np.empty(0, int)  
  fitted_threshold_data = np.empty(0, int)
  fig, ax = plt.subplots(2,1)
  for threshold in threshold_range:          # scan range of threshold voltages
    print('Scanning threshold: ', threshold if use_calibration else  threshold * vthr_dac_lsb_electrons)
    popt, hit_data = threshold_scan(threshold, charge_range, time_constant, n_injections, monitor, use_calibration = use_calibration)
    fitted_threshold_data = np.append(fitted_threshold_data, popt[1])
    if (use_calibration == True):
      label_text = 'tau=%s [µs], sigma=%.0f [e], thr(inj)=%.0f [e], thr(set)=%.0f [e]' % (time_constants_list[time_constant], popt[0], popt[1], (threshold-baseline)*vthr_dac_lsb_electrons)
      ax[0].plot(charge_range * vinj_dac_lsb_electrons, hit_data, label=label_text)    # plot hit probability vs. injected charge
      ax[0].plot(charge_range * vinj_dac_lsb_electrons, err_func(charge_range * vinj_dac_lsb_electrons, *popt)) # plot fitted error-function
    else:
      label_text = 'tau=%s [ms], sigma=%.1f [DAC], thr=%.1f [INJ_DAC], thr=%.0f [VTHR_DAC]' % (time_constants_list[time_constant], popt[0], popt[1], threshold)
      ax[0].plot(charge_range, hit_data, label=label_text)    # plot hit probability vs. injected charge
      ax[0].plot(charge_range, err_func(charge_range, *popt)) # plot fitted error-function
  if (use_calibration == True): 
    ax[0].set(xlabel='Injected charge [e]', ylabel='Hit probability', title='Threshold scan')
  else:
    ax[0].set(xlabel='Injected charge [DAC]', ylabel='Hit probability', title='Threshold scan')
  ax[0].legend()
  ax[0].grid()
  #print(fitted_threshold_data)
  if (use_calibration == True):
    threshold_range = (threshold_range - baseline) * vthr_dac_lsb_electrons
  slope, offset = np.polyfit(fitted_threshold_data, threshold_range, 1)
  label_text = 'slope=%.2f, offset=%.1f' % (slope, offset)
  if (use_calibration == True):
    ax[1].plot(fitted_threshold_data, threshold_range, label=label_text) # plot measured vs set. threshold
    ax[1].set(xlabel='Measured threshold [e]', ylabel='Set threshold [e]')
  else:
    ax[1].plot(fitted_threshold_data, threshold_range, label=label_text) # plot measured vs set. threshold
    ax[1].set(xlabel='Measured threshold [INJ_DAC]', ylabel='Set threshold [VTHR_DAC]')
  ax[1].legend()
  ax[1].grid()

# multiple s-curve measurements with varying time constant, extract the fitted noise values
def parametric_threshold_scan_2(threshold, charge_range, time_constant_range, n_injections = 100, monitor = 'sha', use_calibration = False):
  hit_data = np.empty(0, int)  
  fitted_noise_data = np.empty(0, int)  
  shaping_time_data = np.empty(0, float)
  fig, ax = plt.subplots(2,1)
  for time_constant_index in time_constant_range:    # scan range of shaper time constants **or**
    print('Scanning time constant: ', time_constants_list[time_constant_index])
    popt, hit_data = threshold_scan(threshold, charge_range, time_constant_index, n_injections, monitor, use_calibration = use_calibration)
    fitted_noise_data = np.append(fitted_noise_data, popt[0])
    shaping_time_data = np.append(shaping_time_data, time_constants_list[time_constant_index])
    if (use_calibration == True):
      label_text = 'tau=%s µs, sigma=%.0f [e]' % (time_constants_list[time_constant_index], popt[0])
      ax[0].plot(charge_range * vinj_dac_lsb_electrons, hit_data, label=label_text)    # plot hit probability vs. injected charge
      ax[0].plot(charge_range * vinj_dac_lsb_electrons, err_func(charge_range * vinj_dac_lsb_electrons, *popt))
    else: 
      label_text = 'tau=%s µs, sigma=%.1f [INJ_DAC]' % (time_constants_list[time_constant_index], popt[0])
      ax[0].plot(charge_range, hit_data, label=label_text)    # plot hit probability vs. injected charge
      ax[0].plot(charge_range, err_func(charge_range, *popt)) # plot fittd error-function
  if (use_calibration == True):    
    ax[0].set(xlabel='Injected charge [e]', ylabel='Hit probability', title='Threshold scan')
    ax[1].set(xlabel='Shaping time [us]', ylabel='Noise [e]', title='Noise vs. shaping time')
  else:
    ax[0].set(xlabel='Injected charge [INJ_DAC]', ylabel='Hit probability', title='Threshold scan')
    ax[1].set(xlabel='Shaping time [us]', ylabel='Noise [INJ_DAC]', title='Noise vs. shaping time')
     
  ax[0].legend()
  ax[0].grid()
  ax[1].plot(shaping_time_data, fitted_noise_data, label='some detector capacitance...') # plot noise vs shaping time constant
  ax[1].legend()
  ax[1].grid()

# scan injected charge range and return the resulting TOT values 
def tot_scan(threshold, charge_range, time_constant, n_injections = 100, monitor = 'comp', show_plot = False, use_calibration = False):
  tot_data = np.empty(0, int)
  for charge in tqdm(charge_range):
    tot = 0
    for i in range(n_injections):
      tot = tot + inject_read_tot(threshold, charge, time_constant, monitor)
    tot = tot/n_injections
    tot_data = np.append(tot_data, tot)
  if (show_plot == True):
    fig, ax = plt.subplots()
    if (use_calibration == True):
      label_text = 'tau=%s µs, thr(set)=%.1f [e]' % (time_constants_list[time_constant],(threshold-baseline)*vthr_dac_lsb_electrons)
      ax.set(xlabel='Injected charge (e)', ylabel='TOT [µs]', title='TOT scan')
      charge_range = charge_range * vinj_dac_lsb_electrons
      tot_data = tot_data * tot_period
    else:
      label_text = 'tau=%s µs, thr=%.0f [VTHR_DAC]' % (time_constants_list[time_constant], threshold)
      ax.set(xlabel='Injected charge (DAC)', ylabel='TOT [25 ns]', title='TOT scan')
    ax.plot(charge_range, tot_data, label=label_text)
    ax.legend()
    ax.grid()
  #plt.show()
  return tot_data

# scan the injected charge range and return the resulting TOT values with the time constant as parameter
def parametric_tot_scan(threshold, charge_range, time_constant_range, n_injections = 100, monitor = 'comp', use_calibration = False):
  fig, ax = plt.subplots()
  for time_constant_index in time_constant_range:    # scan range of shaper time constants
    print('Scanning time constant: ', time_constants_list[time_constant_index])
    tot_data = np.empty(0, int)
    tot_data = tot_scan(threshold, charge_range, time_constant_index, n_injections, monitor, use_calibration = use_calibration)
    label_text = 'tau=%s µs, threshold=%.1f' % (time_constants_list[time_constant_index], (threshold-baseline)*vthr_dac_lsb_electrons if use_calibration else threshold)
    if (use_calibration == True):
      ax.plot(charge_range * vinj_dac_lsb_electrons, tot_data * tot_period, label=label_text)    # plot hit probability vs. injected charge
    else: 
      ax.plot(charge_range, tot_data * tot_period, label=label_text)    # plot hit probability vs. injected charge
  if (use_calibration == True):    
    ax.set(xlabel='Injected charge [e]', ylabel='TOT [µs]', title='TOT scan')
  else:
    ax.set(xlabel='Injected charge [INJ_DAC]', ylabel='TOT [25 ns]', title='TOT scan')
  ax.legend()
  ax.grid()

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

# scan range definitions
baseline = 2000  # shaper output DC potential (typical value), adjust for actual baseline of the individual AFE module if needed
threshold_range_min = baseline + 300
threshold_range_max = baseline + 700
charge_range = np.arange(20, 301, 10, dtype=int)
charge = 200
threshold_range = np.arange(threshold_range_min, threshold_range_max, 100, dtype=int)
threshold = baseline + 450 
time_constant_range = range(2,5)
time_constant = 3


# function calls, uncomment to run specific or all tests
vthr_dac_lsb_electrons, vinj_dac_lsb_electrons = calculate_calibration_constants()
#inject(threshold, charge, time_constant, n_injections = 1000, monitor = 'sha')
#threshold_scan(threshold, charge_range, time_constant, monitor='sha', show_plot=True, use_calibration=True)
#tot_scan(threshold, charge_range, time_constant, monitor = 'comp', show_plot = True, use_calibration=True)
parametric_threshold_scan_1(threshold_range, charge_range, time_constant, monitor='sha', use_calibration=True)
parametric_threshold_scan_2(threshold, charge_range, time_constant_range, monitor='sha', use_calibration=True)
parametric_tot_scan(threshold, charge_range, time_constant_range, monitor = 'comp',  use_calibration=True)
#analyze_waveform('code/AFE/test.csv')

# clean up
spi.close()
GPIO.cleanup()
# finally show all plots
plt.show()