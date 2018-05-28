from math import pi as PI, cos, sin

from constants import *
from maths import Vector3f, look_at_RH
from device import get_dt

class CAMERA_MODE: pass

class DIRECTION:
    
    LEFT     = 0x01
    RIGHT    = 0x02
    FORWARD  = 0x04
    BACKWARD = 0x08
    UP       = 0x0F
    DOWN     = 0x10

class ROTATE:
    
    LEFT  =  1
    RIGHT = -1

# TODO: Eventually create a CameraSettings class.

MIN_ELEVATION = 10.00*D2R
MAX_ELEVATION = 89.99*D2R

class Camera(object):
    """ Camera class contains the setting for manipulating the view matrix. """
    
    def __init__(self, world):
        
        self.world = world
        self._position = Vector3f(5, 2, 5)
        self._target = Vector3f(0, 0, 0)
        self._matrix = None
        self._dirty = True
        
        # Third person camera parameters
        self._range = 10.0
        self._elevation = 10.0 * D2R
        self._yaw = 0.0
        self._speed = 5

    def update(self):
        
        # Update view matrix
        pass
        
    def update_position(self):
        
        pass
    
    def move_target(self, direction):
        
        d = self._speed * get_dt()

        if direction & DIRECTION.FORWARD:
            self._target += [d*sin(self.yaw), 0, d*cos(self.yaw)]        
        if direction & DIRECTION.BACKWARD:
            self._target += [d*sin(self.yaw), 0, d*cos(self.yaw)]        
        if direction & DIRECTION.LEFT:
            self._target += [d*sin(self.yaw + PI_2), 0, d*cos(self.yaw + PI_2)]
        if direction & DIRECTION.RIGHT:
            self._target -= [d*sin(self.yaw + PI_2), 0, d*cos(self.yaw + PI_2)]
        if direction & DIRECTION.UP:
            self._target += [0, d, 0]
        if direction & DIRECTION.DOWN:
            self._target -= [0, d, 0]
            
        self._dirty = True

    def rotate(self, direction):
        
        
        self._yaw += direction * self._rotspeed * get_dt()
        self._dirty = True

    def __constrain_angles(self):
        
        self._elevation = max(min(self._elevation, MIN_ELEVATION), MAX_ELEVATION)
        if self._yaw > PI:
            self._yaw -= TWOPI
        elif self._yaw < -PI:
            self._yaw += TWOPI

    def get_matrix(self):
        
        if self._dirty():
            self.update()
        return self._matrix
    
    def get_elevation(self):
        """ Retrieve the angle off the local horizontal. """
        
        return self._elevation
    
    def get_zenith(self):
        """ Retrieve the angle off the local vertical. """
        
        return PI_2 - self._elevation
    
    
    
