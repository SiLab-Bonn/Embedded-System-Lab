import serial
import RPi.GPIO as GPIO
import time
import serial.tools.list_ports


TRG = 4
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM) # use pin numbers according to the GPIO naming
GPIO.setup(TRG, GPIO.OUT)

ports = serial.tools.list_ports.comports()
for port, desc, hwid in sorted(ports): # search device
  print("{}: {} [{}]".format(port, desc, hwid))

#ser = serial.Serial('/dev/ttyAMA0', baudrate=9600)
#ser = serial.Serial('serial0', baudrate=9600)
# if ser.is_open == False:
#   print("Could not open serial port.")
#   exit()

# ser.reset_input_buffer()
    
# while True:    

#   if (ser.in_waiting()):
#     response = ser.readline().decode().strip()
#     print("Received:", response)   
  
#   key = input("Transmit: ").encode()
#   GPIO.output(TRG, GPIO.HIGH)
#   ser.write(key)
#   GPIO.output(TRG, GPIO.LOW)
#   ser.flush()
#   ser.close()
