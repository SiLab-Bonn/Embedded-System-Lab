import time
from i2cdev import I2C
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

#DAC channel connected to internal MOSFET
DRAIN = 2
GATE  = 1

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
    current = current >> 3
  else:
    i2c_data = ADC.read(2)
    current = 0x0fff & int.from_bytes(i2c_data,"big")

  return current

fig, ax = plt.subplots(3,1)

voltage_sweep  = np.arange(0, 4.1, 0.05)
voltage_parameter  = np.arange(1.1, 1.6, 0.1)
current_data_array = np.empty([voltage_parameter.size, voltage_sweep.size])

# Id vs Uds
for ugs_index, ugs in enumerate(voltage_parameter):
  SetVoltage(GATE, ugs)  # gate
  for uds_index, uds in enumerate(voltage_sweep):
    SetVoltage(DRAIN, uds) # drain
    current_data_array[ugs_index][uds_index] = GetCurrent(DRAIN, average=True) 
  ax[0].plot(voltage_sweep, current_data_array[ugs_index], label="{:.2f}".format(ugs))


voltage_sweep  = np.arange(1, 2, 0.05)
voltage_parameter  = np.arange(0.1, .5, 0.1)
current_data_array = np.empty([voltage_parameter.size, voltage_sweep.size])

# Id vs Uds
for uds_index, uds in enumerate(voltage_parameter):
  SetVoltage(DRAIN, uds)  # gate
  for ugs_index, ugs in enumerate(voltage_sweep):
    SetVoltage(GATE, ugs) # drain
    current_data_array[uds_index][ugs_index] = GetCurrent(DRAIN, average=True) 
  ax[1].plot(voltage_sweep, current_data_array[uds_index], label="{:.2f}".format(uds))

# gm vs Id
gm = np.diff(current_data_array[2], prepend = 0)/np.diff(voltage_sweep, prepend = 0.01)

ax[2].plot(voltage_sweep, gm)
#ax[2].plot(current_data_array[2], gm)


ax[0].set(xlabel='Uds (V)', ylabel='Id (uA)')
ax[0].grid()
ax[0].legend(title="Ugs")
ax[1].set(xlabel='Ugs (V)', ylabel='Id (uA)')
ax[1].grid()
ax[1].legend(title  = "Uds")
ax[2].set(xlabel='Ugs (V)', ylabel='gm(uA/V)')
ax[2].grid()

plt.show()

DAC.close() # close device
ADC.close()