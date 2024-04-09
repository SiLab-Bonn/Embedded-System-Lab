import threading
import time

stop_thread = False
key = ''

def myThreadFunction():
  while not stop_thread:
    print("Thread Function working")
    print('last key pressed:', key)
    time.sleep(1)

my_thread = threading.Thread(target=myThreadFunction)
my_thread.start()

print('Press ''q'' to stop')

while True:
  key = input()
  if key == 'q':
    stop_thread = True
    my_thread.join() # Wait for the thread to finish	
    print("Thread stopped")
    exit()


