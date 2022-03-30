import serial
import time

ser = serial.Serial('/dev/ttyS0', 115200)

def getData():
    ser.reset_input_buffer()
    while ser.in_waiting < 8:
        pass
    recv = ser.read(8)  
        
    if recv[0] == 0x08 and recv[1] == 0x15:     #python3
        distance = (recv[2] << 8) + recv[3]
        strength = (recv[4] << 8) + recv[5]
        angle    = (recv[6] << 8) + recv[7]
        print('(distance:', distance, 'mm, ss:', strength,'au, angle:', angle/10, '°)')
      #  print(recv)
            #ser.reset_input_buffer()
try:
    if ser.is_open == False:
        ser.open()
    while True:    
            getData()
except KeyboardInterrupt:   # Ctrl+C
    if ser != None:
        ser.close()
