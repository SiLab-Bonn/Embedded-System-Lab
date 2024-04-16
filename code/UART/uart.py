import serial
import RPi.GPIO as GPIO
import time
import serial.tools.list_ports


# TRG = 4

# GPIO.setwarnings(False)
# GPIO.setmode(GPIO.BCM) # use pin numbers according to the GPIO naming
# GPIO.setup(TRG, GPIO.OUT)


ports = serial.tools.list_ports.comports()
for port, desc, hwid in sorted(ports): # search device
  print("{}: {} [{}]".format(port, desc, hwid))

ser = serial.Serial('/dev/ttyS0', baudrate=9600)
if ser.is_open == False:
  print("Could not open serial port.")
  exit()

ser.write(b'0')

# ser.reset_input_buffer()
    
while True:    
  key = input("Transmit: ")
  #GPIO.output(TRG, GPIO.HIGH)
  ser.write(key.encode())
  ser.flush()
  #GPIO.output(TRG, GPIO.LOW)

  response = ser.read(ser.in_waiting).decode().strip()
  print("Received:", response)   

ser.close()
