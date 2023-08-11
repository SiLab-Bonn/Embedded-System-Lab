import time
from i2cdev import I2C
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
from smu_class import SMU

smu   = SMU()
gate  = smu.ch[0]
drain = smu.ch[1]

# input characteristics: Id(Ugs)
fig1, ax = plt.subplots(3,2, sharex='col')
gate_voltage_sweep       = np.arange(0.0, 2.0, 0.01)
drain_voltage_parameter  = np.arange(0.05, 0.6, 0.2)
current_data_array = np.empty([drain_voltage_parameter.size, gate_voltage_sweep.size])

# Id vs Ugs
for uds_index, uds in enumerate(drain_voltage_parameter):
  drain.set_voltage(uds)  
  for ugs_index, ugs in tqdm(enumerate(gate_voltage_sweep)):
    gate.set_voltage(ugs) 
    current_data_array[uds_index][ugs_index] = drain.get_current(average=True) 
  ax[0,0].plot(gate_voltage_sweep, current_data_array[uds_index], label="{:.2f}".format(uds))
  ax[1,0].semilogy(gate_voltage_sweep, current_data_array[uds_index], label="{:.2f}".format(uds))
  ax[2,0].plot(gate_voltage_sweep, np.sqrt(current_data_array[uds_index]), label="{:.2f}".format(uds))

  # gm vs Id
  gm = np.diff(current_data_array[uds_index], prepend = 0)/(np.diff(gate_voltage_sweep, prepend = 0.5) * 1000)

  ax[0,1].plot(gate_voltage_sweep, gm)
  ax[1,1].plot(gate_voltage_sweep, gm/np.sqrt(current_data_array[uds_index]))
  ax[2,1].plot(gate_voltage_sweep, gm/current_data_array[uds_index])  

# output chracteristics: Id(Uds)
fig2, bx = plt.subplots()
drain_voltage_sweep    = np.arange(0.0, 4.0, 0.01)
gate_voltage_parameter = np.arange(0.6, 1, 0.1)
current_data_array = np.empty([gate_voltage_parameter.size, drain_voltage_sweep.size])

for ugs_index, ugs in enumerate(gate_voltage_parameter):
  gate.set_voltage(ugs)  
  time.sleep(0.05)
  for uds_index, uds in tqdm(enumerate(drain_voltage_sweep)):
    drain.set_voltage(uds) 
    time.sleep(0.005)
    current_data_array[ugs_index][uds_index] = drain.get_current(average=True) 
  bx.plot(drain_voltage_sweep, current_data_array[ugs_index], label="{:.2f}".format(ugs))

smu.close()

ax[0,0].set(ylabel='Id [mA]')
ax[0,0].legend(title="Uds")
ax[0,0].grid()

ax[1,0].set(ylabel='Id [mA]')
ax[1,0].grid()

ax[2,0].set(xlabel='Ugs [V]', ylabel='SQRT(Id [mA])')
ax[2,0].grid()

ax[0,1].set(ylabel='gm [A/V]')
ax[0,1].grid()
ax[0,1].set_ylim(-0.1, )

ax[1,1].set(ylabel='gm/SQRT(Id) [1/SQRT(V)]')
ax[1,1].grid()
ax[1,1].set_ylim(-0.01, 0.05)

ax[2,1].set(xlabel='Ugs [V]', ylabel='gm/Id [1/V]')
ax[2,1].grid()
ax[2,1].set_ylim(-0.01, 0.06)

bx.set(xlabel='Uds [V]', ylabel='Id [mA]')
bx.legend(title="Ugs")
bx.grid()

plt.show()
