import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM) 

LED_R = 25
LED_G = 26
LED_B = 27
BTN   = 4

GPIO.setup(LED_R, GPIO.OUT)
GPIO.setup(LED_G, GPIO.OUT)
GPIO.setup(LED_B, GPIO.OUT)
GPIO.setup(BTN,   GPIO.IN)

GPIO.output(LED_R, GPIO.LOW)
GPIO.output(LED_G, GPIO.LOW)
GPIO.output(LED_B, GPIO.LOW)

def wait_for_btn_press_and_release():
  while (GPIO.input(BTN) == True):   # pressed
    pass
  while (GPIO.input(BTN) == False):  # not pressed
    pass
  time.sleep(0.1)

try:
  while 1:
    GPIO.output(LED_R, GPIO.HIGH)
    wait_for_btn_press_and_release()
    GPIO.output(LED_R, GPIO.LOW)
    GPIO.output(LED_G, GPIO.HIGH)
    wait_for_btn_press_and_release()
    GPIO.output(LED_G, GPIO.LOW)
    GPIO.output(LED_B, GPIO.HIGH)
    wait_for_btn_press_and_release()
    GPIO.output(LED_B, GPIO.LOW)
except KeyboardInterrupt:
  print ("bye")
  GPIO.cleanup()
  pass
