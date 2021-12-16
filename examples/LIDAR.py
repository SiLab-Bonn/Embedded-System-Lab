#!/usr/bin/python3

import time 
import sys
import pygame
from math import cos, sin, pi, floor, ceil


from gpiozero import *
from gpiozero.pins.pigpio import PiGPIOFactory # needs pigpio daemon (call "sudo pigpiod")
factory = PiGPIOFactory() # needed to HW PWM access
import serial

ser = serial.Serial('/dev/ttyS0', 115200)

# servo PWM frequency defaults
pwm_freq = 50
pw_neutral = 1500
pw_offset_ccw = 24
pw_offset_cw = -30

# scan range
min_scan_angle = 120.0
max_scan_angle = 240.0
cw  = 0
ccw = 1

# Set up pygame and the display
pygame.init()
lcd = pygame.display.set_mode((800,800))
pygame.mouse.set_visible(False)
lcd.fill((0,0,0))
pygame.display.update()

# used to scale data to fit on the screen
max_distance = 0

servo = PWMOutputDevice(12, True, 1, pwm_freq, pin_factory=factory)

def calibrateServo():
    global pw_offset_ccw
    global pw_offset_cw
    pw_offset_ccw = 25
    pw_offset_cw = -25
    temp = 0
    setServoRotationSpeed(temp)
    time.sleep(0.5) 
    distance, strength, angle = getLidarData()
    while 1:
        temp -= 1
        setServoRotationSpeed(temp)
        #time.sleep(0.5) 
        distance, strength, new_angle = getLidarData()
        if (angle - new_angle) < -1:
            pw_offset_cw += temp
            break
    temp = 0
    setServoRotationSpeed(temp)
    time.sleep(0.5) 
    distance, strength, angle = getLidarData()
    while 1:
        temp += 1
        setServoRotationSpeed(temp)
        #time.sleep(0.5) 
        distance, strength, new_angle = getLidarData()
        if (angle - new_angle) > 1:
            pw_offset_ccw += temp
            break
    print("Calibration: pw_offset_ccw =", pw_offset_ccw, "pw_offset_cw =", pw_offset_cw)
    return

def setServoRotationAngle(angle):
    while 1:
        distance, strength, current_angle = getLidarData()
        #print(distance, strength, current_angle ) 
        delta = current_angle - angle
        speed = delta / 4
        if abs(delta) < 1:
            setServoRotationSpeed(0)
            #print("Rotation angle:", current_angle)
            break
        setServoRotationSpeed(speed)
    return

def setServoRotationSpeed(speed):
    if speed > 0:
        offset = pw_neutral + pw_offset_ccw
    if speed < 0:
        offset = pw_neutral + pw_offset_cw
    if speed == 0:
        offset = pw_neutral
    servo.value = ((speed+offset)/1000000 * pwm_freq)
    #servo.value = 1500/1000000


def getLidarData():
    ser.reset_input_buffer()
    while ser.in_waiting < 9:
        pass
    recv = ser.read(9)
    distance = None
    strength = None
    angle    = None
    mode = None
        
    if recv[0] == 0x08 and recv[1] == 0x15:     #python3
        distance = ((recv[2] << 8) + recv[3]) / 10 # cm
        strength = (recv[4] << 8) + recv[5]
        angle    = 90 + ((((recv[6] << 8) + recv[7]) - 120) / 3.4) # deg
        mode     = recv[8]
#        angle    = ((recv[6] << 8) + recv[7]) / 10 # deg
    if distance is None:
        distance = 0
    if strength is None:
        strength = 0
    if angle is None:
        angle = 0
   # print('distance:', distance, 'cm, ss:', strength,'au, angle:', angle, '°, mode', mode)
    return distance, strength, angle

def process_data(data, color):
    global max_distance
    #lcd.fill((0,0,0))
    for index in range(len(data)):
        distance = data[index][0] 
        strength = data[index][1]
        angle    = data[index][2]
        max_distance = 0
        #print(data[angle])
#        if ((distance != None) and (strength != None)):                  # ignore initially ungathered data points
        if True:
            max_distance = 800#max([distance, max_distance])
           # print(distance, max_distance)
#            radians = angle * pi / 180.0
            radians = (angle - 180) * pi / 180.0
            y = distance * cos(radians)
            x = - distance * sin(radians)
            point = (400 + int(x / max_distance * 799), 400 - int(y / max_distance * 799))
            #lcd.set_at(point, pygame.Color(color, color, color, 255))
            pygame.draw.circle(lcd, color, point, 2, 1) 
            
    pygame.display.update()


try:
    if ser.is_open == False:
        ser.open()
    data_array = []

   # calibrateServo()
   # setServoRotationAngle(180)

    servo.value = 1350/1000000 * pwm_freq #neutral

       
    cw_rotation_speed   =  0.00035 * pwm_freq#0.5
    ccw_rotation_speed  =  0.0023 * pwm_freq#-0.5
    speed = cw_rotation_speed
    direction = cw
    distance, strength, angle = getLidarData()
    servo.value = speed #setServoRotationSpeed(speed)
    pygame.draw.circle(lcd, pygame.Color("blue"), (400, 400), 2, 2) 

    while True:
        distance, strength, angle = getLidarData()
        if distance > 0:  # data valid
            #print(speed, direction, angle)
            if (angle < min_scan_angle) and (direction == cw):
                #setServoRotationSpeed(0) # stop rotation while data processing
    #                process_data(data_array, pygame.Color("red"))
    #                data_array.clear()
                speed = ccw_rotation_speed
                direction = ccw
                servo.value = speed#setServoRotationSpeed(speed) # rotate CW
                #time.sleep(1)
                lcd.fill((0,0,0))
            if (angle > max_scan_angle) and (direction == ccw):
                #setServoRotationSpeed(0) # stop rotation while data processing
    #                process_data(data_array, pygame.Color("green"))
    #                data_array.clear()
                speed = cw_rotation_speed
                direction = cw
                servo.value = speed#setServoRotationSpeed(speed) # rotate CCW
                #time.sleep(1)
                lcd.fill((0,0,0))
            data_array = []
            if direction == cw:
                data_array.append([distance, strength, angle])
            if (speed == cw_rotation_speed):
                color = pygame.Color("red")
            else:
                color = pygame.Color("green")
            # lcd.fill((0,0,0))
            process_data(data_array, color)
 
  

except KeyboardInterrupt:   # Ctrl+C
    servo.value = 0.00135* pwm_freq#setServoRotationAngle(180)
    if ser != None:
        ser.close()
    pygame.display.quit()
    pygame.quit()
