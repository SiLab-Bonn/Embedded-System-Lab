import smbus

bus = smbus.SMBus(1)

bus.write_byte_data(0x10, 0x10, 0x80)
