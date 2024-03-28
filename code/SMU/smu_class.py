import time
from i2cdev import I2C
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

# DAC channels
CH1 = 1
CH2 = 2

# current sense range
current_range = {
  "off":  0,  # MUX off
  "low":  1,  # 80 kOhm
  "mid":  2,  # 800 Ohm
  "high": 3,  # 8 Ohm
}

# current sense gain setting resistor
rsns_list   = [float("inf"), 800000, 8000, 80]  # effective transimpedance = Rsns x 10
adc_offset  = 6
adc_cm_gain = 0.0045
upper_limit = 4050  # upper limit for current measurement (ADC counts)
lower_limit =   50  # lower limit for current measurement (ADC counts)

class SMU:
  """SMU object instanciates and initializes ADC, DAC, the selectable sense 
  resistor multiplexer for setting the outout current range, and the two SMU channels.
  """
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
  """SMU output channel, instanciated in the SMU object."""
  def __init__(self, smu, channel):
    self.channel = channel-1
    self.smu = smu
    self.auto_ranging = True
    self.set_current_range('off')    
    self.set_voltage(0)    

  def set_voltage(self, milli_volt):
    """Set output voltage in mV units"""
    self.dac_value = int(milli_volt) # 12 bit DAC, VREF = 4096mV, VOUT = #DAC[mV]
    channel_reg = self.channel << 3
    i2c_data = bytes([channel_reg, (self.dac_value >> 8), (self.dac_value & 0xff)])
    self.smu.dac.write(i2c_data)

  def enable_autorange(self):
    self.auto_ranging = True
    self.set_current_range('low')

  def disable_autorange(self):
    self.auto_ranging = False

  def set_current_range(self, value_string):
    """The output current range is defined by the size of the selctable sense resistor:
      state        Rsns       Imax      Ilsb  
      "off"   0     --
      "low"   1   80 kOhm     5 µA    1.25 nA
      "mid"   2  800 Ohm    500 µA     125 nA
      "high"  3    8 Ohm     50 mA    12.5 µA
    """
    value = current_range[value_string]
    if ((value < 0) | (value > 3)):
      print("Current range outside of [0, 3]")
      return

    self.current_range = value_string
    
    # read current output state
    self.smu.rsns.write(b'\x01')
    reg = self.smu.rsns.read(1)

    if (self.channel == 0):
      reg = (reg[0] & 0x0c) + value
    else:
      reg = (reg[0] & 0x03) + (value << 2)
    self.smu.rsns.write(bytes([0x01, reg]))
    time.sleep(0.01)

  def get_current_raw(self, average):
    """Reads the raw ADC counts. If "average" is true, the ADC sends 8 consequtive samples which 
    get averaged before returning the result.
    """
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

  def get_current(self, average = True):
    """Returns the measured current in mA units. If "current_range" is set to "auto", the current range is automatically 
    selected to operate the ADC and the output buffer within their operational range.
    """
    if (self.current_range == current_range['off']):
      print("SMU channel is off. Set current range > 0 to switch on.")
      return(0)

    raw_value = self.get_current_raw(average)
    
    if (self.auto_ranging): 
      while ((raw_value < lower_limit) and (self.current_range != 'low')):
        if (self.current_range == 'mid'):
          self.set_current_range('low')
        if (self.current_range == 'high'):
          self.set_current_range('mid')
        raw_value = self.get_current_raw(average)
      while ((raw_value > upper_limit) and (self.current_range != 'high')):
        if (self.current_range == 'mid'):
          self.set_current_range('high')
        if (self.current_range == 'low'):
          self.set_current_range('mid')
        raw_value = self.get_current_raw(average)
        
#    return (raw_value - adc_offset) / rsns_list[self.current_range]
    return (raw_value - adc_offset - adc_cm_gain * self.dac_value) / rsns_list[current_range[self.current_range]]
  
  def close(self):
    self.set_voltage(0)
    self.set_current_range('off')

  
if __name__ == '__main__':

  fig, ax = plt.subplots(2,2, sharex='col')

  voltage_sweep  = np.arange(0, 2000, 10)
  current_data_array = np.empty([8, voltage_sweep.size])

  smu = SMU()

  # sweep in auto current ranging mode
  smu.ch[0].enable_autorange()
  smu.ch[1].enable_autorange()
  for voltage_step, voltage in enumerate(voltage_sweep):
    smu.ch[0].set_voltage(voltage)   
    smu.ch[1].set_voltage(voltage) 
    current_data_array[0][voltage_step] = smu.ch[0].get_current() 
#    current_data_array[1][voltage_step] = smu.ch[1].get_current() 

  # # sweeps with fixed current range
  #smu.ch[0].disable_autorange()
  #smu.ch[1].disable_autorange()
  # smu.ch[0].set_current_range('low')
  # smu.ch[1].set_current_range('low')
  # for voltage_step, voltage in enumerate(voltage_sweep):
  #   smu.ch[0].set_voltage(voltage)   
  #   smu.ch[1].set_voltage(voltage) 
  #   current_data_array[2][voltage_step] = smu.ch[0].get_current() 
  #   current_data_array[3][voltage_step] = smu.ch[1].get_current() 

  # smu.ch[0].set_current_range('mid')
  # smu.ch[1].set_current_range('mid')
  # for voltage_step, voltage in enumerate(voltage_sweep):
  #   smu.ch[0].set_voltage(voltage)   
  #   smu.ch[1].set_voltage(voltage) 
  #   current_data_array[4][voltage_step] = smu.ch[0].get_current() 
  #   current_data_array[5][voltage_step] = smu.ch[1].get_current()

  # smu.ch[0].set_current_range('high')
  # smu.ch[1].set_current_range('high') 
  # for voltage_step, voltage in enumerate(voltage_sweep):
  #   smu.ch[0].set_voltage(voltage)   
  #   smu.ch[1].set_voltage(voltage) 
  #   current_data_array[6][voltage_step] = smu.ch[0].get_current() 
  #   current_data_array[7][voltage_step] = smu.ch[1].get_current() 
    
  smu.close()

  ax[0,0].plot(voltage_sweep, current_data_array[0], label='auto')
 # ax[0,1].plot(voltage_sweep, current_data_array[1], label='auto')
  # ax[0,0].plot(voltage_sweep, current_data_array[2], label='low')
  # ax[0,1].plot(voltage_sweep, current_data_array[3], label='low')
  # ax[0,0].plot(voltage_sweep, current_data_array[4], label='mid')
  # ax[0,1].plot(voltage_sweep, current_data_array[5], label='mid')
  # ax[0,0].plot(voltage_sweep, current_data_array[6], label='high')
  # ax[0,1].plot(voltage_sweep, current_data_array[7], label='high')
  ax[1,0].semilogy(voltage_sweep, current_data_array[0], label='auto')
  #ax[1,1].semilogy(voltage_sweep, current_data_array[1], label='auto')
  # ax[1,0].semilogy(voltage_sweep, current_data_array[2], label='low')
  # ax[1,1].semilogy(voltage_sweep, current_data_array[3], label='low')
  # ax[1,0].semilogy(voltage_sweep, current_data_array[4], label='mid')
  # ax[1,1].semilogy(voltage_sweep, current_data_array[5], label='mid')
  # ax[1,0].semilogy(voltage_sweep, current_data_array[6], label='high')
  # ax[1,1].semilogy(voltage_sweep, current_data_array[7], label='high')

  ax[0,0].set_title('Ch 1')  
 # ax[0,1].set_title('Ch 2')

  for a in ax.flat:
    a.set(ylabel='I (mA)')
    a.grid()
  #  a.legend(title='current range')

  plt.show()


