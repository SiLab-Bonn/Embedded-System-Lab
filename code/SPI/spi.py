import spidev
import time

spi = spidev.SpiDev()
spi.open(0,0)  # (bus, device)
spi.mode = 0
spi.max_speed_hz = 1000000

data_byte = 44

spi.xfer([data_byte])
        
