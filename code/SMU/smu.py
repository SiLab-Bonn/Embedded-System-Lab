import time
from i2cdev import I2C
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

# source voltage DAC
DAC = I2C(0x60, 1)  # init DAC as I2C device on bus 1
DAC.write(b'\x40\x00\x05') # external VREF, unbuffered
DAC.write(b'\x50\x00\x00') # gain = 1

# sense ADC
ADC = I2C(0x36, 1) # init ADC as I2C device on bus 1
ADC.write(b'\xa2\x03') # configuration byte, setup byte (scan ch0-ch1)

def SetVoltage(channel, volt):
  dac_value = int((volt / 16) * 1000) # 8 bit DAC!!! VOUT = #DAC/256 * 4096 mV
  channel = channel * 8
  i2c_data = bytes([channel, 0, dac_value])
  #print(i2c_data)
  DAC.write(i2c_data)

def GetCurrent(channel, average=False):
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
    current = current >> 3
  else:
    i2c_data = ADC.read(2)
    current = 0x0fff & int.from_bytes(i2c_data,"big")

  return current

voltage_data = np.arange(0, 4.1, 0.05)
current0_data = np.array([])
current1_data = np.array([])

SetVoltage(1, 1)  # drain

for voltage in voltage_data:
  SetVoltage(0, voltage) # gate
  current0 = GetCurrent(0, average=True) 
  current0_data = np.append(current0_data, current0)  
 
SetVoltage(1, 1.1)  # drain

for voltage in voltage_data:
  SetVoltage(0, voltage) # gate
  current1 = GetCurrent(0, average=True)
  current1_data = np.append(current1_data, current1)

fig, ax = plt.subplots()
ax.plot(voltage_data, current0_data)
ax.plot(voltage_data, current1_data)

ax.set(xlabel='Voltage (V)', ylabel='Current (uA)', title='I-V Curve')
ax.grid()
plt.show()

DAC.close() # close device
ADC.close()