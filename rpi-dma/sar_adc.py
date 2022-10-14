import time
import RPi.GPIO as GPIO
import spidev as SPI

GPIO.setmode(GPIO.BCM)

spi = SPI.SpiDev()
spi.open(0,0)  # (bus, device)
spi.mode = 0
spi.max_speed_hz = 100000

dac_resolution = 8 # resolution in bits

SAMPLE = 4 # GPIO4
GPIO.setup(SAMPLE, GPIO.OUT)
GPIO.output(SAMPLE, GPIO.LOW)

COMP = 5  # GPIO5
GPIO.setup(COMP, GPIO.IN)

# trigger sample switch
GPIO.output(SAMPLE, GPIO.HIGH)
time.sleep(0.0001)
GPIO.output(SAMPLE, GPIO.LOW)

# reset dac value
dac_value = 0

# successive approximation loop, MSB to LSB
for dac_bit in reversed(range(dac_resolution)):
  #set DAC value
  dac_value |= 1 << (dac_bit) 
  spi.xfer([dac_value])

  # get result from comparator 
  result = GPIO.input(COMP)
  if not (result):
    dac_value -= 1 << (dac_bit)
  print(dac_bit, dac_value, result)
spi.xfer([dac_value])
    

print("dac_value", dac_value)




