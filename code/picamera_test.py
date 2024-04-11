from picamera2 import Picamera2
from libcamera import controls
cam = Picamera2()
cam.start(show_preview=True)
cam.set_controls({"AfMode": controls.AfModeEnum.Continuous})
input()
cam.stop()