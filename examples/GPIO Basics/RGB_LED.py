import time
from gpiozero import *
from gpiozero.pins.pigpio import PiGPIOFactory # needs pigio daemon

LED_R = LED(22)
LED_G = LED(26)
LED_B = LED(27)
BTN = Button(4, pull_up=None, active_state=True)


try:
    while 1:
        LED_R.on()
        BTN.wait_for_press()
        BTN.wait_for_release()
        LED_R.off()
        LED_G.on()
        BTN.wait_for_press()
        BTN.wait_for_release()
        LED_G.off()
        LED_B.on()
        BTN.wait_for_press()
        BTN.wait_for_release()
        LED_B.off()
except KeyboardInterrupt:
    print ("bye")
    pass
