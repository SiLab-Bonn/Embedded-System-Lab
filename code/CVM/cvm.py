import time
import matplotlib.pyplot as plt
import numpy as np
import ctypes
import sys
sys.path.insert(1, '/home/pi/Embedded-System-Lab/code/SMU')
from smu_class import SMU

CLK = 4            # GPIO pin for clock output
GPIO_MODE_ALT0 = 4 # GPIO alternative mode 0 (GPCLK0 on GPIO 4)
R_SERIES = 1000    # kOhm series resitor in current path (value needed to correct for its voltage drop)

# access to C-library for enhanced GPIO access 
GPIO = ctypes.CDLL("/home/pi/Embedded-System-Lab/code/lib/gpio_clib.so")  

# voltage source with current measurement
smu = SMU()
cvm = smu.ch[0]
cvm.enable_autorange()

# clock output
GPIO.setup()
GPIO.set_gpio_mode(CLK, GPIO_MODE_ALT0) 

# scan parameters
smu_voltage = 1500  # voltage amplitude for charge measurement
frequency_values = np.arange(100, 1000, 100)   # switch frequency in kHz units
current_values   = np.empty(frequency_values.size)

fig, ax = plt.subplots()

cvm.set_voltage(smu_voltage) # mV units
for frequency_index, frequency in enumerate(frequency_values):
  GPIO.set_gpclk_freq(int(frequency)) 
  time.sleep(0.05)
  current = cvm.get_current()  # mA units
  current_values[frequency_index] = current

ax.plot(frequency_values, current_values)

corrected_current_values = [current * smu_voltage/(smu_voltage - current * R_SERIES) for current in current_values]
slope, offset = np.polyfit(frequency_values, corrected_current_values, 1)
capacitance = slope/smu_voltage * 1e9 # pF units: (mA/kHz)/mV * 1e9 

print('offset: %.4f nA' % (offset * 1e6))
print('slope: %.4f nA/kHz' % (slope * 1e6))
print('capacitance: %.2f pF' % capacitance)

ax.set(xlabel='Frequency [kHz]', ylabel='Current (mA)', title='I-F Curve')
#plt.show()

# switch off
GPIO.set_gpclk_freq(0) # switch off
smu.close()
GPIO.cleanup(1)

