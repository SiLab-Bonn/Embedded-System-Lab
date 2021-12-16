#!/usr/bin/python
from sense_hat import SenseHat

sense = SenseHat()
sense.set_rotation(0)
red = (255, 0, 0)
sense.show_message("One small step for Pi!", text_colour=red)
