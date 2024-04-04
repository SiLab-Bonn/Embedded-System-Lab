import matplotlib
import matplotlib.pyplot as plt
import numpy as np

# Parameters for plotting the three current measurement ranges
 # current sensing ADC LSB size in mA for the three current mesurement ranges
Ilsb_list   = [ 0.00000125, 0.000125, 0.0125]     

 # current sensing ADC error in mA (quantization noise = Ilsb/sqrt(12))
Ierror_list = [i/np.sqrt(12) for i in Ilsb_list] 

 # maximum current in mA
Imax_list   = [Ilsb * 4096 for Ilsb in Ilsb_list]
Imin_list   = [0, Imax_list[0], Imax_list[1]]

 # plot settings
Irange_list = ["low range", "mid range", "high range"]
color_list  = ['r', 'g','b']
marker_list = ['.', 'x','+']

# voltage scanning range (12 bit DAC), DAC voltage = 4096 mV * DAC_code/4096
DAC_voltage_range  = np.arange(4096)
DAC_max_voltage    = DAC_voltage_range[-1]
nLogRes  = np.logspace(0, 8, num=1000)
ADC_code_array     = np.arange(4096)

# list of test resistors [Ohm] for I-V curve plotting 
#Resistor_list = [10, 1000, 100000]
Resistor_list = [4000]

fig, ax = plt.subplots(1,2)


# plot the I-V curves and ascociated errors for the three current measurement ranges
for R, marker in zip(Resistor_list, marker_list):
  for i in range(3):
    current_array  = DAC_voltage_range / R 
    ADC_code_array = np.array(current_array / Ilsb_list[i]).astype(int)
    sampled_current_array = ADC_code_array * Ilsb_list[i]
    limited_range = np.where(np.logical_and(sampled_current_array < Imax_list[i], sampled_current_array > Imin_list[i]))
    Vrange_plot = DAC_voltage_range[limited_range]
    Irange_plot = sampled_current_array[limited_range]
    ax[0].step(Vrange_plot, Irange_plot, where='pre', label= str(R) + ' Ohm')
    ax[1].step(Vrange_plot, Irange_plot, where='pre')
#    ax[0].plot(Vrange_plot, Irange_plot, '.k', label= str(R) + ' Ohm')
    #ax[0].fill_between(Vrange_plot, Irange_plot-Ierror_list[i] * 100, Irange_plot+Ierror_list[i] * 100, color='gray')

ax[0].axhspan(0,            Imax_list[0] , color='r', alpha=0.1, label='low range')
ax[0].axhspan(Imax_list[0], Imax_list[1] , color='g', alpha=0.1, label='mid range')
ax[0].axhspan(Imax_list[1], Imax_list[2] , color='b', alpha=0.1, label='high range')
ax[0].set_ylim(0, 1.5)

ax[0].set(xlabel='Voltage [mV]', ylabel='Current [mA]')
ax[0].legend(loc='upper left')

ax[1].axhspan(0,            Imax_list[0] , color='r', alpha=0.1, label='low range')
ax[1].axhspan(Imax_list[0], Imax_list[1] , color='g', alpha=0.1, label='mid range')
ax[1].axhspan(Imax_list[1], Imax_list[2] , color='b', alpha=0.1, label='high range')

ax[1].set(xlabel='Voltage [mV]', ylabel='Current [mA]')
ax[1].set_xscale('log')
ax[1].set_yscale('log')
ax[1].legend(loc='upper left')


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

fig.savefig("test.png")
plt.show()
