import serial
from gpiozero import DistanceSensor
from time import sleep

TF = serial.Serial('/dev/ttyS0', 115200)
US = DistanceSensor(echo=5, trigger=4, max_distance=4, queue_len=1)


def getTFminiData():
    count = TF.in_waiting
    distance = 0
    strength = 0
    if count > 8:
        recv = TF.read(9)  
        TF.reset_input_buffer()  
        # type(recv), 'str' in python2(recv[0] = 'Y'), 'bytes' in python3(recv[0] = 89)
        # type(recv[0]), 'str' in python2, 'int' in python3 
        
        if recv[0] == 0x59 and recv[1] == 0x59:     #python3
            distance = recv[2] + recv[3] * 256
            strength = recv[4] + recv[5] * 256
            #print('(distance: ', distance, ' mm, ss: ', strength, ')')
            TF.reset_input_buffer()
    return distance, strength
            

if __name__ == '__main__':
    try:
        if TF.is_open == False:
            TF.open()
        #send_str = (0x42, 0x57, 0x02, 0x00, 0x00, 0x00, 0x00, 0x1A)
        #print(send_str)
        #ser.write(send_str)
        while True:    
            tf_distance, tf_strength = getTFminiData()
            us_distance = US.distance * 1000
            print("US distance: %0.2f mm, TF distance: %0.2f mm, delta : %0.2f mm" %(us_distance, tf_distance, us_distance - tf_distance))
            sleep(0.5)

    except KeyboardInterrupt:   # Ctrl+C
        if TF != None:
            TF.close()
