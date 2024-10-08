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
gate_voltage_sweep       = np.arange( 0, 2000,  10)
drain_voltage_parameter  = np.arange(100,  201, 50)
current_data_array = np.empty([drain_voltage_parameter.size, gate_voltage_sweep.size])

fig1, ax = plt.subplots(3,2, sharex='col')
# Id vs Ugs
for uds_index, uds in enumerate(drain_voltage_parameter):
  drain.set_voltage(uds)  
  for ugs_index, ugs in tqdm(enumerate(gate_voltage_sweep)):
    gate.set_voltage(ugs) 
    current_data_array[uds_index][ugs_index] = drain.get_current() 

  # plot drain current in linear representation
  ax[0,0].plot(gate_voltage_sweep, current_data_array[uds_index], label="{:.2f}".format(uds))

  # plot sqrt of the drain current
  ax[1,0].plot(gate_voltage_sweep, np.sqrt(current_data_array[uds_index]), label="{:.2f}".format(uds))

  # plot log of the drain current, 
  ax[2,0].semilogy(gate_voltage_sweep, current_data_array[uds_index], label="{:.2f}".format(uds))

  # trasconductance gm = d(Id)/d(Ugs)
  gm = np.diff(current_data_array[uds_index], prepend = 0)/(np.diff(gate_voltage_sweep, prepend = 0.5))

  # plot gm
  ax[0,1].plot(gate_voltage_sweep, gm)

  # plot gm/sqrt(Id)
  ax[1,1].plot(gate_voltage_sweep, gm/np.sqrt(current_data_array[uds_index]))

  # plot gm/Id
  ax[2,1].plot(gate_voltage_sweep, gm/current_data_array[uds_index])  

# output characteristics: Id(Uds)
fig2, bx = plt.subplots(2,1)
drain_voltage_sweep    = np.arange(  0, 4000, 10)
gate_voltage_parameter = np.arange(800, 1401, 200)
current_data_array = np.empty([gate_voltage_parameter.size, drain_voltage_sweep.size])

for ugs_index, ugs in enumerate(gate_voltage_parameter):
  gate.set_voltage(ugs)  
  for uds_index, uds in tqdm(enumerate(drain_voltage_sweep)):
    drain.set_voltage(uds) 
    current_data_array[ugs_index][uds_index] = drain.get_current() 
  bx[0].plot(drain_voltage_sweep, current_data_array[ugs_index], label="{:.2f}".format(ugs))

time.sleep(0.1)

drain_voltage_sweep    = np.arange(  0, 400, 1)
gate_voltage_parameter = np.arange(800, 1401, 200)
current_data_array = np.empty([gate_voltage_parameter.size, drain_voltage_sweep.size])

for ugs_index, ugs in enumerate(gate_voltage_parameter):
  gate.set_voltage(ugs)  
  for uds_index, uds in tqdm(enumerate(drain_voltage_sweep)):
    drain.set_voltage(uds) 
    current_data_array[ugs_index][uds_index] = drain.get_current() 
  bx[1].plot(drain_voltage_sweep, current_data_array[ugs_index], label="{:.2f}".format(ugs))  

smu.close()

fig1.suptitle('Id vs Ugs')

ax[0,0].set(ylabel='Id [mA]')
ax[0,0].legend(title="Uds [mV]")
ax[0,0].grid()

ax[1,0].text(0, 5, 'sqrt(Id) is proportional to Ugs \nin strong inversion operation', wrap=True, fontsize=8, ha='left')
ax[1,0].set(ylabel='sqrt(Id [mA])')
ax[1,0].grid()

ax[2,0].text(0, 1, 'ln(Id) is proportional to Ugs \nin weak inversion operation', wrap=True, fontsize=8, ha='left')
ax[2,0].set(xlabel='Ugs [mV]', ylabel='Id [mA]')
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
bx[0].set(xlabel='Uds [mV]', ylabel='Id [mA]')
bx[0].legend(title="Ugs [mV]", loc='upper right')
bx[0].grid()
bx[1].set(xlabel='Uds [mV]', ylabel='Id [mA]')
bx[1].legend(title="Ugs [mV]", loc='upper right')
bx[1].grid()


plt.show()
