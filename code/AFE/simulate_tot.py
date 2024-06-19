import numpy as np
#from scipy.optimize import curve_fit
import csv
import matplotlib.pyplot as plt

def sha_pulse_func(t, t0, tau, a, b):
  return np.where(t > t0, a * np.exp(1) * (t-t0)/tau * np.exp(-(t-t0)/tau) + b, b)

def sha_pulse2_func(t, t0, tau1, tau2, a, b):   
  return np.where(t > t0, a * np.exp(1) * tau2/(tau1-tau2) * (np.exp(-(t-t0)/tau1) - np.exp(-(t-t0)/tau2)) + b, b)

def plot_shaper_pulse(time_range, amplitude, tau):
  label_text = 'tau=%.1f, a=%.1f' % (tau, amplitude)
  ax.plot(time_range, sha_pulse_func(time_range, 0, tau, amplitude, 0), label=label_text)
  ax.set(xlabel='Time [us]', ylabel='Voltage [mV]', title='SHA pulse')
  ax.legend()

def plot_tot_pulse(time_range, amplitude, tau, threshold):
  tot_data = np.where(sha_pulse_func(time_range, 0, tau, amplitude, 0) > threshold, 1, 0)
  diff_tot_data = np.diff(tot_data) # find the transition points
  tot_transition = np.where(diff_tot_data != 0)[0] # get indices of transition points
  if (len(tot_transition) < 2):
    tot_width=0  # no transitions found, amplitude below threshold
  else:
    tot_width = time_range[tot_transition[1]] - time_range[tot_transition[0]] # calculate the width of the pulse
  label_text = 'threshold=%.1f, tot width=%.1f µs' % (threshold, tot_width)
  ax.plot(time_range, tot_data, label=label_text)
  ax.set(xlabel='Time [us]', ylabel='Voltage [mV]', title='TOT pulse')
  ax.legend()

def tot_scan(time_range, amplitude_range, tau, threshold, do_plot=False):
  tot_width_array = np.empty(0, dtype=float)
  for amplitude in amplitude_range:
    tot_data = np.where(sha_pulse_func(time_range, 0, tau, amplitude, 0) > threshold, 1, 0)
    diff_tot_data = np.diff(tot_data)
    tot_transition = np.where(diff_tot_data != 0)[0]
    if (len(tot_transition) < 2):
      tot_width=0
    else:
      tot_width = time_range[tot_transition[1]] - time_range[tot_transition[0]] 
    tot_width_array = np.append(tot_width_array, tot_width)
  if (do_plot):
    label_text = 'tau=%d, threshold=%.1f' % (tau, threshold)
    ax.plot(amplitude_range, tot_width_array, label=label_text)
    ax.set(xlabel='Amplitude', ylabel='TOT [µs]', title='TOT scan')
    ax.legend()
  return tot_width_array

def parametric_tot_scan(time_range, amplitude_range, tau_range, threshold):
  tot_width_array = np.empty(0, dtype=float)
  for tau in tau_range:
    tot_width_array = tot_scan(time_range, amplitude_range, tau, threshold, False)
    label_text = 'tau=%.1f, threshold=%.1f' % (tau, threshold)
    ax.plot(amplitude_range, tot_width_array, label=label_text)
  ax.set(xlabel='Amplitude', ylabel='TOT [µs]', title='TOT scan')
  ax.legend()

  return tot_width_array


time_range = np.linspace(0, 100, 10000) 
amplitude_range = np.linspace(0, 2, 100)
tau_range = [0.2, 0.5, 1, 2, 5]
threshold = 1
fig, ax = plt.subplots()
#plot_shaper_pulse(time_range, 1, 1)
#plot_tot_pulse(time_range, 1, 1, threshold)
#tot_scan(time_range, amplitude_range, 1, threshold)
parametric_tot_scan(time_range, amplitude_range, tau_range, threshold)
  
plt.show()