import spidev
import time

spi = spidev.SpiDev()
spi.open(0,0)  # (bus, device)
spi.mode = 0
spi.max_speed_hz = 7800

data_array = []
#data_array = [42 for i in range(2)]

try:
    print("running...")
    while True:
        data_array = [0xf0, 0x00, 0x0f]
        spi.xfer(data_array)
        time.sleep(0.0000001)
        
except KeyboardInterrupt:   # Ctrl+C
    if spi != None:
        spi.close()
        print("closed.")
