import numpy as np
from scipy.optimize import curve_fit
import csv
import matplotlib.pyplot as plt

def sha_pulse_func(t, t0, tau, a, b):
  return np.where(t > t0, a * np.exp(1) * (t-t0)/tau * np.exp(-(t-t0)/tau) + b, b)

def sha_pulse2_func(t, t0, tau1, tau2, a, b):
  return np.where(t > t0, a * np.exp(1) * tau2/(tau1-tau2) * (np.exp(-(t-t0)/tau1) - np.exp(-(t-t0)/tau2)) + b, b)

def analyze_waveform(filename):
  with open(filename, 'r') as file:
    reader = csv.reader(file)
    data = list(reader)
    data = np.array(data[:1000]).astype(float)
    
    popt, pcov = curve_fit(sha_pulse_func, data[:,0], data[:,1], bounds=([50, 1, 200, 900], [80, 25, 1500, 1100])) 
 #   popt, pcov = curve_fit(sha_pulse2_func, data[:,0], data[:,1], bounds=([60, 2, 1, 200, 900], [65, 25, 25, 1500, 1100])) 
    label_text = 't0=%.1f, tau=%.1f, a=%.1f, b=%.1f' % (popt[0], popt[1], popt[2], popt[3])
 #   label_text = 't0=%.1f, tau1=%.1f, tau2=%.1f, a=%.1f, b=%.1f' % (popt[0], popt[1], popt[2], popt[3], popt[4])

    fig, ax = plt.subplots()
    ax.plot(data[:,0], data[:,1])
    ax.plot(data[:,0], sha_pulse_func(data[:,0], *popt), label=label_text)
 #   ax.plot(data[:,0], sha_pulse_func2(data[:,0], *popt), label=label_text)
    ax.set(xlabel='Time [us]', ylabel='Voltage [mV]', title='SHA pulse')
    ax.legend()
    plt.show()

analyze_waveform('code/AFE/test.csv')