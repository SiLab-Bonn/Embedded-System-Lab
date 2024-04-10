import matplotlib.pyplot as plt
import numpy as np

# Data for plotting
t0 = 0
t  = np.arange(0.0, 2.0, 0.01)
s  = 1 + np.sin(2 * np.pi * t)

plt.ion()     # intercative mode
fig, ax = plt.subplots()
myplot, = ax.plot(t, s)

ax.set(xlabel='time (s)', ylabel='voltage (mV)', title='Intercative Plot')
ax.grid()

plt.show()

print("Press enter to update (q to exit)")
while True:
  if (input() == 'q'):
    break
  s = 1 + np.sin(2 * np.pi * (t + t0))
  myplot.set_ydata(s)    
  t0 = t0 + 0.1
