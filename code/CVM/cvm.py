import time
import matplotlib.pyplot as plt
import numpy as np
#from tqdm import tqdm
import ctypes
import sys
sys.path.insert(1, '/home/pi/Embedded-System-Lab/code/SMU')
from smu_class import SMU

CLK = 4            # gPIO pin 
GPIO_MODE_OUT  = 1 # set GPIO to output
GPIO_MODE_ALT0 = 4 # set GPIO alternative mode 0
GPCLK0 = 0         # GPCLK 0

# access to c-library for enhanced GPIO access 
GPIO = ctypes.CDLL("/home/pi/Embedded-System-Lab/code/lib/gpio_clib.so")  

smu_voltage = 3000

smu = SMU()
cvm = smu.ch[0]
cvm.set_current_range(2)

GPIO.setup()
GPIO.set_gpio_mode(CLK, GPIO_MODE_ALT0) 
#GPIO.set_gpio_mode(CLK, GPIO_MODE_OUT) 
#GPIO.set_gpio_out(CLK, 1) 

voltage_values   = np.arange(2000, 3001, 500)
frequency_values = np.arange(100, 1100, 100) # frequency in kHz units
current_values   = np.empty([voltage_values.size, frequency_values.size])

fig, ax = plt.subplots()

for voltage_index, smu_voltage in enumerate(voltage_values):
  cvm.set_voltage(smu_voltage)
  time.sleep(0.01)
  for frequency_index, frequency in enumerate(frequency_values):
    GPIO.set_gpclk_freq(int(frequency), GPCLK0) 
    time.sleep(0.01)
    current = cvm.get_current(average = True)
    current_values[voltage_index][frequency_index] = current
    #print("Frequency:", frequency ," current [mA]:", current)

  ax.plot(frequency_values, current_values[voltage_index])

  corrected_current_values = [current * smu_voltage/(smu_voltage - current * 1000000) for current in current_values[voltage_index]]
 # slope = np.polyfit(frequency_values, corrected_current_values, 1)[0]
  slope = np.polyfit(frequency_values, current_values[voltage_index], 1)[0]
  capacitance = slope/smu_voltage * 1e9 # (mA/kHz)/mV  -> mF 

  print('smu_voltage: %.0f mV' % smu_voltage)
  print('slope: %.4f nA/kHz' % (slope * 1000000))
  print('capacitance: %.2f pF' % capacitance)


ax.set(xlabel='Frequency [kHz]', ylabel='Current (mA)', title='I-F Curve')
plt.show()

# switch off
GPIO.set_gpclk_freq(0, GPCLK0) # switch off
smu.close()
GPIO.cleanup(1)

