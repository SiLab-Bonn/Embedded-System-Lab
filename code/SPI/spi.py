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
  print("Sending data", spi_byte)
  GPIO.output(TRG, GPIO.HIGH)
  #time.sleep(0.01)
  spi.xfer([spi_byte])
  GPIO.output(TRG, GPIO.LOW)
  time.sleep(0.1)
  spi_byte += 1

spi.close()
