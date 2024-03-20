import time
from i2cdev import I2C
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

CH1 = 1
CH2 = 2

# There are three devices connected to the I2C bus:
#  - MCP47CVB22, dual channel 12-bit DAC
#  - MAX11644, dual channel 12-bit ADC
#  - PCA9554A, GPIO extender to controll the sense resitor multiplexer
#
# The following code initializes each device with its address on the I2C bus
# and sets the default configuration

# source voltage DAC
dac = I2C(0x60, 1)  # init DAC as I2C device on bus 1
dac.write(b'\x40\x00\x05') # external VREF, unbuffered
dac.write(b'\x50\x00\x00') # gain = 1

def set_voltage(channel, milli_volt):
  dac_value = int(milli_volt) # 12 bit DAC, VREF = 4096mV, VOUT = #DAC[mV]
  channel_reg = (channel-1) << 3
  i2c_data = bytes([channel_reg, (dac_value >> 8), (dac_value & 0xff)])
  dac.write(i2c_data)

# current sense ADC
adc = I2C(0x36, 1) # init ADC as I2C device on bus 1
adc.write(b'\xa2\x03') # configuration byte, setup byte (scan ch0-ch1)

def get_current_raw(channel, average = False):
  channel = channel-1
  if average:
    setup_data = bytes([0x21 | (channel << 1)])
  else:
    setup_data = bytes([0x61 | (channel << 1)])
  adc.write(setup_data)
  if average:
    i2c_data = adc.read(16)
    current = 0
    for i in range(8):
      current += 0x0fff & int.from_bytes(i2c_data[(2*i):(2*i+2)],"big")
    current = current / 8.0
  else:
    i2c_data = adc.read(2)
    current = 0x0fff & int.from_bytes(i2c_data,"big")
  return current

# multiplexer for selecting the current sense resistor
rsns = I2C(0x38, 1) # init GPIO extender as I2C device on bus 1
rsns.write(b'\x01\x00') # set bits 3:0 low
rsns.write(b'\x03\xf0') # configute bits 3:0 as outputs
# the mux settings [0,1,2,3] correspond to the following current sense resistors:
# 0: mux is off
# 1:  80 kOhm
# 2: 800 Ohm
# 3:   8 Ohm
#
# the effective transimpedance is the sense resistor value x 10 (voltage gain of the sense amplifier)
rsns_list  = [float("inf"), 800000, 8000, 80] 

def set_current_range(channel, value):
  channel = channel-1
  # read current output state
  rsns.write(b'\x01')
  reg = rsns.read(1)

  if (channel == 0):
    reg = (reg[0] & 0x0c) + value
  else:
    reg = (reg[0] & 0x03) + (value << 2)
  rsns.write(bytes([0x01, reg]))

# switch on
current_range = 1
set_voltage(CH1, 1)
set_current_range(CH1, current_range)

voltage_values = range(0, 2000, 20)
current_values = []

for voltage in voltage_values:
  set_voltage(CH1, voltage)
  current = get_current_raw(CH1)/rsns_list[current_range]
  current_values.append(current)
  print("H1 voltage [mV]:", voltage ," current [mA]:", current)
 # print("ADC counts:", current_raw)

fig, ax = plt.subplots()
ax.plot(voltage_values, current_values)

ax.set(xlabel='Voltage (mV)', ylabel='Current (mA)', title='I-V Curve')

plt.show()

# switch off
set_voltage(CH1, 0)
set_voltage(CH2, 0)
set_current_range(CH1, 0)
set_current_range(CH2, 0)

adc.close()
dac.close()
rsns.close()