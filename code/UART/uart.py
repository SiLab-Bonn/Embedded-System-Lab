import serial
import RPi.GPIO as GPIO
import time
import serial.tools.list_ports

# ports = serial.tools.list_ports.comports()
# for port, desc, hwid in sorted(ports): # search device
#   print("{}: {} [{}]".format(port, desc, hwid))

ser = serial.Serial('/dev/ttyS0', baudrate=9600)
if ser.is_open == False:
  print("Could not open serial port.")
  exit()

    
while True:    
  key = input("Transmit: ")
  ser.write(key.encode())
  ser.flush()

  response = ser.read(ser.in_waiting).decode().strip()
  print("Received:", response)   

ser.close()
