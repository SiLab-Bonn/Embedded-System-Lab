import time
from i2cdev import I2C
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

# DAC channels
CH1 = 1
CH2 = 2

# current sense range
curr_range_dict = {
  "off":  0,  # MUX off
  "low":  1,  # 80 kOhm
  "mid":  2,  # 800 Ohm
  "high": 3,  # 8 Ohm
  "auto": -1  # auto range
}

# current sense gain setting resistor
rsns_list  = [float("inf"), 800000, 8000, 80]  # effective transimpedance = Rsns x 10
adc_offset  = 6
adc_cm_gain = 0.0045
upper_limit = 4050  # upper limit for current measurement (ADC counts)
lower_limit = 50    # lower limit for current measurement (ADC counts)

class SMU:
  def __init__(self):
    # source voltage DAC
    self.dac = I2C(0x60, 1)  # init DAC as I2C device on bus 1
    self.dac.write(b'\x40\x00\x05') # external VREF, unbuffered
    self.dac.write(b'\x50\x00\x00') # gain = 1

    # current sense ADC
    self.adc = I2C(0x36, 1) # init ADC as I2C device on bus 1
    self.adc.write(b'\xa2\x03') # configuration byte, setup byte (scan ch0-ch1)

    # current sense resistor
    self.rsns = I2C(0x38, 1) # init GPIO extender as I2C device on bus 1
    self.rsns.write(b'\x03\xf0') # configute bits 3:0 as outputs
    self.rsns.write(b'\x01\x00') # set bits 3:0 low

    self.ch = [SMU_channel(self, 1), SMU_channel(self, 2)]

  def close(self):
    self.ch[0].close()
    self.ch[1].close()
    self.dac.close()
    self.adc.close()
    self.rsns.close()
    
    
class SMU_channel:
  def __init__(self, smu, channel):
    self.channel = channel-1
    self.smu = smu
    self.set_current_range(0)    
    self.set_voltage(0)    

  def set_voltage(self, volt):
    self.dac_value = int(volt * 1000) # 12 bit DAC, VREF = 4096mV, VOUT = #DAC[mV]
    channel_reg = self.channel << 3
    i2c_data = bytes([channel_reg, (self.dac_value >> 8), (self.dac_value & 0xff)])
    self.smu.dac.write(i2c_data)

  def set_current_range(self, value):
    # read current output state
    self.smu.rsns.write(b'\x01')
    reg = self.smu.rsns.read(1)

    if (self.channel == 0):
      reg = (reg[0] & 0x0c) + value
    else:
      reg = (reg[0] & 0x03) + (value << 2)
    self.smu.rsns.write(bytes([0x01, reg]))
    self.current_range = value
    time.sleep(0.01)

  def get_current_raw(self, average):
    if average:
      setup_data = bytes([0x21 | (self.channel << 1)])
    else:
      setup_data = bytes([0x61 | (self.channel << 1)])
    self.smu.adc.write(setup_data)
    if average:
      i2c_data = self.smu.adc.read(16)
      current = 0
      for i in range(8):
        current += 0x0fff & int.from_bytes(i2c_data[(2*i):(2*i+2)],"big")
      current = current / 8.0
    else:
      i2c_data = self.smu.adc.read(2)
      current = 0x0fff & int.from_bytes(i2c_data,"big")
    return current

  def get_current(self, current_range='auto', average = False):
    if (current_range != 'auto'):
      if (self.current_range != current_range):
        self.set_current_range(current_range)
      raw_value =  self.get_current_raw(average) 
    else:  # autoscaling
      raw_value = self.get_current_raw(average)
      while (raw_value < lower_limit and self.current_range > 1):
        self.set_current_range(self.current_range-1)
        raw_value = self.get_current_raw(average)
      while (raw_value > upper_limit and self.current_range < 3):
        self.set_current_range(self.current_range+1)
        raw_value = self.get_current_raw(average)
#    return (raw_value - adc_offset) / rsns_list[self.current_range]
    return (raw_value - adc_offset - adc_cm_gain * self.dac_value) / rsns_list[self.current_range]
  
  def close(self):
    self.set_voltage(0)
    self.set_current_range(0)

  
if __name__ == '__main__':

  fig, ax = plt.subplots(2,2, sharex='col')

  voltage_sweep  = np.arange(0, 2, 0.01)
  current_data_array = np.empty([8, voltage_sweep.size])

  smu = SMU()

  smu.ch[1].set_voltage(0.1) 

  # sweep in auto current ranging mode
  for voltage_step, voltage in enumerate(voltage_sweep):
    smu.ch[0].set_voltage(voltage)   
    smu.ch[1].set_voltage(voltage) 
    current_data_array[0][voltage_step] = smu.ch[0].get_current() 
    current_data_array[1][voltage_step] = smu.ch[1].get_current() 

  # sweeps with fixed current range
  for voltage_step, voltage in enumerate(voltage_sweep):
    smu.ch[0].set_voltage(voltage)   
    smu.ch[1].set_voltage(voltage) 
    current_data_array[2][voltage_step] = smu.ch[0].get_current(current_range = 1) 
    current_data_array[3][voltage_step] = smu.ch[1].get_current(current_range = 1) 

  for voltage_step, voltage in enumerate(voltage_sweep):
    smu.ch[0].set_voltage(voltage)   
    smu.ch[1].set_voltage(voltage) 
    current_data_array[4][voltage_step] = smu.ch[0].get_current(current_range = 2) 
    current_data_array[5][voltage_step] = smu.ch[1].get_current(current_range = 2) 

  for voltage_step, voltage in enumerate(voltage_sweep):
    smu.ch[0].set_voltage(voltage)   
    smu.ch[1].set_voltage(voltage) 
    current_data_array[6][voltage_step] = smu.ch[0].get_current(current_range = 3) 
    current_data_array[7][voltage_step] = smu.ch[1].get_current(current_range = 3) 
    
  smu.close()

  ax[0,0].plot(voltage_sweep, current_data_array[0], label='auto')
  ax[0,1].plot(voltage_sweep, current_data_array[1], label='auto')
  ax[0,0].plot(voltage_sweep, current_data_array[2], label='low')
  ax[0,1].plot(voltage_sweep, current_data_array[3], label='low')
  ax[0,0].plot(voltage_sweep, current_data_array[4], label='mid')
  ax[0,1].plot(voltage_sweep, current_data_array[5], label='mid')
  ax[0,0].plot(voltage_sweep, current_data_array[6], label='high')
  ax[0,1].plot(voltage_sweep, current_data_array[7], label='high')
  ax[1,0].semilogy(voltage_sweep, current_data_array[0], label='auto')
  ax[1,1].semilogy(voltage_sweep, current_data_array[1], label='auto')
  ax[1,0].semilogy(voltage_sweep, current_data_array[2], label='low')
  ax[1,1].semilogy(voltage_sweep, current_data_array[3], label='low')
  ax[1,0].semilogy(voltage_sweep, current_data_array[4], label='mid')
  ax[1,1].semilogy(voltage_sweep, current_data_array[5], label='mid')
  ax[1,0].semilogy(voltage_sweep, current_data_array[6], label='high')
  ax[1,1].semilogy(voltage_sweep, current_data_array[7], label='high')

  ax[0,0].set_title('Ch 1')  
  ax[0,1].set_title('Ch 2')

  for a in ax.flat:
    a.set(ylabel='I (mA)')
    a.grid()
    a.legend(title='current range')

  plt.show()


