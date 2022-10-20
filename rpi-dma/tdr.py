import time
import RPi.GPIO as GPIO
import spidev as SPI
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

spi = SPI.SpiDev()
spi.open(0,0)  # (bus, device)
spi.mode = 0
spi.max_speed_hz = 1000000

COMP = 5
GPIO.setup(COMP, GPIO.IN)
TRIGGER = 4
GPIO.setup(TRIGGER, GPIO.OUT)
GPIO.output(TRIGGER, GPIO.LOW)

def reverse_bits(num, bits):
    result = 0
    for i in range(bits):
        result = (result << 1) + (num & 1)
        num >>= 1
    return result

def update_spi_regs(threshold, pulse_delay, sample_delay):
  # MCP4811 DAC samples first 16 bits after CS falling edge (MSB first)
  # SY89297 delay line samples last 20 bits before CS rising edge (LSB first)
  # Both device connect in parallel to the MOSI line (not daisy chained!)
  spi_data = ((threshold | dac_cmd) << 24) + \
             ((0x3ff & reverse_bits(pulse_delay,  10)) << 10) + \
             ((0x3ff & reverse_bits(sample_delay, 10)) << 0)
  #print(bin(spi_data))
  spi.xfer(bytearray(spi_data.to_bytes(5, byteorder='big')))

dac_resolution = 12 # resolution in bits
delay_size = 1 # number of delay steps

dac_cmd      = 0x3000 # DAC enable, gain = 1: VDAC = [0..2047]mV
threshold    = 2048
pulse_delay  = 100 #0x07f
sample_delay = 1000

# update_spi_regs(3000, pulse_delay, sample_delay)
# GPIO.output(TRIGGER, GPIO.HIGH)
# GPIO.output(TRIGGER, GPIO.LOW)

for t in range(1000):
  #set delay value
  pulse_delay = t
  threshold = 2048 # start with mid-level DAC output for SAR ADC conversion

  for dac_bit in reversed(range(dac_resolution)):
    #set DAC value
    threshold |= 1 << (dac_bit)
    update_spi_regs(threshold, pulse_delay, sample_delay)

    # trigger pulse step
    GPIO.output(TRIGGER, GPIO.HIGH)
    GPIO.output(TRIGGER, GPIO.LOW)
    GPIO.output(TRIGGER, GPIO.HIGH)
    
    result = GPIO.input(COMP)
    #print(dac_bit, threshold, result)
    if result:
      threshold -= 1 << (dac_bit)
  print("input level", threshold)

spi.close()


