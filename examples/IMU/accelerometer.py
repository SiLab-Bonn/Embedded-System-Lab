#!/usr/bin/python
import sys
import time

from sense_hat import SenseHat

sense = SenseHat()
sense.set_imu_config(False, True, False)  # gyroscope only
sense.clear([0,0,0])

pitch_n = 0
roll_n  = 0
x = 3
y = 3

orientation = sense.get_orientation_degrees() # read offsets
pitch_ofs = 180#int(orientation["pitch"])
roll_ofs  = 180#int(orientation["roll"])



while 1:
    orientation = sense.get_orientation_degrees()
    #print("p: {pitch}, r: {roll}, y: {yaw}".format(**orientation))
    
    pitch =  (orientation["pitch"]+180)%360
    roll  =  (orientation["roll"] -180)%360
        
    d_pitch = pitch_n - pitch
    d_roll  = roll_n - roll
    pitch_n = pitch
    roll_n  = roll

    x = x + d_pitch
    y = y - d_roll
    
     
    if (x > 7):
        x = 4
    if (x < 0):
        x = 0
        
    if (y > 7):
        y = 7
    if (y < 0):
        y = 0       

    #print(x, y, d_pitch, d_roll)
    
    sense.clear([0,0,0])
    sense.set_pixel(int(x), int(y), 255, 255, 255)
   # time.sleep(0.1)