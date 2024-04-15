import spidev
import time
import os

# os.system("sudo raspi-config nonint do_spi 1")
# os.system("sudo raspi-config nonint do_spi 0")

spi = spidev.SpiDev()
spi.open(0,0)  # (bus, device)
spi.max_speed_hz = 1000000
spi.mode = 0


data_byte = 0x33

spi.xfer([data_byte])
        
spi.close()
