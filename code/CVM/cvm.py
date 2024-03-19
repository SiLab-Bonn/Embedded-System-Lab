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


smu = SMU()
cvm = smu.ch[0]
cvm.set_current_range(2)
cvm.set_voltage(1)

GPIO.setup()
GPIO.set_gpio_mode(CLK, GPIO_MODE_ALT0) 
#GPIO.set_gpio_mode(CLK, GPIO_MODE_OUT) 
#GPIO.set_gpio_out(CLK, 1) 


voltage_values = range(0, 2000, 20)
frequency_values = range(100, 1100, 100) # frequency in kHz units
current_values = []

#for voltage in voltage_values:
for frequency in frequency_values:
  GPIO.set_gpclk_freq(frequency, GPCLK0) 
  time.sleep(0.01)
  current = cvm.get_current(average = True, current_range = 2)
  current_values.append(current)
  print("Frequency:", frequency ," current [mA]:", current)


fig, ax = plt.subplots()
# ax.plot(voltage_values, current_values)
# ax.set(xlabel='Voltage (mV)', ylabel='Current (mA)', title='I-V Curve')

ax.plot(frequency_values, current_values)
ax.set(xlabel='Frequency [kHz]', ylabel='Current (mA)', title='I-F Curve')

plt.show()

# switch off
GPIO.set_gpclk_freq(0, GPCLK0) # switch off
smu.close()
GPIO.cleanup(1)

