import serial
import time

ser = serial.Serial('/dev/ttyS0', 115200)
#ser.open()
if ser.is_open == False:
  print("Could not open serial port.")
  exit()

ser.reset_input_buffer()
    
while True:    
  if (ser.inWaiting() > 0):
      data_str = ser.read(ser.inWaiting()).decode('ascii') 
      print("Received:", data_str)   
  
  key = input("Transmit: ").encode()
  ser.write(key)
  ser.flush()
