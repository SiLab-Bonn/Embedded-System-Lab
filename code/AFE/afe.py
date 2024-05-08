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
INJECT = 4
GPIO.setup(INJECT, GPIO.OUT)
GPIO.output(INJECT, GPIO.LOW)

time_constants_list = ['100ns', '200ns','500ns', '1us', '2us', '5us', '10us', '20us']
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
  spi_data = ((((0xfff & threshold) | dac_cmd_a) << 8) + \
                ( 0x07 & time_constant) | ((0x03 & out_mux_val) << 3))
  #print(bin(spi_data)[2:].zfill(24))
  spi.xfer(bytearray(spi_data.to_bytes(3, byteorder='big')))

  #set DAC channel B (injection signal)
  spi_data = ((((0xfff & injected_signal) | dac_cmd_b) << 8) + \
                ( 0x07 & time_constant) | ((0x03 & out_mux_val) << 3))
  #print(bin(spi_data)[2:].zfill(24))
  spi.xfer(bytearray(spi_data.to_bytes(3, byteorder='big')))

charge    = 300
threshold = 2800
out_mux = 0

GPIO.output(INJECT, GPIO.LOW)


def threshold_scan(threshold, charge_range, time_constant_range, n_injections = 100, plot = 'sha'):
  fig, ax = plt.subplots()
  hit_data = []
  charge_data = []
  for time_constant in time_constant_range:
    print("time constant index =", time_constant )
    for charge in tqdm(charge_range):
      charge_data.append(charge)
      update_spi_regs(threshold, charge, time_constant, plot)
      hit_count = 0
      for i in range (n_injections): 
        GPIO.output(INJECT, GPIO.HIGH)
        time.sleep(0.0001) 
        if (GPIO.input(COMP)):
          hit_count = hit_count + 1
        GPIO.output(INJECT, GPIO.LOW)
        time.sleep(0.0002)
      hit_data.append(hit_count)
    ax.plot(charge_data, hit_data, label=time_constants_list[time_constant])
    charge_data = []
    hit_data = []
 
  ax.set(xlabel='charge (DAC)', ylabel='hit count', title='Threshold scan')
  ax.legend(title="shaper time constant")
  ax.grid()
  #fig.savefig("test.png")
  plt.show()


def inject(threshold, charge, time_constant, n_injections):
  update_spi_regs(threshold, charge, time_constant, 'sha')
  for i in range(n_injections): 
    GPIO.output(INJECT, GPIO.HIGH)
    time.sleep(0.0002) 
    GPIO.output(INJECT, GPIO.LOW)
    time.sleep(0.0002)
  
charge_range = range(30, 100, 1)
threshold = 2200
time_constant_range = range(6,7)

threshold_scan(threshold, charge_range, time_constant_range, plot='sha')

# while True:
#   inject(3000, 200, 7, 1)

#update_spi_regs(2000, 1000, 5, 'sha')
#input()


spi.close()
GPIO.cleanup()