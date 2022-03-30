import time
import sys
import RPi.GPIO as GPIO

# GPIO.setmode(GPIO.BOARD) # RPi.GPIO Layout verwenden (wie Pin-Nummern)
GPIO.setmode(GPIO.BCM)

#GPIO.setup(12, GPIO.OUT)
#pwm12 = GPIO.PWM(12, 5000)  # set up PWM mode (software PWM!!!)
#pwm12.start(50)


GPIO.setup(4, GPIO.OUT)

GPIO.output(4, GPIO.LOW)
time.sleep(0.0010)
GPIO.output(4, GPIO.HIGH)
time.sleep(0.001)
GPIO.output(4, GPIO.LOW)
GPIO.cleanup()
