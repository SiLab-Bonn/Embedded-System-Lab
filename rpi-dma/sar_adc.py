import time
import RPi.GPIO as GPIO
import spidev as SPI
import matplotlib.pyplot as plt
import numpy as np

GPIO.setmode(GPIO.BCM)

spi = SPI.SpiDev()
spi.open(0,0)  # (bus, device)
spi.mode = 0
spi.max_speed_hz = 100000

dac_resolution = 8 # resolution in bits

SAMPLE = 4 # GPIO4
GPIO.setwarnings(False)
GPIO.setup(SAMPLE, GPIO.OUT)
GPIO.output(SAMPLE, GPIO.LOW)

COMP = 5  # GPIO5
GPIO.setup(COMP, GPIO.IN)

adc_data = np.array([])

for i in range(100000):
  # trigger sample switch
  GPIO.output(SAMPLE, GPIO.HIGH)
  time.sleep(0.0001)
  GPIO.output(SAMPLE, GPIO.LOW)

  # reset dac value
  dac_value = 0

  # succesive approximation loop from bit 7 (MSB) down to bit 0 (LSB)
  for dac_bit in reversed(range(dac_resolution)):
    # set next DAC bit value
    dac_value |= 1 << (dac_bit) 
    # write DAC value 
    spi.xfer([dac_value])

    # get result from comparator 
    result = GPIO.input(COMP)
    if not (result): # input voltage is lower than DAC voltage
      dac_value -= 1 << (dac_bit)  # substract DAC bit value
    #print(dac_bit, dac_value, result)

  spi.xfer([dac_value]) # write final DAC value with correct LSB
  adc_data = np.append(adc_data, [dac_value])
  #time.sleep(0.1)

#print(adc_data)

plt.hist(adc_data, bins = range(0, 256, 1))
plt.show()

#print("dac_value", dac_value)




