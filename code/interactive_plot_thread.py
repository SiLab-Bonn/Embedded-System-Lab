import matplotlib.pyplot as plt
import numpy as np
from threading import Thread
from queue import Queue
import time

key = ''

# Data for plotting
t0  = 0
t   = np.arange(0.0, 2.0, 0.01)
s   = 1 + np.sin(2 * np.pi * t)
f   = 1

plt.ion()     # intercative mode
fig, ax = plt.subplots()
myplot, = ax.plot(t, s)

# plotting will run in a separate thread
def updatePlot(queue):
  global f, t0, t, myplot
  while True:
    t0 = t0 + 0.1/f
    if not queue.empty():
      data = queue.get()
      if data.isnumeric():
        f = int(data)
    s = 1 + np.sin(2 * np.pi * f * (t + t0))
    myplot.set_ydata(s)    
    time.sleep(0.1)

# add queue to pass data between main and plotting thread
queue = Queue()

# instantiate plotting thread and start it, set the 'daemon flag' to automatically kill the thread when the main thread stops
plotThread = Thread(target=updatePlot, args =(queue,), daemon = True)
plotThread.start()

# prepare plot window
ax.set(xlabel='time (s)', ylabel='voltage (mV)', title='Intercative Plot')
ax.grid()
plt.show()

# main thread
while True:
  print('Enter frequency value or press \'q\' to stop')
  key = input()  
  if key == 'q':
    break
  queue.put(key)


# add any clean-up code here
print("Program stopped")
  

