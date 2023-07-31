import matplotlib
import matplotlib.pyplot as plt
import numpy as np

# Data for plotting
Igain_list  = [ 0.00000125, 0.000125, 0.0125]
Ierror_list = [i/np.sqrt(12) for i in Igain_list]
Imax_list   = [i * 4096 for i in Igain_list]
Imin_list   = [0, Imax_list[0], Imax_list[1]]
Irange_list = ["low range", "mid range", "high range"]
color_list  = ['r', 'g','b']
marker_list = ['.', 'x','+']
Vrange      = np.arange(4096)
Vgain = 1
Vmax = 4096 * Vgain
nLogRes  = np.logspace(0, 8, num=1000)
nRes = [10, 1000, 100000]

fig, ax = plt.subplots(1,2)

for Igain, Iname, color in zip(Igain_list, Irange_list, color_list):
  nBins = []
  Imax = 4096 * Igain
  for R in nLogRes:
    Vlim = Imax * R    # voltage limit given by maximum current
    Ilim = Vmax / R    # current limit given by maximum voltage
    if (Vlim < Vmax):  # DAC limited
      bin = Vlim / Vgain
    else:
      bin = Ilim/Igain  # ADC limited
    nBins.append(bin)
  ax[1].plot(nLogRes, nBins, color, label=Iname)

R = 1000

for R, marker in zip(nRes, marker_list):
  for i in range(3):
    Ivalues = Vrange / R 
    limited_range = np.where(np.logical_and(Ivalues < Imax_list[i], Ivalues > Imin_list[i]))
    Vrange_plot = Vrange[limited_range]
    Irange_plot = Ivalues[limited_range]
    ax[0].plot(Vrange_plot, Irange_plot, '.k')
    ax[0].fill_between(Vrange_plot, Irange_plot-Ierror_list[i] * 100, Irange_plot+Ierror_list[i] * 100, color='gray')

ax[0].axhspan(0,            Imax_list[0] , color='r', alpha=0.1)
ax[0].axhspan(Imax_list[0], Imax_list[1] , color='g', alpha=0.1)
ax[0].axhspan(Imax_list[1], Imax_list[2] , color='b', alpha=0.1)
  #ax[0].set_label(Iname)


ax[0].set(xlabel='Voltage [mV]', ylabel='Current [mA]', title='Measurement Ranges')
ax[0].set_xscale('log')
ax[0].set_yscale('log')
#ax[0].legend()

ax[1].set(xlabel='Resistance [Ohm]', ylabel='# Bins', title='Bin Count')
ax[1].set_xscale('log')
ax[1].legend()

fig.savefig("test.png")
plt.show()
