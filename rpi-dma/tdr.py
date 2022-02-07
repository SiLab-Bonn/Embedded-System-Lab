import time
import RPi.GPIO as GPIO
import spidev as SPI
# GPIO.setmode(GPIO.BOARD) # RPi.GPIO Layout verwenden (wie Pin-Nummern)
GPIO.setmode(GPIO.BCM)

spi = SPI.SpiDev()
spi.open(0,0)  # (bus, device)
spi.mode = 0
spi.max_speed_hz = 10000000

dac_resolution = 12 # resolution in bits
delay_size = 1 # numer of delay steps

spi_array = bytearray(6)
dac_value   = 0
delay_value = 0
spi_array = [dac_value >> 8, dac_value & 0xff, delay_value >> 8, delay_value & 0xff]
 

TRIGGER = 4
GPIO.setup(TRIGGER, GPIO.OUT)
GPIO.output(TRIGGER, GPIO.LOW)

COMP = 5
GPIO.setup(COMP, GPIO.IN)

for t in range(delay_size):
  #set delay value
  delay_value = t
  spi_array = [dac_value >> 8, dac_value & 0xff, delay_value >> 8, delay_value & 0xff]
  spi.xfer(spi_array)
  #reset dac output 
  dac_value = 0

  for dac_bit in reversed(range(dac_resolution)):
    #set DAC value
    dac_value |= 1 << (dac_bit)
    spi_array = [dac_value >> 8, dac_value & 0xff, delay_value >> 8, delay_value & 0xff]
    spi.xfer(spi_array)

    # trigger pulse step
    GPIO.output(TRIGGER, GPIO.HIGH)
    GPIO.output(TRIGGER, GPIO.LOW)

    result = 253 >= dac_value #GPIO.input(COMP)
    print(dac_bit, dac_value, result)
    if not result:
      dac_value -= 1 << (dac_bit)
print("dac_value", dac_value)




