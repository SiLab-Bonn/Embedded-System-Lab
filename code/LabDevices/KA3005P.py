import serial
import time
import serial.tools.list_ports
ports = serial.tools.list_ports.comports()



# KA3005 device does not end the response with a newline character '\n' and also 
# does not expect commands to end with '\n'. The response is read with readline() 
# and an appropriate timeout.

class KA3005P:
  def __init__(self):
    for port, desc, hwid in sorted(ports): # search device
      #print("{}: {} [{}]".format(port, desc, hwid))
      if 'VID:PID=0416:5011' in hwid:
        try:
          self.serial = serial.Serial(port, baudrate=9600, timeout=0.05)
        except serial.SerialException:
          print(f"Port {port} is not available. Exiting.")
          exit(1)
        self.serial.write('*IDN?'.encode()) # check if device responds
        time.sleep(0.1)
        response = self.serial.readline().decode().strip()
        # print(f"Response to *IDN?: {response}")
        if "KA3005" not in response:
          print("Device is not responding. Exiting.")
          exit(1)
        self.set_current(0.1) # set small current limit to avoid damage
        return
    print("Device not found. Exiting.")
    exit(-1)
    
     
  def set_voltage(self, voltage):
    if (voltage > 30):
      voltage = 30
    command = str('VSET1:%.2f' % round(voltage, 2))
    self.serial.write(command.encode())
    time.sleep(0.1)
 
  def set_current(self, current):
    if (current > 5):
      current = 5
    command = str('ISET1:%.3f' % round(current, 3))
    self.serial.write(command.encode())
    time.sleep(0.1)
 
  def enable_output(self):
    self.serial.write('OUT1'.encode())
    time.sleep(0.1)
 
  def disable_output(self):
    self.serial.write('OUT0'.encode())
    time.sleep(0.1)

  def get_voltage(self):
    self.serial.write('VOUT1?'.encode())
    response = self.serial.readline().decode().strip()
    time.sleep(0.1)
    return float(response)

  def get_current(self):
    self.serial.write('IOUT1?'.encode())
    response = self.serial.readline().decode().strip()
    time.sleep(0.1)
    return float(response)

  def close(self):
    self.serial.close()

if __name__ == '__main__':

  ps = KA3005P()
  ps.set_voltage(3.3)
  ps.set_current(0.1)
  ps.enable_output()
  print('Voltage: %.2f' % ps.get_voltage())
  print('Current: %.3f' % ps.get_current())
  input("Press any key to continue...")
  ps.disable_output()
  ps.close()
    
