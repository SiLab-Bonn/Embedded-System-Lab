#!/usr/bin/python3

import time
from gpiozero import *

speed_of_sound = 34300 # [cm/s]

echo    = DigitalInputDevice(13)
trigger = DigitalOutputDevice(12)

while 1:
    # trigger measurement
    trigger.on()
    time.sleep(0.00001)
    trigger.off()

    # wait for echo pulse and get pulse width
    while not echo.wait_for_active():
        pass
    start_time = time.perf_counter()
    
    while not echo.wait_for_inactive():
        pass
    stop_time = time.perf_counter()
    
    # calculate distance
    distance = (stop_time - start_time)/2 * speed_of_sound

    print("distance: %0.2f cm" %distance)

    time.sleep(1)



