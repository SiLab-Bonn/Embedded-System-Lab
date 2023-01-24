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

def SetVoltage(channel, volt, raw = False):
  if raw:
    dac_value = volt
  else:
    dac_value = int((volt / 16) * 1000) # 8 bit DAC!!! VOUT = #DAC/256 * 4096 mV
  channel = (channel-1) * 8
  i2c_data = bytes([channel, 0, dac_value])
  #print(i2c_data)
  DAC.write(i2c_data)

current_range = 0

def GetCurrent(channel, average=False):
  global current_range
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

  if current > 4000 and current_range == 0: # manually change to higher range
    input("Set high current range and press enter to continue.")
    current_range = 1
    if average:
      i2c_data = ADC.read(16)
      current = 0
      for i in range(8):
        current += 0x0fff & int.from_bytes(i2c_data[(2*i):(2*i+2)],"big")
      current = current / 8.0
    else:
      i2c_data = ADC.read(2)
      current = 0x0fff & int.from_bytes(i2c_data,"big")

  if current < 30 and current_range == 1: # manually change to lower range
    input("Set low current range and press enter continue.")
    current_range = 0
    if average:
      i2c_data = ADC.read(16)
      current = 0
      for i in range(8):
        current += 0x0fff & int.from_bytes(i2c_data[(2*i):(2*i+2)],"big")
      current = current / 8.0
    else:
      i2c_data = ADC.read(2)
      current = 0x0fff & int.from_bytes(i2c_data,"big")
  
  current -= 7 # subtract offset

  if current_range == 1:
    current *= 10

  else:
    current /= 10

  return current

fig1, ax = plt.subplots(3,2, sharex='col')
# fig2, bx = plt.subplots()

# voltage_sweep  = np.arange(0, 4.1, 0.05)
# voltage_parameter  = np.arange(1.1, 1.6, 0.1)
# current_data_array = np.empty([voltage_parameter.size, voltage_sweep.size])

# # Id vs Uds
# for ugs_index, ugs in enumerate(voltage_parameter):
#   SetVoltage(GATE, ugs)  # gate
#   for uds_index, uds in enumerate(voltage_sweep):
#     SetVoltage(DRAIN, uds) # drain
#     current_data_array[ugs_index][uds_index] = GetCurrent(DRAIN, average=True) 
#   bx.plot(voltage_sweep, current_data_array[ugs_index], label="{:.2f}".format(ugs))

# bx.set(xlabel='Uds [V]', ylabel='Id [uA]')
# bx.grid()
# bx.legend(title="Ugs")

voltage_sweep      = np.arange(0.0, 2.0, 16/1000)
voltage_parameter  = np.arange(0.8, 0.9, 0.2)
current_data_array = np.empty([voltage_parameter.size, voltage_sweep.size])

# Id vs Ugs
for uds_index, uds in enumerate(voltage_parameter):
  SetVoltage(DRAIN, uds)  # gate
  for ugs_index, ugs in enumerate(voltage_sweep):
    SetVoltage(GATE, ugs) # drain
    current_data_array[uds_index][ugs_index] = GetCurrent(DRAIN, average=True) 
  ax[0,0].plot(voltage_sweep, current_data_array[uds_index], label="{:.2f}".format(uds))
  ax[1,0].semilogy(voltage_sweep, current_data_array[uds_index], label="{:.2f}".format(uds))
  ax[2,0].plot(voltage_sweep, np.sqrt(current_data_array[uds_index]), label="{:.2f}".format(uds))

  # gm vs Id
  gm = np.diff(current_data_array[uds_index], prepend = 0)/np.diff(voltage_sweep, prepend = 0.5)

  ax[0,1].plot(voltage_sweep, gm/1000)
  ax[1,1].plot(voltage_sweep, gm/np.sqrt(current_data_array[uds_index]))
  ax[2,1].plot(voltage_sweep, gm/current_data_array[uds_index])  

ax[0,0].set(ylabel='Id [uA]')
ax[0,0].legend(title="Uds")
ax[0,0].grid()

ax[1,0].set(ylabel='Id [uA]')
ax[1,0].grid()

ax[2,0].set(xlabel='Ugs [V]', ylabel='SQRT(Id [uA])')
ax[2,0].grid()

ax[0,1].set(ylabel='gm [A/V]')
ax[0,1].grid()
ax[0,1].set_ylim(-5, )

ax[1,1].set(ylabel='gm/SQRT(Id) [1/SQRT(V)]')
ax[1,1].grid()
ax[1,1].set_ylim(-5, )

ax[2,1].set(xlabel='Ugs [V]', ylabel='gm/Id [1/V]')
ax[2,1].grid()
ax[2,1].set_ylim(-5, )

plt.show()

DAC.close() # close device
ADC.close()