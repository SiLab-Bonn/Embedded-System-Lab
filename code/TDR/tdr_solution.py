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

end_application = False

COMP = 5
GPIO.setup(COMP, GPIO.IN)
TRIGGER = 4
GPIO.setup(TRIGGER, GPIO.OUT)
GPIO.output(TRIGGER, GPIO.LOW)

dac_resolution =  10 # threshold DAC resolution
max_threshold = 1023 # maximum threshold value DAC counts 
pulse_delay   =    0 # offset to shift edge of the pulse
sample_delay  =    0 # parameter to scan the sampling time
max_delay     = 1023 # maximum sampling time delay 
delay_step    =    5 # delay step in ps
Z0            =   50 # characteristic impedance of the system

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
  dac_cmd  = 0x3000 # DAC enable, gain = 1: VDAC = [0..2047]mV
  spi_data = ((((0x3ff & threshold) << 2)| dac_cmd) << 24) + \
             ((0x3ff & reverse_bits(pulse_delay,  10)) << 10) + \
             ((0x3ff & reverse_bits(sample_delay, 10)) << 0)
  #print(bin(spi_data))
  spi.xfer(bytearray(spi_data.to_bytes(5, byteorder='big')))


dac_data         = np.zeros(max_delay)
voltage_data     = np.zeros(max_delay)
time_steps       = np.zeros(max_delay)
length_steps     = np.zeros(max_delay)
reflection_data  = np.zeros(max_delay)
impedance_data   = np.zeros(max_delay)

# voltage amplitude calibration data
amplitude_low  = 778   # DAC count for low amplitude w/o termination
amplitude_high = 215   # DAC count for high amplitude w/o termination
voltage_low    = 2711  # mV
voltage_high   = 3083  # mV
voltage_slope  = (voltage_high - voltage_low)/(amplitude_high - amplitude_low)
voltage_offset = voltage_low - voltage_slope * amplitude_low

# reflection coefficient  calibration data
amplitude_50ohm = 394 # DAC count for high amplitude with 50 ohm termination
amplitude_open  = 215 # DAC count for high amplitude w/o termination
rc_offset = amplitude_50ohm
rc_slope  = 1/(amplitude_open - amplitude_50ohm)


# time / distance calibration data
propagation_delay = 5.04 # ~5 ps/mm typical FR-4 and RG-174 coax cable
length_step = 0.5/propagation_delay # convert delay steps to distance
t0_offset   = 230 # offset in delay steps
x0_offset   = t0_offset * length_step # offset in mm  

def on_close(event):
  global end_application
  end_application = True

# plot the waveform data
plt.ion()
fig, waveform = plt.subplots(3,1)
# Connect the close event to the callback function
fig.canvas.mpl_connect('close_event', on_close)
plot1, = waveform[0].plot(time_steps, voltage_data)
waveform[0].set_xlabel("Time [ps]")
waveform[0].set_ylabel("Voltage [#DAC]")
waveform[0].set_xlim(0, max_delay * delay_step)
waveform[0].set_ylim(1500, 2500)
plot2, = waveform[1].plot(time_steps, reflection_data)
waveform[1].set_xlabel("Time [ps]")
waveform[1].set_ylabel("Refection Coefficient")
waveform[1].set_xlim(0, max_delay * delay_step)
waveform[1].set_ylim(-1.1, 1.1)
plot3, = waveform[2].plot(time_steps, impedance_data)
waveform[2].set_xlabel("Distance [mm]")
waveform[2].set_ylabel("Impedance [Ohm]")
waveform[2].set_xlim(- x0_offset, (max_delay * delay_step * length_step) - x0_offset)
waveform[2].set_ylim(0, 110)


while not end_application:
  dac_data = [0]
  time_steps = [0]
  for sample_delay in tqdm(range(max_delay)):
    time_steps = np.append(time_steps, [sample_delay * delay_step])
    # SAR loop
    threshold = 512 # start SAR ADC conversion with MSB set to '1'
    for dac_bit in reversed(range(dac_resolution)): # SAR conversion from MSB to LSB
      #set DAC value
      threshold |= 1 << (dac_bit)
      # update comparator threshold
      update_spi_regs(threshold, pulse_delay, sample_delay)
      # trigger pulse step
      GPIO.output(TRIGGER, GPIO.HIGH)
      #time.sleep(0.00001)
      # read comparator result
      result = GPIO.input(COMP)
      # reset pulse output
      GPIO.output(TRIGGER, GPIO.LOW)

      if result: # set next DAC bit, VTHR ~ 3.1V - VDAC/k
        threshold -= 1 << (dac_bit)
    # DAC is buffered with an inverting amplifier => higher DAC value -> lower threshold voltage  
    dac_data = np.append(dac_data, threshold)

  voltage_data    = (dac_data - voltage_offset) * voltage_slope
  reflection_data = (dac_data - rc_offset) * rc_slope
  impedance_data  = Z0 * (1 + reflection_data)/(1 - reflection_data)
  length_steps    = (time_steps - t0_offset) * length_step 
  plot1.set_data(time_steps, voltage_data)
  plot2.set_data(time_steps, reflection_data)
  plot3.set_data(length_steps, impedance_data)
  fig.canvas.draw()
  fig.canvas.flush_events()

# clean up
spi.close()
GPIO.cleanup()

