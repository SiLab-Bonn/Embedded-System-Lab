import time
from i2cdev import I2C
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

#DAC channels
CH1 = 1
CH2 = 2

# source voltage DAC
DAC = I2C(0x60, 1)  # init DAC as I2C device on bus 1
DAC.write(b'\x40\x00\x05') # external VREF, unbuffered
DAC.write(b'\x50\x00\x00') # gain = 1

# sense ADC
ADC = I2C(0x36, 1) # init ADC as I2C device on bus 1
ADC.write(b'\xa2\x03') # configuration byte, setup byte (scan ch0-ch1)

def SetVoltage(channel, volt):
  dac_value = int((volt / 16) * 1000) # 8 bit DAC!!! VOUT = #DAC/256 * 4096 mV
  channel = (channel-1) * 8
  i2c_data = bytes([channel, 0, dac_value])
  #print(i2c_data)
  DAC.write(i2c_data)

def GetCurrent(channel, average=False):
  channel = channel -1 # 1,2 -> 0,1
  if average:
    setup_data = bytes([0x21 | (channel << 1)])
  else:
    setup_data = bytes([0x61 | (channel << 1)])
  ADC.write(setup_data)

  if average:
    i2c_data = ADC.read(16)
    current = 0
    for i in range(8):
      current += 0x0fff & int.from_bytes(i2c_data[(2*i):(2*i+2)],"big")
    current = current / 8.0
  else:
    i2c_data = ADC.read(2)
    current = 0x0fff & int.from_bytes(i2c_data,"big")

  return current

fig, ax = plt.subplots(1,1)

voltage_sweep  = np.arange(0, 4.1, 0.05)
current_data_array = np.empty([2, voltage_sweep.size])

for voltage_step, voltage in enumerate(voltage_sweep):
  SetVoltage(CH1, voltage) 
  SetVoltage(CH2, voltage) 
  current_data_array[0][voltage_step] = GetCurrent(CH1, average=True) 
  current_data_array[1][voltage_step] = GetCurrent(CH2, average=True) 
ax.plot(voltage_sweep, current_data_array[0])
ax.plot(voltage_sweep, current_data_array[1])

ax.set(xlabel='U (V)', ylabel='I (uA)')
ax.grid()

plt.show()

DAC.close() # close device
ADC.close()