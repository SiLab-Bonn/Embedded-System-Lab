import time
from i2cdev import I2C
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
from smu_class import SMU

# fig, ax = plt.subplots(2,2, sharex='col')

# voltage_sweep  = np.arange(0, 2, 0.01)
# current_data_array = np.empty([8, voltage_sweep.size])

# smu = SMU()

# smu.ch[1].set_voltage(0.1) 

# # sweep in auto current ranging mode
# for voltage_step, voltage in enumerate(voltage_sweep):
#   smu.ch[0].set_voltage(voltage)   
#   smu.ch[1].set_voltage(voltage) 
#   current_data_array[0][voltage_step] = smu.ch[0].get_current() 
#   current_data_array[1][voltage_step] = smu.ch[1].get_current() 

# # sweeps with fixed current range
# for voltage_step, voltage in enumerate(voltage_sweep):
#   smu.ch[0].set_voltage(voltage)   
#   smu.ch[1].set_voltage(voltage) 
#   current_data_array[2][voltage_step] = smu.ch[0].get_current(current_range = 1) 
#   current_data_array[3][voltage_step] = smu.ch[1].get_current(current_range = 1) 

# for voltage_step, voltage in enumerate(voltage_sweep):
#   smu.ch[0].set_voltage(voltage)   
#   smu.ch[1].set_voltage(voltage) 
#   current_data_array[4][voltage_step] = smu.ch[0].get_current(current_range = 2) 
#   current_data_array[5][voltage_step] = smu.ch[1].get_current(current_range = 2) 

# for voltage_step, voltage in enumerate(voltage_sweep):
#   smu.ch[0].set_voltage(voltage)   
#   smu.ch[1].set_voltage(voltage) 
#   current_data_array[6][voltage_step] = smu.ch[0].get_current(current_range = 3) 
#   current_data_array[7][voltage_step] = smu.ch[1].get_current(current_range = 3) 
  
# smu.close()

# ax[0,0].plot(voltage_sweep, current_data_array[0], label='auto')
# ax[0,1].plot(voltage_sweep, current_data_array[1], label='auto')
# ax[0,0].plot(voltage_sweep, current_data_array[2], label='low')
# ax[0,1].plot(voltage_sweep, current_data_array[3], label='low')
# ax[0,0].plot(voltage_sweep, current_data_array[4], label='mid')
# ax[0,1].plot(voltage_sweep, current_data_array[5], label='mid')
# ax[0,0].plot(voltage_sweep, current_data_array[6], label='high')
# ax[0,1].plot(voltage_sweep, current_data_array[7], label='high')
# ax[1,0].semilogy(voltage_sweep, current_data_array[0], label='auto')
# ax[1,1].semilogy(voltage_sweep, current_data_array[1], label='auto')
# ax[1,0].semilogy(voltage_sweep, current_data_array[2], label='low')
# ax[1,1].semilogy(voltage_sweep, current_data_array[3], label='low')
# ax[1,0].semilogy(voltage_sweep, current_data_array[4], label='mid')
# ax[1,1].semilogy(voltage_sweep, current_data_array[5], label='mid')
# ax[1,0].semilogy(voltage_sweep, current_data_array[6], label='high')
# ax[1,1].semilogy(voltage_sweep, current_data_array[7], label='high')

# ax[0,0].set_title('Ch 1')  
# ax[0,1].set_title('Ch 2')

# for a in ax.flat:
#   a.set(ylabel='I (mA)')
#   a.grid()
#   a.legend(title='current range')

# plt.show()


smu   = SMU()
gate  = smu.ch[0]
drain = smu.ch[1]

# input characteristics: Id(Ugs)
fig1, ax = plt.subplots(3,2, sharex='col')
gate_voltage_sweep       = np.arange(0.0, 2.0, 0.01)
drain_voltage_parameter  = np.arange(0.1, 0.6, 0.2)
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
  gm = np.diff(current_data_array[uds_index], prepend = 0)/np.diff(gate_voltage_sweep, prepend = 0.5)

  ax[0,1].plot(gate_voltage_sweep, gm)
  ax[1,1].plot(gate_voltage_sweep, gm/np.sqrt(current_data_array[uds_index]))
  ax[2,1].plot(gate_voltage_sweep, gm/current_data_array[uds_index])  

# output chracteristics: Id(Uds)
fig2, bx = plt.subplots()
drain_voltage_sweep    = np.arange(0.0, 0.6, 0.001)
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
ax[1,1].set_ylim(-5, )

ax[2,1].set(xlabel='Ugs [V]', ylabel='gm/Id [1/V]')
ax[2,1].grid()
ax[2,1].set_ylim(-5, )

bx.set(xlabel='Uds [V]', ylabel='Id [mA]')
bx.legend(title="Ugs")
bx.grid()

plt.show()
