import time
from i2cdev import I2C
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM) # use pin numbers according to the GPIO naming
import sys
sys.path.insert(1, '/home/pi/Embedded-System-Lab/code/SMU')
from smu_class import SMU

CLK = 4

#GPIO.setup(CLK, GPIO.)

smu   = SMU()
cvm  = smu.ch[0]
cvm.set_current_range(1)

voltage_values = range(0,2000, 20)
current_values = []

for voltage in voltage_values:
  cvm.set_voltage(voltage/1000)
  current = cvm.get_current(average = True)
  current_values.append(current)
  print("H1 voltage [mV]:", voltage ," current [mA]:", current)
 # print("ADC counts:", current_raw)

fig, ax = plt.subplots()
ax.plot(voltage_values, current_values)

ax.set(xlabel='Voltage (mV)', ylabel='Current (mA)', title='I-V Curve')

plt.show()

# switch off
smu.close

