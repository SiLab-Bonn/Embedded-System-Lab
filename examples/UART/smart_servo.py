import serial
import time
import struct
import sys


ALL_DEVICE              = 0xff    # Broadcast command identifies
CUSTOM_TYPE             = 0x00    # 0x00 indicates no external module
servo_num_max = 12

CTL_ASSIGN_DEV_ID       = 0x10 # device ID assignment
CTL_SYSTEM_RESET        = 0x11 # reset from host
CTL_READ_DEV_VERSION    = 0x12 # read the firmware version
CTL_SET_BAUD_RATE       = 0x13 # Set the baudrate
CTL_CMD_TEST            = 0x14 # just for test
CTL_ERROR_CODE          = 0x15 # error code
SMART_SERVO             = 0x60

# Secondary commands 
SET_SERVO_PID                          = 0x10
SET_SERVO_ABSOLUTE_POS                 = 0x11
SET_SERVO_RELATIVE_POS                 = 0x12
SET_SERVO_CONTINUOUS_ROTATION          = 0x13
SET_SERVO_MOTION_COMPENSATION          = 0x14
CLR_SERVO_MOTION_COMPENSATION          = 0x15
SET_SERVO_BREAK                        = 0x16
SET_SERVO_RGB_LED                      = 0x17
SERVO_SHARKE_HAND                      = 0x18
SET_SERVO_CMD_MODE                     = 0x19

GET_SERVO_STATUS                       = 0x20
GET_SERVO_PID                          = 0x21
GET_SERVO_CUR_POS                      = 0x22
GET_SERVO_SPEED                        = 0x23
GET_SERVO_MOTION_COMPENSATION          = 0x24
GET_SERVO_TEMPERATURE                  = 0x25
GET_SERVO_ELECTRIC_CURRENT             = 0x26
GET_SERVO_VOLTAGE                      = 0x27

SET_SERVO_CURRENT_ANGLE_ZERO_DEGREES   = 0x30
SET_SERVO_ABSOLUTE_ANGLE               = 0x31
SET_SERVO_RELATIVE_ANGLE               = 0x32
SET_SERVO_ABSOLUTE_ANGLE_LONG          = 0x33
SET_SERVO_RELATIVE_ANGLE_LONG          = 0x34
SET_SERVO_PWM_MOVE                     = 0x35
GET_SERVO_CUR_ANGLE                    = 0x36
SET_SERVO_INIT_ANGLE                   = 0x37

START_SYSEX             = 0xF0 # start a MIDI Sysex message
END_SYSEX               = 0xF7 # end a MIDI Sysex message


class SmartServo:
    def __init__(self, com_name, baudrate, dev_id=1):
        self.dev_id = dev_id
        self.ser = serial.Serial(com_name, baudrate)
        if self.ser.is_open == False:
            print("Open serial device...")
            self.ser.open()
            self.available = True
        else:
            print("Serial device already open...")
            self.available = False

    def init(self):
            self.assignDevIdRequest()
            time.sleep(0.1)
            self.setRGBLed(0, 0, 255)
            #self.handShake()
 

    def close(self):
        self.ser.close()

    def write(self, data_byte):
        self.ser.write(bytes([data_byte]))

    def read(self):
        return self.ser.read(1)

    def sendByte(self, val):
        checksum = 0
        val_7bit = [0] * 2
        val_7bit[0] = val & 0x7f
        self.write(val_7bit[0])
        val_7bit[1] = (val >> 7) & 0x7f
        self.write(val_7bit[1])
        checksum = val_7bit[0] + val_7bit[1]
        return(checksum & 0x7f)

    def sendShort(self, val, ignore_high):
        checksum = 0
        val_7bit = [0] * 3
        val_7bit[0] = val & 0x7f
        self.write(val_7bit[0])
        val_7bit[1] = ((val >> 7) & 0xf7) | ((val >>7) & 0x7f)
        self.write(val_7bit[1])
        checksum = val_7bit[0] + val_7bit[1]
        if ignore_high is False:
            val_7bit[2] = (val >> 12) & 0x7f
            checksum += val_7bit[2]
            checksum = checksum & 0x7f
            self.write(val_7bit[2]);
        return(checksum & 0x7f)        


    def sendLong(self, val):
        checksum = 0
        byteVal = int(round(val)).to_bytes(5, byteorder = 'little', signed=True)
        val_7bit = [0] * 5
        val_7bit[0] = byteVal[0] & 0x7f
        self.write(val_7bit[0]);
        val_7bit[1] = ((byteVal[1] << 1) | (byteVal[0] >> 7)) & 0x7f;
        self.write(val_7bit[1]);
        val_7bit[2] = ((byteVal[2] << 2) | (byteVal[1] >> 6)) & 0x7f;
        self.write(val_7bit[2]);
        val_7bit[3] = ((byteVal[3] << 3) | (byteVal[2] >> 5)) & 0x7f;
        self.write(val_7bit[3]);
        val_7bit[4] = (byteVal[3] >> 4) & 0x7f;
        self.write(val_7bit[4]);
        checksum = (val_7bit[0] + val_7bit[1] + val_7bit[2] + val_7bit[3] + val_7bit[4]) & 0x7f;
        return checksum

    def readLong(self, readVal):
        return ((readVal[self.dev_id+2] + (readVal[self.dev_id+3]<<7) + (readVal[self.dev_id+4]<<14) + (readVal[self.dev_id+5]<<21)) + (readVal[self.dev_id+6]<<28))


    def assignDevIdRequest(self):
        self.write(START_SYSEX)
        self.write(ALL_DEVICE)
        self.write(CTL_ASSIGN_DEV_ID)
        self.write(0x00)
        self.write(0x0f)
        self.write(END_SYSEX)
        self.readResult(CTL_ASSIGN_DEV_ID)

    def handShake(self):
        checksum = 0
        if((self.dev_id > servo_num_max) and (self.dev_id != ALL_DEVICE)):
            return False
        self.write(START_SYSEX)
        self.write(self.dev_id)
        self.write(SMART_SERVO)
        self.write(SERVO_SHARKE_HAND)
        checksum = (self.dev_id + SMART_SERVO + SERVO_SHARKE_HAND) & 0x7f
        self.write(checksum)
        self.write(END_SYSEX)
        self.readResult(SERVO_SHARKE_HAND)

    def setRGBLed(self, r_value, g_value, b_value):
        checksum = 0
        self.write(START_SYSEX)
        self.write(self.dev_id)
        self.write(SMART_SERVO)
        self.write(SET_SERVO_RGB_LED)
        checksum = (self.dev_id + SMART_SERVO + SET_SERVO_RGB_LED)
        checksum += self.sendByte(r_value)
        checksum += self.sendByte(g_value)
        checksum += self.sendByte(b_value)
        self.write(checksum & 0x7f)
        self.write(END_SYSEX)
        #self.readResult()
              

    def moveTo(self, angle_value, speed):
        checksum = 0
        self.write(START_SYSEX)
        self.write(self.dev_id)
        self.write(SMART_SERVO)
        self.write(SET_SERVO_ABSOLUTE_ANGLE_LONG)
        checksum = (self.dev_id + SMART_SERVO + SET_SERVO_ABSOLUTE_ANGLE_LONG)
        checksum += self.sendLong(angle_value)
        checksum = checksum & 0x7f
        checksum += self.sendShort(speed, True)
        checksum = checksum & 0x7f;
        self.write(checksum)
        self.write(END_SYSEX);
        #self.readResult()

    def move(self, angle_value, speed):
        checksum = 0
        self.write(START_SYSEX)
        self.write(self.dev_id)
        self.write(SMART_SERVO)
        self.write(SET_SERVO_RELATIVE_ANGLE_LONG)
        checksum = (self.dev_id + SMART_SERVO + SET_SERVO_RELATIVE_ANGLE_LONG)
        checksum += self.sendLong(angle_value)
        checksum = checksum & 0x7f
        checksum += self.sendShort(speed, True)
        checksum = checksum & 0x7f;
        self.write(checksum)
        self.write(END_SYSEX);
        #self.readResult()

    def setPwmMove(self, speed):
        checksum = 0
        self.write(START_SYSEX)
        self.write(self.dev_id)
        self.write(SMART_SERVO)
        self.write(SET_SERVO_PWM_MOVE)
        checksum = (self.dev_id + SMART_SERVO + SET_SERVO_PWM_MOVE)
        checksum += self.sendShort(speed, False)
        checksum = checksum & 0x7f
        self.write(checksum)
        self.write(END_SYSEX);
        #self.readResult()
        
    def setZero(self):
        checksum = 0
        self.write(START_SYSEX)
        self.write(self.dev_id)
        self.write(SMART_SERVO)
        self.write(SET_SERVO_CURRENT_ANGLE_ZERO_DEGREES)
        checksum = (self.dev_id + SMART_SERVO + SET_SERVO_CURRENT_ANGLE_ZERO_DEGREES)
        checksum = checksum & 0x7f
        self.write(checksum)
        self.write(END_SYSEX);
        #self.readResult()
        

    def getAngle(self):
        checksum = 0
        self.write(START_SYSEX)
        self.write(self.dev_id)
        self.write(SMART_SERVO)
        self.write(GET_SERVO_CUR_ANGLE)
        checksum = (self.dev_id + SMART_SERVO + GET_SERVO_CUR_ANGLE + 0x00)        
        checksum = checksum & 0x7f
        self.write(checksum)
        self.write(END_SYSEX);
        result = self.readResult(GET_SERVO_CUR_ANGLE)
        #print(result)
        if result is None:
            return 0
        rawVal = self.readLong(result)
        if (rawVal  & 0x80000000):
            rawVal = -0x100000000 + rawVal
        return (rawVal % 360)

    def readResult(self, dataType):
        parsedData = []
        parseCounter = 0
        Error = False
        #self.ser.reset_input_buffer()
        self.parsing = False
        while parseCounter < 16:
            inputData = int.from_bytes(self.read(), byteorder='big')
            parseCounter = parseCounter +1
            if (self.parsing):
                if (inputData == END_SYSEX): # parsing complete
                    self.parsing = False
                    if (parsedData[2] != dataType):
                        parsedData = None
                        print(parsedData)
                    return parsedData
                else:
                    parsedData.append(inputData)
            else:
                if (inputData == START_SYSEX):
                    self.parsing = True
        print("parse counter timeout", parseCounter)
        return None

            
        
        
      

if __name__ == '__main__':
    try:
        servo1 = SmartServo('/dev/ttyS0', 115200)
        if servo1 is None:
            print("Oops")
        else:
            print("Ok")
            servo1.init()
            servo1.setZero()
            #servo1.moveTo(720, 50)
            servo1.setPwmMove(200)
            while True:
                print(servo1.getAngle())
                time.sleep(0.02)

    except KeyboardInterrupt:   # Ctrl+C
        servo1.setPwmMove(0)
        servo1.close()            
            

