from gpiozero import DistanceSensor
from time import sleep

US = DistanceSensor(echo=5, trigger=4, max_distance=4, queue_len=1)
while True:
    print("Distance: %0.2f cm" %(US.distance * 100))
    sleep(1)
