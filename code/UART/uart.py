import serial
import time

ser = serial.Serial('/dev/ttyS0', 115200)
ser.open()
if ser.is_open == False:
     print("Could not open serial port.")
     exit()

ser.reset_input_buffer()
        
while True:    
  if ser.in_waiting > 1:
    print(ser.readall())

except KeyboardInterrupt:   # Ctrl+C

if ser != None:
  ser.close()
