import time
import sys

# import the library and define the prefix for using its members
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM) # use pin numbers according to the GPIO naming

# define GPIO pins for RGB LED control
RGB_LED_RED  = 26
RGB_LED_BLUE = 27

# define output pins for LED
GPIO.setup(RGB_LED_BLUE, GPIO.OUT)
GPIO.setup(RGB_LED_RED, GPIO.OUT)
GPIO.output(RGB_LED_BLUE, GPIO.LOW)
GPIO.output(RGB_LED_RED, GPIO.LOW)

# toggle the output states
GPIO.output(RGB_LED_BLUE, GPIO.HIGH)
time.sleep(1)
GPIO.output(RGB_LED_BLUE, GPIO.LOW)
GPIO.output(RGB_LED_RED, GPIO.HIGH)
time.sleep(1)
GPIO.output(RGB_LED_BLUE, GPIO.HIGH)
time.sleep(1)

GPIO.cleanup()#   set GPIO configuration back to default