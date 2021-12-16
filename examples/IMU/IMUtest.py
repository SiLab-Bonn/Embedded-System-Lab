from sense_hat import SenseHat
import pygame
from pygame.locals import *
import sys
from OpenGL.GL import *
from OpenGL.GLU import *

verticies = (
    (1, -1, -1),
    (1, 1, -1),
    (-1, 1, -1),
    (-1, -1, -1),
    (1, -1, 1),
    (1, 1, 1),
    (-1, -1, 1),
    (-1, 1, 1)
    )

edges = (
    (0,1),
    (0,3),
    (0,4),
    (2,1),
    (2,3),
    (2,7),
    (6,3),
    (6,4),
    (6,7),
    (5,1),
    (5,4),
    (5,7)
    )


def Cube():
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(verticies[vertex])
    glEnd()


sense = SenseHat()
sense.set_imu_config(True, True, True)  # all sensors enabled
orientation = sense.get_orientation()
yaw_ofs = orientation["yaw"] # get yaw offset
    
pygame.init()
display = (800,600)
pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
glTranslatef(0.0,0.0, -5)

while True:
    for event in pygame.event.get():
        if (event.type == KEYUP and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit(0)
            
    orientation = sense.get_orientation()
    pitch = orientation["pitch"]
    roll  = orientation["roll"]
    yaw   = orientation["yaw"] - yaw_ofs
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glPushMatrix()
    glRotate(-roll, 1, 0, 0)
    glRotate(-yaw,  0, 1, 0)
    glRotate(-pitch,0, 0, 1)
    Cube()
    glPopMatrix()
    pygame.display.flip()
    pygame.time.wait(10)
