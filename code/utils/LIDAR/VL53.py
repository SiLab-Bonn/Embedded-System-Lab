import os
import time
import sys
import signal
import VL53L1X

tof = VL53L1X.VL53L1X(i2c_bus=1, i2c_address=0x29)
tof.open() # Initialise the i2c bus and configure the sensor
tof.start_ranging(2) # Start ranging, 1 = Short Range, 2 = Medium Range, 3 = Long Range
distance_in_mm = tof.get_distance() # Grab the range in mm

while True:
    print("Distance: %0.2f cm" %(tof.get_distance() / 10))
    #time.sleep(1)


tof.stop_ranging() # Stop ranging
