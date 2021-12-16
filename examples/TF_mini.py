import serial
import time

ser = serial.Serial('/dev/ttyS0', 115200)

def getTFminiData():
    count = ser.in_waiting
    if count > 8:
        recv = ser.read(9)  
        ser.reset_input_buffer()  
        # type(recv), 'str' in python2(recv[0] = 'Y'), 'bytes' in python3(recv[0] = 89)
        # type(recv[0]), 'str' in python2, 'int' in python3 
        
        if recv[0] == 0x59 and recv[1] == 0x59:     #python3
            distance = recv[2] + recv[3] * 256
            strength = recv[4] + recv[5] * 256
            print('(distance: ', distance, ' mm, ss: ', strength, ')')
            ser.reset_input_buffer()
            

if __name__ == '__main__':
    try:
        if ser.is_open == False:
            ser.open()
        #send_str = (0x42, 0x57, 0x02, 0x00, 0x00, 0x00, 0x00, 0x1A)
        #print(send_str)
        #ser.write(send_str)
        while True:    
            getTFminiData()
    except KeyboardInterrupt:   # Ctrl+C
        if ser != None:
            ser.close()
