/**
 * \par Copyright (C), 2012-2017, MakeBlock
 * \class MSmartServo
 * \brief   Driver for Me Smart Servo device.
 * @file    MSmartServo.cpp
 * @author  MakeBlock
 * @version V1.0.0
 * @date    2017/03/04
 * @brief   Driver for Me Smart Servo device.
 *
 * \par Copyright
 * This software is Copyright (C), 2012-2016, MakeBlock. Use is subject to license \n
 * conditions. The main licensing options available are GPL V2 or Commercial: \n
 *
 * \par Open Source Licensing GPL V2
 * This is the appropriate option if you want to share the source code of your \n
 * application with everyone you distribute it to, and you also want to give them \n
 * the right to share who uses it. If you wish to use this software under Open \n
 * Source Licensing, you must contribute all your source code to the open source \n
 * community in accordance with the GPL Version 2 when your application is \n
 * distributed. See http://www.gnu.org/copyleft/gpl.html
 *
 * \par Description
 * This file is a drive for Smart Servo device, The Smart Servo inherited the
 * MeSerial class from SoftwareSerial.
 *
 *
 * \par Method List:
 *    1. uint8_t MSmartServo::readByte(uint8_t *argv,int16_t idx);
 *    2. short MSmartServo::readShort(uint8_t *argv,int16_t idx,boolean ignore_high);
 *    3. float MSmartServo::readFloat(uint8_t *argv,int16_t idx);
 *    4. long MSmartServo::readLong(uint8_t *argv,int idx);
 *    5. uint8_t MSmartServo::sendByte(uint8_t val);
 *    6. uint8_t MSmartServo::sendShort(int16_t val,boolean ignore_high);
 *    7. uint8_t MSmartServo::sendFloat(float val);
 *    8. uint8_t MSmartServo::sendLong(long val);
 *    9. boolean MSmartServo::assignDevIdRequest(void);
 *    10. boolean MSmartServo::moveTo(uint8_t dev_id,long angle_value,float speed);
 *    11. boolean MSmartServo::move(uint8_t dev_id,long angle_value,float speed);
 *    12. boolean MSmartServo::setZero(uint8_t dev_id);
 *    13. boolean MSmartServo::setBreak(uint8_t dev_id, uint8_t breakStatus);
 *    14. boolean MSmartServo::setRGBLed(uint8_t dev_id, uint8_t r_value, uint8_t g_value, uint8_t b_value);
 *    15. boolean MSmartServo::handSharke(uint8_t dev_id);
 *    16. boolean MSmartServo::setPwmMove(uint8_t dev_id, int16_t pwm_value);
 *    17. boolean MSmartServo::setInitAngle(uint8_t dev_id);
 *    18. long MSmartServo::getAngleRequest(uint8_t devId);
 *    19. float MSmartServo::getSpeedRequest(uint8_t devId);
 *    20. float MSmartServo::getVoltageRequest(uint8_t devId);
 *    21. float MSmartServo::getTempRequest(uint8_t devId);
 *    22. float MSmartServo::getCurrentRequest(uint8_t devId);
 *    23. void MSmartServo::assignDevIdResponse(void *arg);
 *    24. void MSmartServo::processSysexMessage(void);
 *    25. void MSmartServo::smartServoEventHandle(void);
 *    26. void MSmartServo::errorCodeCheckResponse(void *arg);
 *    27. void MSmartServo::smartServoCmdResponse(void *arg);
 *    28. void MSmartServo::begin(long baudrate);
 *    29. void setHardware(bool mode);
 *    30. size_t write(uint8_t byte);
 *
 * \par History:
 * <pre>
 * `<Author>`         `<Time>`        `<Version>`        `<Descr>`
 * Watson         2017/03/04     1.0.0            Build the new.
 * </pre>
 *
 * @example SmartServoTestMoveTo.ino
 *          SmartServoTestMove.ino
 *          SmartServoTestRGBLedColorLoop.ino
 *          SmartServoTestGetParameter.ino

 */
//#include <Arduino.h>
#include "MSmartServo.h"

/**
 * Alternate Constructor which can call your own function to map the serial to arduino port,
 * no pins are used or initialized here. hardware serial will be used by default.
 * \param[in]
 *   None
 */
MSmartServo::MSmartServo() : SoftwareSerial(0, 0)
{
  _hard = true;
  _port = 1;
  parsingSysex = false;
  sysex = {0};
  sysexBytesRead = 0;
}

/**
 * Alternate Constructor which can call your own function to map the serial to arduino port,
 * If the hardware serial was selected, we will used the hardware serial.
 * \param[in]
 *   port - the UART connected to MSmartServo
 *    This parameter can be one of the following values:
 *      @arg 1:  serial connected to MSmartServo
 *      @arg 2:  serial2 connected to MSmartServo
 *      @arg 3:  serial3 connected to MSmartServo
 *      @arg 4:  serial4 connected to MSmartServo
 * \note
 *   For Arduino Uno only one of the following parameters can
 *    be used: 1
 *   For Arduino Mega2560 can the all parameters
 */
MSmartServo::MSmartServo(uint8_t port) : SoftwareSerial(0, 0)
{
  _hard = true;
  switch(port)
  {
    case 1:
      _port = 1;
      break;
    case 2:
      _port = 2;
      break;
    case 3:
      _port = 3;
      break;
    case 4:
      _port = 4;
      break;
    default:
      break;
  }
  parsingSysex = false;
  sysex = {0};
  sysexBytesRead = 0;
}

/**
 * Alternate Constructor which can call your own function to map the Me Smart Servo to arduino port,
 * If the hardware serial was selected, it will used the hardware serial.
 * \param[in]
 *   receivePin - the rx pin of serial(arduino port).
 * \param[in]
 *   transmitPin - the tx pin of serial(arduino port).
 * \param[in]
 *   inverse_logic - Whether the Serial level need inv.
 */
MSmartServo::MSmartServo(uint8_t receivePin, uint8_t transmitPin, bool inverse_logic)\
                          : SoftwareSerial(receivePin, transmitPin, inverse_logic)
{
  _hard = false;
  _port = 0x00;
  parsingSysex = false;
  sysex = {0};
  sysexBytesRead = 0;
}

/**
 * \par Function
 *   setHardware
 * \par Description
 *   if need change the hardware and software serial, this function can be used.
 * \param[in]
 *   mode - if need use hardware serial this value should set to true, or set it false.
 * \par Output
 *   None
 * \return
 *   None
 * \par Others
 *   None
 */
void MSmartServo::setHardware(bool mode)
{
  _hard = mode;
}

/**
 * \par Function
 *   begin
 * \par Description
 *   Sets the speed (baud rate) for the serial communication. Supported baud
 *   rates are 300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 28800, 31250,
 *   38400, 57600, and 115200.
 * \param[in]
 *   baudrate - he baud rate (long)
 * \par Output
 *   None
 * \return
 *   None
 * \par Others
 *   None
 */
void MSmartServo::begin(long baudrate)
{
  if (_hard)
  {
    switch(_port)
    {
#if defined(__AVR_ATmega2560__)
      case 1:
        Serial.begin(baudrate);
        break;
      case 2:
        Serial1.begin(baudrate);
        break;
      case 3:
        Serial2.begin(baudrate);
        break;
      case 4:
        Serial3.begin(baudrate);
        break;
#endif
      default:
        Serial.begin(baudrate);
        break;
    }
  }
  else
  {
    SoftwareSerial::begin(baudrate);
  }
}

/**
 * \par Function
 *   write
 * \par Description
 *   Writes binary data to the serial port. This data is sent as a byte or series of bytes;
 * \param[in]
 *   byte - a value to send as a single byte
 * \par Output
 *   None
 * \return
 *   it will return the number of bytes written, though reading that number is optional
 * \par Others
 *   None
 */
size_t MSmartServo::write(uint8_t byte)
{
  if (_hard)
  {
    switch(_port)
    {
#if defined(__AVR_ATmega2560__)
      case 1:
        Serial.write(byte);
        break;
      case 2:
        Serial1.write(byte);
        break;
      case 3:
        Serial2.write(byte);
        break;
      case 4:
        Serial3.write(byte);
        break;
#endif
      default:
        Serial.write(byte);
        break;
    }
  }
  else
  {
    return (SoftwareSerial::write(byte));
  }
}

/**
 * \par Function
 *   read
 * \par Description
 *   Return a character that was received on the RX pin of the software serial port.
 *   Note that only one SoftwareSerial instance can receive incoming data at a time
 *  (select which one with the listen() function).
 * \par Output
 *   None
 * \return
 *   The character read, or -1 if none is available
 * \par Others
 *   None
 */
int16_t MSmartServo::read(void)
{
  if (_hard)
  {
    switch(_port)
    {
#if defined(__AVR_ATmega2560__)
      case 1:
        Serial.read();
        break;
      case 2:
        Serial1.read();
        break;
      case 3:
        Serial2.read();
        break;
      case 4:
        Serial3.read();
        break;
#endif
      default:
        Serial.read();
        break;
    }
  }
  else
  {
    return (SoftwareSerial::read());
  }
}

/**
 * \par Function
 *   available
 * \par Description
 *   Get the number of bytes (characters) available for reading from a software
 *   serial port. This is data that's already arrived and stored in the serial
 *   receive buffer.
 * \par Output
 *   None
 * \return
 *   The number of bytes available to read
 * \par Others
 *   None
 */
int16_t MSmartServo::available(void)
{
  if (_hard)
  {
    switch(_port)
    {
#if defined(__AVR_ATmega2560__)
      case 1:
        Serial.available();
        break;
      case 2:
        Serial1.available();
        break;
      case 3:
        Serial2.available();
        break;
      case 4:
        Serial3.available();
        break;
#endif
      default:
        Serial.available();
        break;
    }
  }
  else
  {
    return (SoftwareSerial::available());
  }
}

/**
 * \par Function
 *   readByte
 * \par Description
 *   change 2byte 7bit read date to 1byte byte data.
 * \param[in]
 *   *argv - the buffer for input data.\n
 * \param[in]
 *   idx - the index used to identify the first address of read data.\n
 * \par Output
 *   return the converted data.
 * \return
 *   None
 * \par Others
 *   None
 */
uint8_t MSmartServo::readByte(uint8_t *argv,int16_t idx)
{
  uint8_t temp;
  val1byte.byteVal[0] = argv[idx] & 0x7f;
  temp = argv[idx+1] << 7;
  val1byte.byteVal[0] |= temp;
  return val1byte.charVal;
}

/**
 * \par Function
 *   readShort
 * \par Description
 *   change (2byte 7bit) or (3byte 7bit) read date to 2byte short data.
 * \param[in]
 *   *argv - the buffer for input data.\n
 * \param[in]
 *   idx - the index used to identify the first address of read data.\n
 * \param[in]
 *   ignore_high - is there have third byte high-level data.\n
 * \par Output
 *   return the converted data.
 * \return
 *   None
 * \par Others
 *   None
 */
short MSmartServo::readShort(uint8_t *argv,int16_t idx,bool ignore_high)
{
  uint8_t temp;
  val2byte.byteVal[0] = argv[idx] & 0x7f;
  temp = argv[idx+1] << 7;
  val2byte.byteVal[0] |= temp;
  val2byte.byteVal[1] = (argv[idx+1] >> 1) & 0x7f;

  //Send analog can ignored high
  if(ignore_high == false)
  {
    temp = (argv[idx+2] << 6);
    val2byte.byteVal[1] |= temp;
  }
  return val2byte.shortVal;
}

/**
 * \par Function
 *   readFloat
 * \par Description
 *   change (5byte 7bit) read date to 4byte float data.
 * \param[in]
 *   *argv - the buffer for input data.\n
 * \param[in]
 *   idx - the index used to identify the first address of read data.\n
 * \par Output
 *   return the converted data.
 * \return
 *   None
 * \par Others
 *   None
 */
float MSmartServo::readFloat(uint8_t *argv,int16_t idx)
{
  uint8_t temp;
  val4byte.byteVal[0] = argv[idx] & 0x7f;
  temp = argv[idx+1] << 7;
  val4byte.byteVal[0] |= temp;

  val4byte.byteVal[1] =  (argv[idx+1] >> 1) & 0x7f;
  temp = (argv[idx+2] << 6);
  val4byte.byteVal[1] += temp;

  val4byte.byteVal[2] =  (argv[idx+2] >> 2) & 0x7f;
  temp = (argv[idx+3] << 5);
  val4byte.byteVal[2] += temp;

  val4byte.byteVal[3] =  (argv[idx+3] >> 3) & 0x7f;
  temp = (argv[idx+4] << 4);
  val4byte.byteVal[3] += temp;

  return val4byte.floatVal;
}

/**
 * \par Function
 *   readLong
 * \par Description
 *   change (5byte 7bit) read date to 4byte long data.
 * \param[in]
 *   *argv - the buffer for input data.\n
 * \param[in]
 *   idx - the index used to identify the first address of read data.\n
 * \par Output
 *   return the converted data.
 * \return
 *   None
 * \par Others
 *   None
 */
long MSmartServo::readLong(uint8_t *argv,int idx)
{
  uint8_t temp;
  val4byte.byteVal[0] = argv[idx] & 0x7f;
  temp = argv[idx+1] << 7;
  val4byte.byteVal[0] |= temp;

  val4byte.byteVal[1] =  (argv[idx+1] >> 1) & 0x7f;
  temp = (argv[idx+2] << 6);
  val4byte.byteVal[1] += temp;

  val4byte.byteVal[2] =  (argv[idx+2] >> 2) & 0x7f;
  temp = (argv[idx+3] << 5);
  val4byte.byteVal[2] += temp;

  val4byte.byteVal[3] =  (argv[idx+3] >> 3) & 0x7f;
  temp = (argv[idx+4] << 4);
  val4byte.byteVal[3] += temp;

  return val4byte.longVal;
}

/**
 * \par Function
 *   sendByte
 * \par Description
 *   send (1byte 8bit) date to 2byte 7bit data.
 * \param[in]
 *   val - the byte data to be converted.\n
 * \par Output
 *   return the checksum data.
 * \return
 *   None
 * \par Others
 *   None
 */
uint8_t MSmartServo::sendByte(uint8_t val)
{
  uint8_t checksum;
  uint8_t val_7bit[2]={0};
  val1byte.charVal = val;
  val_7bit[0] = val1byte.byteVal[0] & 0x7f;
  write(val_7bit[0]);
  val_7bit[1] = (val1byte.byteVal[0] >> 7) & 0x7f;
  write(val_7bit[1]);
  checksum = val_7bit[0] + val_7bit[1];
  checksum = checksum & 0x7f;
  return checksum;
}

/**
 * \par Function
 *   sendShort
 * \par Description
 *   send (2byte short) date to 2byte or 3byte 7bit data.
 * \param[in]
 *   val - the short data to be converted.\n
 * \param[in]
 *   ignore_high - is there have third byte high-level data.\n
 * \par Output
 *   return the checksum data.
 * \return
 *   None
 * \par Others
 *   None
 */
uint8_t MSmartServo::sendShort(int16_t val,bool ignore_high)
{
  uint8_t checksum;
  uint8_t val_7bit[3]={0};
  val2byte.shortVal = val;
  val_7bit[0] = val2byte.byteVal[0] & 0x7f;
  write(val_7bit[0]);
  val_7bit[1] = ((val2byte.byteVal[1] << 1) | (val2byte.byteVal[0] >> 7)) & 0x7f;
  write(val_7bit[1]);
  checksum = val_7bit[0] + val_7bit[1];
  //Send analog can ignored high
  if(ignore_high == false)
  {
    val_7bit[2] = (val2byte.byteVal[1] >> 6) & 0x7f;
    checksum += val_7bit[2];
    checksum = checksum & 0x7f;
    write(val_7bit[2]);
  }
}

/**
 * \par Function
 *   sendFloat
 * \par Description
 *   send (4byte float) date to 5byte 7bit data.
 * \param[in]
 *   val - the short data to be converted.\n
 * \par Output
 *   return the checksum data.
 * \return
 *   None
 * \par Others
 *   None
 */
uint8_t MSmartServo::sendFloat(float val)
{
  uint8_t checksum;
  uint8_t val_7bit[5]={0};
  val4byte.floatVal = val;
  val_7bit[0] = val4byte.byteVal[0] & 0x7f;
  write(val_7bit[0]);
  val_7bit[1] = ((val4byte.byteVal[1] << 1) | (val4byte.byteVal[0] >> 7)) & 0x7f;
  write(val_7bit[1]);
  val_7bit[2] = ((val4byte.byteVal[2] << 2) | (val4byte.byteVal[1] >> 6)) & 0x7f;
  write(val_7bit[2]);
  val_7bit[3] = ((val4byte.byteVal[3] << 3) | (val4byte.byteVal[2] >> 5)) & 0x7f;
  write(val_7bit[3]);
  val_7bit[4] = (val4byte.byteVal[3] >> 4) & 0x7f;
  write(val_7bit[4]);
  checksum = (val_7bit[0] + val_7bit[1] + val_7bit[2] + val_7bit[3] + val_7bit[4]) & 0x7f;
  return checksum;
}

/**
 * \par Function
 *   sendLong
 * \par Description
 *   send (4byte long) date to 5byte 7bit data.
 * \param[in]
 *   val - the short data to be converted.\n
 * \par Output
 *   return the checksum data.
 * \return
 *   None
 * \par Others
 *   None
 */
uint8_t MSmartServo::sendLong(long val)
{
  uint8_t checksum;
  uint8_t val_7bit[5]={0};
  val4byte.longVal = val;
  val_7bit[0] = val4byte.byteVal[0] & 0x7f;
  write(val_7bit[0]);
  val_7bit[1] = ((val4byte.byteVal[1] << 1) | (val4byte.byteVal[0] >> 7)) & 0x7f;
  write(val_7bit[1]);
  val_7bit[2] = ((val4byte.byteVal[2] << 2) | (val4byte.byteVal[1] >> 6)) & 0x7f;
  write(val_7bit[2]);
  val_7bit[3] = ((val4byte.byteVal[3] << 3) | (val4byte.byteVal[2] >> 5)) & 0x7f;
  write(val_7bit[3]);
  val_7bit[4] = (val4byte.byteVal[3] >> 4) & 0x7f;
  write(val_7bit[4]);
  checksum = (val_7bit[0] + val_7bit[1] + val_7bit[2] + val_7bit[3] + val_7bit[4]) & 0x7f;
  return checksum;
}

/**
 * \par Function
 *   assignDevIdRequest
 * \par Description
 *   distribution device ID number to the smart servo link.
 * \param[in]
 *   None
 * \par Output
 *   None
 * \return
 *   If the assignment is successful, return true.
 * \par Others
 *   None
 */
bool MSmartServo::assignDevIdRequest(void)
{
  write(START_SYSEX);
  write(ALL_DEVICE);
  write(CTL_ASSIGN_DEV_ID);
  write(0x00);
  write(0x0f);
  write(END_SYSEX);
  resFlag &= 0xfe;
  cmdTimeOutValue = millis();
  while((resFlag & 0x01) != 0x01)
  {
    smartServoEventHandle();
    if(millis() - cmdTimeOutValue > 2000)
    {
      resFlag &= 0xfe;
      return false;
    }
  }
  resFlag &= 0xfe;
  return true;
}

/**
 * \par Function
 *   moveTo
 * \par Description
 *   smart servo moves to the absolute angle.
 * \param[in]
 *    dev_id - the device id of servo that we want to move.
 * \param[in]
 *    angle_value - the absolute angle value we want move to.
 * \param[in]
 *    speed - move speed value(The unit is rpm).
 * \par Output
 *   None
 * \return
 *   If the assignment is successful, return true.
 * \par Others
 *   None
 */
bool MSmartServo::moveTo(uint8_t dev_id,long angle_value,float speed)
{
  uint8_t checksum;
  write(START_SYSEX);
  write(dev_id);
  write(SMART_SERVO);
  write(SET_SERVO_ABSOLUTE_ANGLE_LONG);
  checksum = (dev_id + SMART_SERVO + SET_SERVO_ABSOLUTE_ANGLE_LONG);
  checksum += sendLong(angle_value);
  checksum = checksum & 0x7f;
  checksum += sendShort((int)speed,true);
  checksum = checksum & 0x7f;
  write(checksum);
  write(END_SYSEX);
  resFlag &= 0xbf;
  cmdTimeOutValue = millis();
  while((resFlag & 0x40) != 0x40)
  {
    smartServoEventHandle();
    if(millis() - cmdTimeOutValue > 2000)
    {
      resFlag &= 0xbf;
      return false;
    }
  }
  resFlag &= 0xbf;
  return true;
}

/**
 * \par Function
 *   move
 * \par Description
 *   smart servo moves to the relative angle.
 * \param[in]
 *    dev_id - the device id of servo that we want to move.
 * \param[in]
 *    angle_value - the relative angle value we want move to.
 * \param[in]
 *    speed - move speed value(The unit is rpm).
 * \par Output
 *   None
 * \return
 *   If the assignment is successful, return true.
 * \par Others
 *   None
 */
bool MSmartServo::move(uint8_t dev_id,long angle_value,float speed)
{
  uint8_t checksum;
  write(START_SYSEX);
  write(dev_id);
  write(SMART_SERVO);
  write(SET_SERVO_RELATIVE_ANGLE_LONG);
  checksum = (dev_id + SMART_SERVO + SET_SERVO_RELATIVE_ANGLE_LONG);
  checksum += sendLong(angle_value);
  checksum = checksum & 0x7f;
  checksum += sendShort((int)speed,true);
  checksum = checksum & 0x7f;
  write(checksum);
  write(END_SYSEX);
  resFlag &= 0xbf;
  cmdTimeOutValue = millis();
  while((resFlag & 0x40) != 0x40)
  {
    smartServoEventHandle();
    if(millis() - cmdTimeOutValue > 2000)
    {
      resFlag &= 0xbf;
      return false;
    }
  }
  resFlag &= 0xbf;
  return true;
}

/**
 * \par Function
 *   setZero
 * \par Description
 *   set smart servo current angle zero postion.
 * \param[in]
 *    dev_id - the device id of servo that we want to initialization position.
 * \par Output
 *   None
 * \return
 *   If the assignment is successful, return true.
 * \par Others
 *   None
 */
bool MSmartServo::setZero(uint8_t dev_id)
{
  uint8_t checksum;
  write(START_SYSEX);
  write(dev_id);
  write(SMART_SERVO);
  write(SET_SERVO_CURRENT_ANGLE_ZERO_DEGREES);
  checksum = (dev_id + SMART_SERVO + SET_SERVO_CURRENT_ANGLE_ZERO_DEGREES);
  write(checksum);
  write(END_SYSEX);
  resFlag &= 0xbf;
  cmdTimeOutValue = millis();
  while((resFlag & 0x40) != 0x40)
  {
    smartServoEventHandle();
    if(millis() - cmdTimeOutValue > 2000)
    {
      resFlag &= 0xbf;
      return false;
    }
  }
  resFlag &= 0xbf;
  return true;
}

/**
 * \par Function
 *   setBreak
 * \par Description
 *   set smart servo break status.
 * \param[in]
 *    dev_id - the device id of servo that we want to set.
 * \param[in]
 *    breakStatus - the break status of servo.
 * \par Output
 *   None
 * \return
 *   If the assignment is successful, return true.
 * \par Others
 *   None
 */
bool MSmartServo::setBreak(uint8_t dev_id, uint8_t breakStatus)
{
  uint8_t checksum;
  write(START_SYSEX);
  write(dev_id);
  write(SMART_SERVO);
  write(SET_SERVO_BREAK);
  write(breakStatus);
  checksum = (dev_id + SMART_SERVO + SET_SERVO_BREAK + breakStatus);
  write(checksum);
  write(END_SYSEX);
  resFlag &= 0xbf;
  cmdTimeOutValue = millis();
  while((resFlag & 0x40) != 0x40)
  {
    smartServoEventHandle();
    if(millis() - cmdTimeOutValue > 2000)
    {
      resFlag &= 0xbf;
      return false;
    }
  }
  resFlag &= 0xbf;
  return true;
}

/**
 * \par Function
 *   setRGBLed
 * \par Description
 *   set the color of smart servo's RGB LED.
 * \param[in]
 *    dev_id - the device id of servo that we want to set.
 * \param[in]
 *    r_value - Red component.
 * \param[in]
 *    g_value - green component.
 * \param[in]
 *    B_value - Blue component.
 * \par Output
 *   None
 * \return
 *   If the assignment is successful, return true.
 * \par Others
 *   None
 */
bool MSmartServo::setRGBLed(uint8_t dev_id, uint8_t r_value, uint8_t g_value, uint8_t b_value)
{
  uint8_t checksum;
  write(START_SYSEX);
  write(dev_id);
  write(SMART_SERVO);
  write(SET_SERVO_RGB_LED);
  checksum = (dev_id + SMART_SERVO + SET_SERVO_RGB_LED);
  checksum += sendByte(r_value);
  checksum += sendByte(g_value);
  checksum += sendByte(b_value);
  write(checksum);
  write(END_SYSEX);
  resFlag &= 0xbf;
  cmdTimeOutValue = millis();
  while((resFlag & 0x40) != 0x40)
  {
    smartServoEventHandle();
    if(millis() - cmdTimeOutValue > 2000)
    {
      resFlag &= 0xbf;
      return false;
    }
  }
  resFlag &= 0xbf;
  return true;
}

/**
 * \par Function
 *   handSharke
 * \par Description
 *   This function is used MCU and servo handshake.
 * \param[in]
 *    dev_id - the device id of servo that we want to handsharke.
 * \par Output
 *   None
 * \return
 *   If the assignment is successful, return true.
 * \par Others
 *   None
 */
bool MSmartServo::handSharke(uint8_t dev_id)
{
  uint8_t checksum;
  write(START_SYSEX);
  write(dev_id);
  write(SMART_SERVO);
  write(SERVO_SHARKE_HAND);
  checksum = (dev_id + SMART_SERVO + SERVO_SHARKE_HAND);
  write(checksum);
  write(END_SYSEX);
  resFlag &= 0xbf;
  cmdTimeOutValue = millis();
  while((resFlag & 0x40) != 0x40)
  {
    smartServoEventHandle();
    if(millis() - cmdTimeOutValue > 2000)
    {
      resFlag &= 0xbf;
      return false;
    }
  }
  resFlag &= 0xbf;
  return true;
}

/**
 * \par Function
 *   setPwmMove
 * \par Description
 *   This function is used to set the pwm motion of smart servo.
 * \param[in]
 *    dev_id - the device id of servo that we want to set.
 * \param[in]
 *    pwm_value - the pwm value we wan't set the servo motor.
 * \par Output
 *   None
 * \return
 *   If the assignment is successful, return true.
 * \par Others
 *   None
 */
bool MSmartServo::setPwmMove(uint8_t dev_id, int16_t pwm_value)
{
  uint8_t checksum;
  write(START_SYSEX);
  write(dev_id);
  write(SMART_SERVO);
  write(SET_SERVO_PWM_MOVE);
  checksum = (dev_id + SMART_SERVO + SET_SERVO_PWM_MOVE);
  checksum += sendShort(pwm_value,false);
  write(checksum);
  write(END_SYSEX);
  resFlag &= 0xbf;
  cmdTimeOutValue = millis();
  while((resFlag & 0x40) != 0x40)
  {
    smartServoEventHandle();
    if(millis() - cmdTimeOutValue > 2000)
    {
      resFlag &= 0xbf;
      return false;
    }
  }
  resFlag &= 0xbf;
  return true;
}

/**
 * \par Function
 *   setInitAngle
 * \par Description
 *   This function is used to move smart servo to its 0 degrees.
 * \param[in]
 *    dev_id - the device id of servo that we want to set.
 * \par Output
 *   None
 * \return
 *   If the assignment is successful, return true.
 * \par Others
 *   None
 */
bool MSmartServo::setInitAngle(uint8_t dev_id)
{
  uint8_t checksum;
  write(START_SYSEX);
  write(dev_id);
  write(SMART_SERVO);
  write(SET_SERVO_INIT_ANGLE);
  checksum = (dev_id + SMART_SERVO + SET_SERVO_INIT_ANGLE);
  write(checksum);
  write(END_SYSEX);
  resFlag &= 0xbf;
  cmdTimeOutValue = millis();
  while((resFlag & 0x40) != 0x40)
  {
    smartServoEventHandle();
    if(millis() - cmdTimeOutValue > 2000)
    {
      resFlag &= 0xbf;
      return false;
    }
  }
  resFlag &= 0xbf;
  return true;
}

/**
 * \par Function
 *   getAngleRequest
 * \par Description
 *   This function used to get the smart servo's angle.
 * \param[in]
 *   devId - the device id of servo that we want to read its angle.
 * \par Output
 *   None
 * \return
 *   the angle of smart servo.
 * \par Others
 *   None
 */
long MSmartServo::getAngleRequest(uint8_t devId)
{
  uint8_t checksum;
  write(START_SYSEX);
  write(devId);
  write(SMART_SERVO);
  write(GET_SERVO_CUR_ANGLE);
  write(0x00);
  checksum = devId + SMART_SERVO + GET_SERVO_CUR_ANGLE + 0x00;
  write(checksum);
  write(END_SYSEX);
  resFlag &= 0xfd;
  cmdTimeOutValue = millis();
  while((resFlag & 0x02) != 0x02)
  {
    smartServoEventHandle();
    if(millis() - cmdTimeOutValue > 2000)
    {
      break;
    }
  }
  resFlag &= 0xfd;
  return servo_dev_list[devId - 1].angleValue;
}

/**
 * \par Function
 *   getSpeedRequest
 * \par Description
 *   This function used to get the smart servo's speed.
 * \param[in]
 *   devId - the device id of servo that we want to read its speed.
 * \par Output
 *   None
 * \return
 *   the speed of smart servo.
 * \par Others
 *   None
 */
float MSmartServo::getSpeedRequest(uint8_t devId)
{
  uint8_t checksum;
  write(START_SYSEX);
  write(devId);
  write(SMART_SERVO);
  write(GET_SERVO_SPEED);
  write(0x00);
  checksum = devId + SMART_SERVO + GET_SERVO_SPEED + 0x00;
  write(checksum);
  write(END_SYSEX);
  resFlag &= 0xfb;
  cmdTimeOutValue = millis();
  while((resFlag & 0x04) != 0x04)
  {
    smartServoEventHandle();
    if(millis() - cmdTimeOutValue > 2000)
    {
      break;
    }
  }
  resFlag &= 0xfb;
  return servo_dev_list[devId - 1].servoSpeed;
}

/**
 * \par Function
 *   getVoltageRequest
 * \par Description
 *   This function used to get the smart servo's voltage.
 * \param[in]
 *   devId - the device id of servo that we want to read its voltage.
 * \par Output
 *   None
 * \return
 *   the voltage of smart servo.
 * \par Others
 *   None
 */
float MSmartServo::getVoltageRequest(uint8_t devId)
{
  uint8_t checksum;
  write(START_SYSEX);
  write(devId);
  write(SMART_SERVO);
  write(GET_SERVO_VOLTAGE);
  write(0x00);
  checksum = devId + SMART_SERVO + GET_SERVO_VOLTAGE + 0x00;
  write(checksum);
  write(END_SYSEX);
  resFlag &= 0xf7;
  cmdTimeOutValue = millis();
  while((resFlag & 0x08) != 0x08)
  {
    smartServoEventHandle();
    if(millis() - cmdTimeOutValue > 2000)
    {
      break;
    }
  }
  return servo_dev_list[devId - 1].voltage;
}

/**
 * \par Function
 *   getTempRequest
 * \par Description
 *   This function used to get the smart servo's temperature.
 * \param[in]
 *   devId - the device id of servo that we want to read its temperature.
 * \par Output
 *   None
 * \return
 *   the temperature of smart servo.
 * \par Others
 *   None
 */
float MSmartServo::getTempRequest(uint8_t devId)
{
  uint8_t checksum;
  write(START_SYSEX);
  write(devId);
  write(SMART_SERVO);
  write(GET_SERVO_TEMPERATURE);
  write(0x00);
  checksum = devId + SMART_SERVO + GET_SERVO_TEMPERATURE + 0x00;
  write(checksum);
  write(END_SYSEX);
  resFlag &= 0xef;
  cmdTimeOutValue = millis();
  while((resFlag & 0x10) != 0x10)
  {
    smartServoEventHandle();
    if(millis() - cmdTimeOutValue > 2000)
    {
      break;
    }
  }
  resFlag &= 0xf7;
  return servo_dev_list[devId - 1].temperature;
}

/**
 * \par Function
 *   getCurrentRequest
 * \par Description
 *   This function used to get the smart servo's current.
 * \param[in]
 *   devId - the device id of servo that we want to read its current.
 * \par Output
 *   None
 * \return
 *   the current of smart servo.
 * \par Others
 *   None
 */
float MSmartServo::getCurrentRequest(uint8_t devId)
{
  uint8_t checksum;
  write(START_SYSEX);
  write(devId);
  write(SMART_SERVO);
  write(GET_SERVO_ELECTRIC_CURRENT);
  write(0x00);
  checksum = devId + SMART_SERVO + GET_SERVO_ELECTRIC_CURRENT + 0x00;
  write(checksum);
  write(END_SYSEX);
  resFlag &= 0xdf;
  cmdTimeOutValue = millis();
  while((resFlag & 0x20) != 0x20)
  {
    smartServoEventHandle();
    if(millis() - cmdTimeOutValue > 2000)
    {
      break;
    }
  }
  resFlag &= 0xdf;
  return servo_dev_list[devId - 1].current;
}

/**
 * \par Function
 *   assignDevIdResponse
 * \par Description
 *   distribution device ID number return packet processing.
 * \param[in]
 *   *arg - address of input parameter.
 * \par Output
 *   None
 * \return
 *   None
 * \par Others
 *   None
 */
void MSmartServo::assignDevIdResponse(void *arg)
{
  //The arg from value[0]
  uint8_t DeviceId = 0;
  uint8_t ServiceId = 0;
  DeviceId = sysex.val.dev_id;
  ServiceId = sysex.val.srv_id;
  resFlag |= 0x01;
}

/**
 * \par Function
 *   processSysexMessage
 * \par Description
 *   This function is used to process protocol messages of smart servo.
 * \param[in]
 *   None
 * \par Output
 *   None
 * \return
 *   None
 * \par Others
 *   None
 */
void MSmartServo::processSysexMessage(void)
{
  uint8_t i;
  if(sysex.val.dev_id != ALL_DEVICE)
  {
    switch(sysex.val.srv_id)
    {
      case CTL_ASSIGN_DEV_ID:
        assignDevIdResponse((void*)NULL);
        break;
      case CTL_ERROR_CODE:
        errorCodeCheckResponse((void*)NULL);
        break;
      case SMART_SERVO:
        smartServoCmdResponse((void*)NULL);
        break;
      default:
        break;
    }
  }
}

/**
 * \par Function
 *   smartServoEventHandle
 * \par Description
 *   This function is used to process protocol messages of smart servo.
 * \param[in]
 *   None
 * \par Output
 *   None
 * \return
 *   None
 * \par Others
 *   None
 */
void MSmartServo::smartServoEventHandle(void)
{
  while (available())
  {
    // get the new byte:
    uint8_t inputData = read();
    if(parsingSysex)
    {
      if (inputData == END_SYSEX)
      {
        //stop sysex byte
        parsingSysex = false;
        //fire off handler function
        processSysexMessage();
      }
      else
      {
        //normal data byte - add to buffer
        sysex.storedInputData[sysexBytesRead] = inputData;
        sysexBytesRead++;
        if(sysexBytesRead > DEFAULT_UART_BUF_SIZE-1)
        {
          parsingSysex = false;
          sysexBytesRead = 0;
        }
      }
    }
    else if(inputData == START_SYSEX)
    {
      parsingSysex = true;
      sysexBytesRead = 0;
    }
  }
}

/**
 * \par Function
 *   errorCodeCheckResponse
 * \par Description
 *   This function is used to process the error response message of smart servo.
 * \param[in]
 *   *arg - address of input parameter.
 * \par Output
 *   None
 * \return
 *   None
 * \par Others
 *   None
 */
void MSmartServo::errorCodeCheckResponse(void *arg)
{
  uint8_t DeviceId = 0;
  uint8_t ServiceId = 0;
  uint8_t errorcode = WRONG_TYPE_OF_SERVICE;
  DeviceId = sysex.val.dev_id;
  ServiceId = sysex.val.srv_id;
  if(ServiceId == CTL_ERROR_CODE)
  {
    errorcode = sysex.val.value[0];
    resFlag |= 0x40;
  }
}

/**
 * \par Function
 *   smartServoCmdResponse
 * \par Description
 *   This function is used to process the response message of smart servo.
 * \param[in]
 *   *arg - address of input parameter.
 * \par Output
 *   None
 * \return
 *   None
 * \par Others
 *   None
 */
void MSmartServo::smartServoCmdResponse(void *arg)
{
  long angle_v;
  float speed_v;
  float temp_v;
  float vol_v;
  float current_v;
  int16_t cmd;
  cmd = (int16_t)sysex.val.value[0];
  switch(cmd)
  {
    case GET_SERVO_CUR_ANGLE:
      angle_v = readLong(sysex.val.value,1);
      servo_dev_list[sysex.val.dev_id - 1].angleValue = angle_v;
      resFlag |= 0x02;
      break;
    case GET_SERVO_SPEED:
      speed_v = readFloat(sysex.val.value,1);
      servo_dev_list[sysex.val.dev_id - 1].servoSpeed = speed_v;
      resFlag |= 0x04;
      break;
    case GET_SERVO_VOLTAGE:
      vol_v = readFloat(sysex.val.value,1);
      servo_dev_list[sysex.val.dev_id - 1].voltage = vol_v;
      resFlag |= 0x08;
      break;
    case GET_SERVO_TEMPERATURE:
      temp_v = readFloat(sysex.val.value,1);
      servo_dev_list[sysex.val.dev_id - 1].temperature = temp_v;
      resFlag |= 0x10;
      break;
    case GET_SERVO_ELECTRIC_CURRENT:
      current_v = readFloat(sysex.val.value,1);
      servo_dev_list[sysex.val.dev_id - 1].current = current_v;
      resFlag |= 0x20;
      break;
    default:
      break;
  }
}
