import spidev
import time
import os
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

TRG = 4
GPIO.setup(TRG, GPIO.OUT)

# os.system("sudo raspi-config nonint do_spi 1")
# os.system("sudo raspi-config nonint do_spi 0")

spi = spidev.SpiDev()
spi.open(0,0)  # (bus, device)
spi.max_speed_hz = 50000
spi.mode = 0

spi_byte = 0x00

while (input() != 'q'):
  print("SPI data 0x%02x" % spi_byte)
  GPIO.output(TRG, GPIO.HIGH)

  spi.xfer([0x33, spi_byte])
  
  GPIO.output(TRG, GPIO.LOW)

  spi_byte += 1

spi.close()
