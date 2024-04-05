import matplotlib.pyplot as plt
import numpy as np


# Parameters for plotting the three current measurement ranges

# ADC and DAC dynamic range in mV
DAC_range = 4096
ADC_range = 4096

# ADC and DAC resolution
DAC_resolution = 12
ADC_resolution = 12

# Number of codes for the ADC and DAC
DAC_max_steps = 2**DAC_resolution
ADC_max_steps = 2**ADC_resolution

# Current measurement ranges are defined by the 
#  sense resistor value (* the gain of the sense amplifier) = Rsns * 10
#  and the input range of the ADC = 4096 mV

# List of the current sense resistors
Rsns_list = [80000, 800, 8] # [Ohm]
print('Rsns list:', Rsns_list, 'Ohm')

# Conversion factor (transimpedance gain) from current to voltage
ADCgain_list = [10 * Rsns for Rsns in Rsns_list] 
print('ADC gain list:', ADCgain_list, 'V/A')

# Resulting current measurement ranges
Imax_list = [ADC_range / gain for gain in ADCgain_list] # [mA]
print('Imax list:', Imax_list, 'mA')

# Minimum current measurable in each range
Imin_list = [0, Imax_list[0], Imax_list[1]] # [mA]
print('Imin list:', Imin_list, 'mA')

# Current value equivalent to one ADC code (LSB, least significant bit) 
Ilsb_list = [Imax/ADC_max_steps for Imax in Imax_list] # [mA]
print('Ilsb list:', Ilsb_list, 'mA')

# Voltage value equivalent to one DAC code (LSB, least significant bit) 
Vlsb = DAC_range/DAC_max_steps # [mV]
print('Vlsb:', Vlsb, 'mV')

 # Current sensing ADC error in mA (quantization noise = Ilsb/sqrt(12))
Ierror_list = [i/np.sqrt(12) for i in Ilsb_list] 

 # plot settings
Irange_list = ["low range", "mid range", "high range"]
color_list  = ['r', 'g','b']
marker_list = ['.', 'x','+']

# voltage scanning range DAC voltage = DAC_range * DAC_code/4096
voltage_steps_array = np.arange(0, DAC_range, Vlsb)
max_voltage         = voltage_steps_array[-1]
ADC_steps_array     = np.arange(ADC_max_steps)

# list of load resistors [Ohm] for I-V curve plotting 


# start with simple plots for a constant current measurement range
Resistor_list = [200, 1000, 5000]
Rsns = 1000
Imax = ADC_range / Rsns 
Ilsb = Imax / ADC_max_steps
fig1, ax = plt.subplots()

for Rload, marker in zip(Resistor_list, marker_list):
  
  # calculate the current as a function of the applied voltage
  current_array  = voltage_steps_array / Rload 

  # calculate the ADC code for the current values
  ADC_steps_array = np.array(current_array / Ilsb).astype(int)

  # calculate the current values from the ADC codes
  sampled_current_array = ADC_steps_array * Ilsb

  # limit the points to the current measurement range
  limited_range = np.where(np.logical_and(sampled_current_array <= Imax, sampled_current_array >= 0))

  Vrange_plot = voltage_steps_array[limited_range]
  Irange_plot = sampled_current_array[limited_range]

  ax.step(Vrange_plot, Irange_plot, where='mid', label= str(Rload) + ' Ohm')

ax.set_title('Resistor I-V curves for fixed current range')
ax.set_xlim(0, 4096)
ax.set_ylim(0, Imax)
ax.set(xlabel='Voltage [mV]', ylabel='Current [mA]')
ax.legend(loc='upper left')


# plot the I-V curves for a list of load resistors using the three current measurement ranges
Resistor_list = [4000]
fig2, bx = plt.subplots(1,2)

for Rload, marker in zip(Resistor_list, marker_list):
  for current_range in range(3):

    # calculate the current as a function of the applied voltage
    current_array  = voltage_steps_array / Rload 

    # calculate the ADC code for the current values
    ADC_steps_array = np.array(current_array / Ilsb_list[current_range]).astype(int)

    # calculate the current values from the ADC codes
    sampled_current_array = ADC_steps_array * Ilsb_list[current_range]

    # limit the points to the current measurement range
    limited_range = np.where(np.logical_and(sampled_current_array <= Imax_list[current_range], sampled_current_array >= Imin_list[current_range]))

    Vrange_plot = voltage_steps_array[limited_range]
    Irange_plot = sampled_current_array[limited_range]

    bx[0].step(Vrange_plot, Irange_plot, '.--', where='mid', label= str(Rload) + ' Ohm')
    bx[1].step(Vrange_plot, Irange_plot, '.--', where='mid')
    #ax[0].plot(Vrange_plot, Irange_plot, '.k', label= str(R) + ' Ohm')
    #ax[0].fill_between(Vrange_plot, Irange_plot-Ierror_list[i] * 100, Irange_plot+Ierror_list[i] * 100, color='gray')

fig2.suptitle('I-V curves for various current measurement ranges')

bx[0].set_title('Linear plot')
bx[0].axhspan(0,            Imax_list[0] , color='r', alpha=0.1, label='low range')
bx[0].axhspan(Imax_list[0], Imax_list[1] , color='g', alpha=0.1, label='mid range')
bx[0].axhspan(Imax_list[1], Imax_list[2] , color='b', alpha=0.1, label='high range')
bx[0].set_xlim(0, 4096)
bx[0].set_ylim(0, 1.5)

bx[0].set(xlabel='Voltage [mV]', ylabel='Current [mA]')
bx[0].legend(loc='upper left')

bx[1].set_title('Logarithmic plot')
bx[1].axhspan(0,            Imax_list[0] , color='r', alpha=0.1, label='low range')
bx[1].axhspan(Imax_list[0], Imax_list[1] , color='g', alpha=0.1, label='mid range')
bx[1].axhspan(Imax_list[1], Imax_list[2] , color='b', alpha=0.1, label='high range')

bx[1].set(xlabel='Voltage [mV]', ylabel='Current [mA]')
#ax[1].set_ylim(1e-6, 100)
bx[1].set_xlim(1, 4096)
bx[1].set_xscale('log')
bx[1].set_yscale('log')
bx[1].legend(loc='upper left')

# nLogRes  = np.logspace(0, 8, num=1000)

# # plot the number of non-redundant I-V pairs for the three current measurement ranges
# for Igain, Iname, color in zip(Ilsb_list, Irange_list, color_list):
#   nBins = []
#   Imax = 4096 * Igain
#   for R in nLogRes:
#     Vlim = Imax * R    # voltage limit given by maximum current
#     Ilim = DAC_max_voltage / R    # current limit given by maximum voltage
#     if (Vlim < DAC_max_voltage):  # DAC limited
#       bin = Vlim
#     else:
#       bin = Ilim/Igain  # ADC limited
#     nBins.append(bin)
#   ax[1].plot(nLogRes, nBins, color, label=Iname)


# ax[1].set(xlabel='Resistance [Ohm]', ylabel='# Bins', title='Bin Count')
# ax[1].set_xscale('log')
# ax[1].legend()

#fig.savefig("test.png")
plt.show()
