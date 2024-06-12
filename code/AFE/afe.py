import time
import RPi.GPIO as GPIO
import spidev as SPI
import matplotlib.pyplot as plt
import numpy as np
import scipy
from scipy.optimize import curve_fit
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

time_constants_list = ['100 ns', '200 ns','500 ns', '1 us', '2 us', '5 us', '10 us', '20 us']
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

def inject(threshold, charge, time_constant, n_injections, monitor = 'sha'):
  update_spi_regs(threshold, charge, time_constant, monitor)
  hit_count = 0
  for i in range(n_injections): 
    GPIO.output(INJECT, GPIO.HIGH) # inject charge
    time.sleep(0.001) 
    if (GPIO.input(COMP)):         # read latched comparator output
      hit_count = hit_count + 1    
    GPIO.output(INJECT, GPIO.LOW)  # reset charge injection and hit latch 
    time.sleep(0.001)
  return (hit_count/n_injections)  # return measured hit probability

def threshold_scan(threshold, charge_range, time_constant, n_injections = 100, monitor = 'sha', show_plot = False):
  hit_data = np.empty(0, int)
  for charge in tqdm(charge_range):        # scan range of injected charges
    hit_probability = inject(threshold, charge, time_constant, n_injections, monitor)
    hit_data=np.append(hit_data, hit_probability)
  popt, pcov = curve_fit(err_func, charge_range, hit_data, bounds=([10,30], [100, 300])) # fir error function to data (still DAC units!)
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

def parametric_threshold_scan(threshold_range, charge_range, time_constant_range, n_injections = 100, monitor = 'sha'):
  hit_data = np.empty(0, int)
  fig, ax = plt.subplots()
  for time_constant in time_constant_range:    # scan range of shaper time constants or
    for threshold in threshold_range:          # scan range of threshold voltages
      popt, hit_data = threshold_scan(threshold, charge_range, time_constant, n_injections, monitor)
      label_text = 'tau=%s, sigma=%.1f, thr=%.1f [INJ_DAC], thr=%.1f [VTHR_DAC]' % (time_constants_list[time_constant], popt[0], popt[1], threshold)
      ax.plot(charge_range, hit_data, label=label_text)
      ax.plot(charge_range, err_func(charge_range, *popt))
  ax.set(xlabel='Injected charge (DAC)', ylabel='Hit probability', title='Threshold scan')
  ax.legend()
  ax.grid()
  plt.show()
  
charge_range = np.arange(50, 301, 10, dtype=int)
charge = 200
threshold_range = np.arange(2400, 2701, 100, dtype=int)
threshold = 2600 
time_constant_range = range(6,7)
time_constant = 6

#inject(threshold, charge, time_constant, n_injections = 1000, monitor = 'sha')
#threshold_scan(threshold, charge_range, time_constant, monitor='sha', show_plot = True)
parametric_threshold_scan(threshold_range, charge_range, time_constant_range, monitor='sha')

# while True:
#   inject(2300, 300, 6, 1)

#update_spi_regs(2000, 1000, 5, 'sha')
#input()


spi.close()
GPIO.cleanup()