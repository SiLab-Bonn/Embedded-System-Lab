import time
from i2cdev import I2C
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
from smu_class import SMU

smu   = SMU()
gate  = smu.ch[0]
drain = smu.ch[1]

gate.set_current_range('low')
drain.enable_autorange()

# input characteristics: Id(Ugs)
fig1, ax = plt.subplots(3,2, sharex='col')
gate_voltage_sweep       = np.arange( 0, 2000,  10)
drain_voltage_parameter  = np.arange(100,  201, 50)
current_data_array = np.empty([drain_voltage_parameter.size, gate_voltage_sweep.size])

# Id vs Ugs
for uds_index, uds in enumerate(drain_voltage_parameter):
  drain.set_voltage(uds)  
  for ugs_index, ugs in tqdm(enumerate(gate_voltage_sweep)):
    gate.set_voltage(ugs) 
    current_data_array[uds_index][ugs_index] = drain.get_current() 
  ax[0,0].plot(gate_voltage_sweep, current_data_array[uds_index], label="{:.2f}".format(uds))
  ax[1,0].plot(gate_voltage_sweep, np.sqrt(current_data_array[uds_index]), label="{:.2f}".format(uds))
  ax[2,0].semilogy(gate_voltage_sweep, current_data_array[uds_index], label="{:.2f}".format(uds))

  # gm vs Id
  gm = np.diff(current_data_array[uds_index], prepend = 0)/(np.diff(gate_voltage_sweep, prepend = 0.5))

  ax[0,1].plot(gate_voltage_sweep, gm)
  ax[1,1].plot(gate_voltage_sweep, gm/np.sqrt(current_data_array[uds_index]))
  ax[2,1].plot(gate_voltage_sweep, gm/current_data_array[uds_index])  

# output chracteristics: Id(Uds)
fig2, bx = plt.subplots()
drain_voltage_sweep    = np.arange(  0, 4000, 10)
gate_voltage_parameter = np.arange(800, 1400, 200)
current_data_array = np.empty([gate_voltage_parameter.size, drain_voltage_sweep.size])

for ugs_index, ugs in enumerate(gate_voltage_parameter):
  gate.set_voltage(ugs)  
  for uds_index, uds in tqdm(enumerate(drain_voltage_sweep)):
    drain.set_voltage(uds) 
    current_data_array[ugs_index][uds_index] = drain.get_current() 
  bx.plot(drain_voltage_sweep, current_data_array[ugs_index], label="{:.2f}".format(ugs))

smu.close()

fig1.suptitle('Id vs Ugs')

ax[0,0].set(ylabel='Id [mA]')
ax[0,0].legend(title="Uds [mV]")
ax[0,0].grid()

ax[1,0].text(0, 5, 'sqrt(Id) is proportional to Ugs \nin strong inversion operation', wrap=True, fontsize=8, ha='left')
ax[1,0].grid()

ax[2,0].text(0, 1, 'exp(Id) is proportional to Ugs \nin weak inversion operation', wrap=True, fontsize=8, ha='left')
ax[2,0].set(xlabel='Ugs [mV]', ylabel='SQRT(Id [mA])')
ax[2,0].set(ylabel='Id [mA]')
ax[2,0].grid()

ax[0,1].text(0, 0.3, 'gm is a linear function of Ugs-Uthr\nin strong inversion operation', wrap=True, fontsize=8, ha='left')
ax[0,1].set(ylabel='gm [A/V]')
ax[0,1].grid()
ax[0,1].set_ylim(0, 0.4)

ax[1,1].text(0, 0.04, 'gm/sqrt(Id) is constant \nin strong inversion operation', wrap=True, fontsize=8, ha='left')
ax[1,1].set(ylabel='gm/SQRT(Id) [1/SQRT(mV)]')
ax[1,1].grid()
ax[1,1].set_ylim(0, 0.05)

ax[2,1].text(0, 0.04, 'gm/Id is constant \nin weak inversion operation', wrap=True, fontsize=8, ha='left')
ax[2,1].set(xlabel='Ugs [mV]', ylabel='gm/Id [1/V]')
ax[2,1].grid()
ax[2,1].set_ylim(0, 0.05)

fig2.suptitle('Id vs Uds')
bx.set(xlabel='Uds [mV]', ylabel='Id [mA]')
bx.legend(title="Ugs [mV]")
bx.grid()

plt.show()
