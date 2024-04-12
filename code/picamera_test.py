from picamera2 import Picamera2
from libcamera import controls, Transform
import time

cam = Picamera2()
config = cam.create_preview_configuration(main={"size": (1600, 1200)})
config["transform"] = Transform(hflip=1, vflip=1)
cam.configure(config)
cam.set_controls({"AfMode": controls.AfModeEnum.Auto, "AfTrigger": controls.AfTriggerEnum.Start})
#cam.set_controls({"AfMode": libcamera.controls.AfModeEnum.Manual})
cam.start(show_preview=True)
time.sleep(1)
input()
cam.stop()