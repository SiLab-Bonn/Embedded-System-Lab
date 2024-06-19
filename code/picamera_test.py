from picamera2 import Picamera2
from libcamera import controls, Transform
import os
import time

cam = Picamera2()
#config = cam.create_preview_configuration(main={"size": (1600, 1200)})
config = cam.create_preview_configuration(main={"size": (2028, 1520)})
config["transform"] = Transform(hflip=1, vflip=1)
cam.configure(config)
#cam.set_controls({"AfMode": controls.AfModeEnum.Auto, "AfTrigger": controls.AfTriggerEnum.Start})
#cam.set_controls({"AfMode": controls.AfModeEnum.Continuous})
#cam.set_controls({"AfMode": libcamera.controls.AfModeEnum.Manual})
cam.set_controls({"Brightness": 0.1})
cam.start(show_preview=True)

while True:
  os.system('cls||clear')
  print('\033[1m' + 'PiCamera' + '\033[0m' + '\n')
  print('Picture format: %d x %d' % (config["main"]["size"][0], config["main"]["size"][1]))
  print(
'\nCommands:\n\
  <s>     Save picture\n\
  <q>     Quit')
  key = input('Enter command:')

  if key == 's':
    filename = input("Enter file name:")
    cam.capture_file(filename +".jpg")

  if key == 'q':
    break
cam.stop()