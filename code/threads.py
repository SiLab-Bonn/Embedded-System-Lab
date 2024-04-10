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


# this is the main thread 
while True:
  # do something with the key input
  print('Last key pressed:', key)

  # add code for scan loops here
  time.sleep(1)

  if key == 'q':
    print("Thread stopped")
    break 

print("Program stopped")
exit() 
