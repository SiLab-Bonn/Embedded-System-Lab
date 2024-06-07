import time
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import savgol_filter
import ctypes
import sys
sys.path.insert(1, '/home/pi/Embedded-System-Lab/code/SMU')
sys.path.insert(1, '/home/pi/Embedded-System-Lab/code/LabDevices')
from smu_class import SMU
from KA3005P import KA3005P

CLK = 4            # GPIO pin for clock output
GPIO_MODE_ALT0 = 4 # GPIO alternative mode 0 (GPCLK0 on GPIO 4)
R_SERIES = 1000    # kOhm series resitor in current path (value needed to correct for its voltage drop)
parasitic_capacitance = 5.4 # CVM module with no diode plugged in

# BPW34 diode data and other constants
e0 = 8.85e-14       # F/cm
er = 11.7           # relative permittivity of Si
A_diode = 0.0702    # cm^2, diode area
q = 1.602e-19       # C, elementary charge

# access to C-library for enhanced GPIO access 
gpio = ctypes.CDLL("/home/pi/Embedded-System-Lab/code/lib/gpio_clib.so")  

# voltage source with current measurement
smu = SMU()
cvm = smu.ch[0]
#cvm.set_current_range('low')
cvm.enable_autorange()

# clock output
gpio.setup()
gpio.set_gpio_mode(CLK, GPIO_MODE_ALT0) 

# bias voltage source
vbias = KA3005P()

# scan parameters
smu_voltage = 1500  # voltage amplitude for charge measurement
frequency_values = np.arange(200, 600, 50)   # switch frequency in kHz units
current_values   = np.empty(frequency_values.size)
vbias_values     = np.arange(0, 30.1, 0.1)
capacitance_values = np.empty(vbias_values.size)

fig, ax = plt.subplots(2,2)

cvm.set_voltage(smu_voltage) # mV units
vbias.set_voltage(0)
vbias.enable_output()

for vbias_index, bias_voltage in enumerate(vbias_values):
  vbias.set_voltage(bias_voltage)
  time.sleep(1)
  for frequency_index, frequency in enumerate(frequency_values):
    gpio.set_gpclk_freq(int(frequency)) 
    time.sleep(0.05)
    current = cvm.get_current()  # mA units
    current_values[frequency_index] = current

  corrected_current_values = [current * smu_voltage/(smu_voltage - current * R_SERIES) for current in current_values]
  slope = np.polyfit(frequency_values, corrected_current_values, 1)[0]
  capacitance = slope/smu_voltage * 1e9 # pF units: (mA/kHz)/mV * 1e9 
  print('capacitance: %.2f pF' % capacitance)
  capacitance_values[vbias_index] = capacitance

# remove parasitic capacitance
capacitance_values = capacitance_values - parasitic_capacitance 
# smoothing
capacitance_values = savgol_filter(capacitance_values, 20, 2) 

# calculate effective doping density calculation
depletion_width_values = (e0 * er * A_diode)/(capacitance_values/1e12) * 1e4 # pF to F, cm to µm
depletion_width_values = savgol_filter(depletion_width_values, 9, 2) 
capacitance_derivative = np.gradient(1/(capacitance_values/1e12 * capacitance_values/1e12))

neff = 2/(A_diode*A_diode*e0*er*q)*1/capacitance_derivative


vbias.set_voltage(0)
vbias.disable_output()
gpio.set_gpclk_freq(0) 

ax[0][0].plot(vbias_values, capacitance_values)
ax[0][0].set(ylabel='Capacitance (pF)', title='C-V Curve')

ax[1][0].plot(vbias_values, 1/(capacitance_values * capacitance_values * capacitance_values))
ax[1][0].set(xlabel='Vbias [V]', ylabel='1/(Capacitance (pF))3', title='C-V Curve')

ax[0][1].plot(vbias_values, depletion_width_values)
ax[0][1].set(xlabel='Vbias [V]', ylabel='depletion width (µm)', title='Depletion Width')

ax[1][1].plot(depletion_width_values, neff)
ax[1][1].set(xlabel='d (µm)', ylabel='Neff (cm-3)', title='Doping Concentration')
ax[1][1].set_yscale('log')

plt.show()

# cleanup & switch off
vbias.close()
smu.close()
gpio.cleanup(1)

