#!/usr/bin/python3

import time
from gpiozero import *
from gpiozero.pins.pigpio import PiGPIOFactory # needs pigpio daemon (call "sudo pigpiod")

factory = PiGPIOFactory() # needed to HW PWM access

# servo PWM frequency
pwm_freq = 100
# servo pulse width range [sec]
min_pw = 0.00055#0.000545
max_pw = 0.0025#0.002350

# servo PWM duty cycle range
min_dc = min_pw * pwm_freq #0.05 
max_dc = max_pw * pwm_freq #0.1
# servo turn range
min_deg = 0
max_deg = 180

def get_dc_from_deg(deg):
    val = deg*(max_dc-min_dc)/(max_deg-min_deg)+min_dc
    #print(val)
    return (val)

servo = PWMOutputDevice(12, True, get_dc_from_deg(90), pwm_freq, pin_factory=factory)


##for deg in range(0, 180, 1):
##    servo.value = get_dc_from_deg(deg)
##    time.sleep(0.02)

A = 100#0
B = 220

while True:
    servo.value = get_dc_from_deg(A)
    time.sleep(0.2)    
    servo.value = get_dc_from_deg(B)
    time.sleep(0.2)    
  

##while True:
##    for deg in range(0, 180, 1):
##        servo.value = get_dc_from_deg(deg)
##        time.sleep(0.001)
##
##    for deg in range(180, 0, -1):
##        servo.value = get_dc_from_deg(deg)
##        time.sleep(0.005)


