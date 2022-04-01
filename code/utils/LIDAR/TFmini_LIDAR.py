#!/usr/bin/python3

import time
import sys
import pygame
from math import cos, sin, pi, floor, ceil


from gpiozero import *
from gpiozero.pins.pigpio import PiGPIOFactory # needs pigpio daemon (call "sudo pigpiod")
factory = PiGPIOFactory() # needed to HW PWM access
import serial

tf_mini = serial.Serial('/dev/ttyS0', 115200)

# servo PWM frequency
pwm_freq = 100
# servo pulse width range [sec]
min_pw = 0.00075
max_pw = 0.00225

# servo PWM duty cycle range
min_dc = min_pw * pwm_freq #0.05 
max_dc = max_pw * pwm_freq #0.1
# servo turn range
min_angle = 0
max_angle = 180

# scan range
min_scan_angle = 10
max_scan_angle = 170

scan_data = [[0 for i in range(2)] for j in range(max_scan_angle)]

# Set up pygame and the display
pygame.init()
lcd = pygame.display.set_mode((800,800))
pygame.mouse.set_visible(False)
lcd.fill((0,0,0))
pygame.display.update()
# used to scale data to fit on the screen
max_distance = 0

def get_dc_from_deg(deg):
    return (deg*(max_dc-min_dc)/(max_angle-min_angle)+min_dc)

servo = PWMOutputDevice(12, True, get_dc_from_deg(90), pwm_freq, pin_factory=factory)


def getTFminiData(deg):
    tf_mini.reset_input_buffer()
    distance = 30
    strength = 1
    count = tf_mini.in_waiting
    while (count < 8):
#        time.sleep(0.1)
        count = tf_mini.in_waiting
    recv = tf_mini.read(9)  
    tf_mini.reset_input_buffer()  
    if recv[0] == 0x59 and recv[1] == 0x59:     
        distance = recv[2] + recv[3] * 256
        strength = recv[4] + recv[5] * 256
        #buf = ('(angle: %d°, distance: %d cm, ss: %d a.u.)' %(deg, distance, strength))
        #print(buf)
    if distance is None:
        distance = 30
    if strength is None:
        strength = 1
    return distance, strength

def process_data(data):
    global max_distance
    lcd.fill((0,0,0))
    for angle in range(min_scan_angle, max_scan_angle):
        strength = data[angle][1]
        distance = data[angle][0]
        max_distance = 0
        #print(data[angle])
#        if ((distance != None) and (strength != None)):                  # ignore initially ungathered data points
        if True:
            max_distance = 700#max([distance, max_distance])
            #print(distance, max_distance)
            radians = angle * pi / 180.0
            x = distance * cos(radians)
            y = distance * sin(radians)
            point = (400 + int(x / max_distance * 799), 700 - int(y / max_distance * 799))
            #lcd.set_at(point, pygame.Color(ceil(strength /8), 255, 255, 255))
            pygame.draw.circle(lcd, pygame.Color(255, 255, 255, 255), point, ceil(strength/64), 1) 
    pygame.display.update()


try:
    if tf_mini.is_open == False:
        tf_mini.open()
    while True:    
        for deg in range(min_scan_angle, max_scan_angle, 1):
            servo.value = get_dc_from_deg(deg)
            time.sleep(0.01)            
            scan_data[deg]=getTFminiData(deg)
        process_data(scan_data)
        time.sleep(0.1)
##        for deg in range(max_scan_angle-1, min_scan_angle+1, -1):
##            servo.value = get_dc_from_deg(deg)
##            time.sleep(0.01)            
##            scan_data[deg]=getTFminiData(deg)
##        process_data(scan_data)    

except KeyboardInterrupt:   # Ctrl+C
    if tf_mini != None:
        tf_mini.close()
        pygame.display.quit()
        pygame.quit()
