import matplotlib.pyplot as plt
import numpy as np
import threading
import time

key = ''

 # this function will run in a separate thread and capture user input to control the loop in the main thread
def getInput():
  while True:
    print('Enter value or press ''q'' to stop')
    global key # use the global variable to communicate between threads (better: use queues)
    key = input()


# instantiate the thread and start it, set the 'daemon flag' to automatically kill the thread when the main thread stops
inputThread = threading.Thread(target=getInput)
inputThread.daemon = True  
inputThread.start()

# Data for plotting
t = np.arange(0.0, 2.0, 0.01)
s = 1 + np.sin(2 * np.pi * t)

plt.ion()     # intercative mode
fig, ax = plt.subplots()
myplot, = ax.plot(t, s)

ax.set(xlabel='time (s)', ylabel='voltage (mV)', title='Intercative Plot')
ax.grid()

# draw plot canvas once and update data later on in the loop
plt.show()

t0 = 0
f = 1

while True:
  # end the main loop 
  if (key == 'q'):
    break

  if key.isnumeric():
    f = int(key)
  s = 1 + np.sin(2 * np.pi * f * (t + t0))
  myplot.set_ydata(s)    
  t0 = t0 + 0.1
  plt.pause(0.1)

# add any clean-up code here
print("Program stopped")
  

