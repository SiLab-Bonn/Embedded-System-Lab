import serial
import RPi.GPIO as GPIO
import time
import serial.tools.list_ports


TRG = 4
RX = 15
TX = 14
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM) # use pin numbers according to the GPIO naming
GPIO.setup(TRG, GPIO.OUT)
GPIO.setup(RX, GPIO.MODE_ALT5)
GPIO.setup(TX, GPIO.ALT5)

# ports = serial.tools.list_ports.comports()
# for port, desc, hwid in sorted(ports): # search device
#   print("{}: {} [{}]".format(port, desc, hwid))

ser = serial.Serial('/dev/ttyS0', baudrate=9600)
if ser.is_open == False:
  print("Could not open serial port.")
  exit()

ser.reset_input_buffer()
    
while True:    
  key = input("Transmit: ")
  GPIO.output(TRG, GPIO.HIGH)
  ser.write(key.encode())
  GPIO.output(TRG, GPIO.LOW)

  time.sleep(1)
  while (ser.in_waiting):
    response = ser.readline().decode().strip()
    print("Received:", response)   

ser.close()
