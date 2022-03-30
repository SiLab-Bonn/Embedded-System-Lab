#!/usr/bin/python3
from time import sleep
from gpiozero import *
from gpiozero.pins.pigpio import PiGPIOFactory # needs pigio daemon

factory = PiGPIOFactory() # needed to HW PWM access

f_pwm = 50
pw = 1350/1000000
A_pw = 400/1000000
B_pw = 2300/1000000

duty_c = pw * f_pwm

PWM = PWMOutputDevice(12, True, duty_c, f_pwm, pin_factory=factory)

try:

    while True:
        PWM.value = A_pw * f_pwm
        sleep(2)
        PWM.value = B_pw * f_pwm
        sleep(2)
except KeyboardInterrupt:   # Ctrl+C
    PWM.value = 1350/1000000 * f_pwm
