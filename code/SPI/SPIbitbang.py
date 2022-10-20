import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

SCK = 11
GPIO.setup(SCK, GPIO.OUT)
GPIO.output(SCK, GPIO.LOW)
SDO = 10
GPIO.setup(SDO, GPIO.OUT)
GPIO.output(SDO, GPIO.LOW)
CS0_B = 8
GPIO.setup(CS0_B, GPIO.OUT)
GPIO.output(CS0_B, GPIO.HIGH)

def spixfer(data, num_bits):
  GPIO.output(CS0_B, GPIO.LOW)
  for i in reversed(range(num_bits)):
    GPIO.output(SDO, 0x01 & (data >> i))
    GPIO.output(SCK, GPIO.HIGH)
    GPIO.output(SCK, GPIO.LOW)
  GPIO.output(CS0_B, GPIO.HIGH)

spixfer(0x35, 8)  