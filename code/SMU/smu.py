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

def GetCurrent():
  i2c_data = ADC.read(4)
  curr_ch0 = 0x0fff & int.from_bytes(i2c_data[0:2],"big")
  curr_ch1 = 0x0fff & int.from_bytes(i2c_data[2:4],"big")
  #print(curr_ch0, curr_ch1)  
  return (curr_ch0, curr_ch1)

for voltage in np.arange(0, 4.1, 0.1):
  SetVoltage(0, voltage)
  current0, current1 = GetCurrent()
  print(voltage, current0)



DAC.close() # close device
ADC.close()