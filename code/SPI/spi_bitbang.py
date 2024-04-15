import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# SPI clock
SCK = 11
GPIO.setup(SCK, GPIO.OUT)
GPIO.output(SCK, GPIO.LOW)

# data from master to slave
MOSI = 10
GPIO.setup(MOSI, GPIO.OUT)
GPIO.output(MOSI, GPIO.LOW)

# chip select, active low
CS0_B = 8
GPIO.setup(CS0_B, GPIO.OUT)
GPIO.output(CS0_B, GPIO.HIGH)


data_byte = 0xff

# start transfer be pulling chip select low
GPIO.output(CS0_B, GPIO.LOW)

# serialize the data byte and shift out 
for i in range(8):
  GPIO.output(MOSI, 0x01 & (data_byte >> (7 - i)))
  GPIO.output(SCK, GPIO.HIGH)
  GPIO.output(SCK, GPIO.LOW)

# pull chip select high to end the transfer 
GPIO.output(CS0_B, GPIO.HIGH)

GPIO.cleanup()
