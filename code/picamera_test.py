from picamera2 import Picamera2
import libcamera

cam = Picamera2()
config = cam.create_preview_configuration(main={"size": (1600, 1200)})
config["transform"] = libcamera.Transform(hflip=1, vflip=1)
cam.configure(config)
cam.set_controls({"AfMode": libcamera.controls.AfModeEnum.Continuous})
cam.start(show_preview=True)
input()
cam.stop()