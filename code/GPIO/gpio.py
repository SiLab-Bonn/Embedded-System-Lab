# import the library and define the prefix for using its members
import RPi.GPIO as GPIO

# tell the library to use pin numbers according to the GPIO naming
GPIO.setmode(GPIO.BCM)

# define GPIO27 as an output
GPIO.setup(27, GPIO.OUT)

# set the output to high
GPIO.output(27, GPIO.HIGH)

# wait for user input
input()

# set the output to low
GPIO.output(27, GPIO.LOW)

# wait for user input
input()

# set GPIO configuration back to default
GPIO.cleanup()