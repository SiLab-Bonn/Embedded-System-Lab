import gpiozero
import time

spi = gpiozero.SPIDevice()

data_array = []
data_array = [0 for i in range(64)]

try:
    print("running...")
    while True:
        spi._spi.transfer(data_array)
        #time.sleep(0.0000001)
        
except KeyboardInterrupt:   # Ctrl+C
    if spi != None:
        spi.close()
        print("closed.")
