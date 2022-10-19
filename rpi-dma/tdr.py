import time
import RPi.GPIO as GPIO
import spidev as SPI
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# spi = SPI.SpiDev()
# spi.open(0,0)  # (bus, device)
# spi.mode = 0
# spi.max_speed_hz = 100000

COMP = 5
GPIO.setup(COMP, GPIO.IN)
TRIGGER = 4
GPIO.setup(TRIGGER, GPIO.OUT)
GPIO.output(TRIGGER, GPIO.LOW)

SCK = 11
GPIO.setup(SCK, GPIO.OUT)
GPIO.output(SCK, GPIO.LOW)
SDO = 10
GPIO.setup(SDO, GPIO.OUT)
GPIO.output(SDO, GPIO.LOW)
CS0_B = 8
GPIO.setup(CS0_B, GPIO.OUT)
GPIO.output(CS0_B, GPIO.HIGH)

def spixfer(data, num_bits):
  GPIO.output(CS0_B, GPIO.LOW)
  for i in reversed(range(num_bits)):
    GPIO.output(SDO, 0x01 & (data >> i))

    GPIO.output(SCK, GPIO.HIGH)

    GPIO.output(SCK, GPIO.LOW)
    
  GPIO.output(CS0_B, GPIO.HIGH)


dac_resolution = 12 # resolution in bits
delay_size = 1 # number of delay steps

spi_array = bytearray(5)  # holds 2 x 10 bit delay + 16 bit DAC command/data
dac_cmd     = 0x1000 # DAC enable, gain = 1: VDAC = [0..2024]mV
dac_value   = 0x0080
delayA_value = 0x200 #0x07f
delayB_value = 0x200
spi_data = ((dac_value | dac_cmd) << 20) + ((0x3ff & delayA_value) << 10) + (0x3ff & delayB_value)
spi_array = spi_data.to_bytes(5, byteorder='big')
#print(bin(spi_data))

spixfer(spi_data, 36)
#spi.xfer(spi_array)

# for t in range(delay_size):
#   #set delay value
#   delay_value = t
#   spi_array = [(dac_value >> 8) | dac_cmd, dac_value & 0xff, delayB_value >> 8, delayB_value & 0xff, delayA_value >> 8, delayA_value & 0xff]
#   spi.xfer(spi_array)
#   #reset dac output 
#   dac_value = 0

#   for dac_bit in reversed(range(dac_resolution)):
#     #set DAC value
#     dac_value |= 1 << (dac_bit)
#     spi_array = [(dac_value >> 8) | dac_cmd, dac_value & 0xff, delayB_value >> 8, delayB_value & 0xff, delayA_value >> 8, delayA_value & 0xff]
#     spi.xfer(spi_array)

#     # trigger pulse step
#     GPIO.output(TRIGGER, GPIO.HIGH)
#     GPIO.output(TRIGGER, GPIO.LOW)

#     result = 253 >= dac_value #GPIO.input(COMP)
#     print(dac_bit, dac_value, result)
#     if not result:
#       dac_value -= 1 << (dac_bit)
# print("dac_value", dac_value)




