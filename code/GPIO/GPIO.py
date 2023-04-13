import time
import sys

# import the library and define the prefix for using its members
import RPi.GPIO as GPIO

# tell the library to use pin numbers according to the GPIO naming
GPIO.setmode(GPIO.BCM) 

# define GPIO4 as an output
GPIO.setup(4, GPIO.OUT)

# toggle th output state
GPIO.output(4, GPIO.LOW)
GPIO.output(4, GPIO.HIGH)
GPIO.output(4, GPIO.LOW)

# set GPIO configuration back to default
GPIO.cleanup()
