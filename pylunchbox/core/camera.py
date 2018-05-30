from math import pi as PI, cos, sin

from constants import *
from maths import Vector3f, look_at_RH, cross, normalize
from device import get_dt

class CAMERA_MODE: pass

class DIRECTION:
    
    LEFT     = 0x01
    RIGHT    = 0x02
    FORWARD  = 0x04
    BACKWARD = 0x08
    UP       = 0x10
    DOWN     = 0x20

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
        
        # View direction coordinates
        self._front = Vector3f(0, 0, 0)
        self._right = Vector3f(0, 0, 0)
        self._up = Vector3f(0, 1, 0)
        
        # Third person camera parameters
        self._range = 10.0
        self._elevation = 10.0 * D2R
        self._yaw = PI_2
        self._speed = 5
        self._rotspeed = 2
        
        self._dirty = True
        self.update()

    def update(self):
        
        # Update view matrix
        if self._dirty:
            self.__constrain_angles()
            self.__update_position()
            self.__update_vectors()
            self._matrix = look_at_RH(self._position, self._target, self._up)
            self._dirty = False
        
    def __constrain_angles(self):
        
        self._elevation = max(min(self._elevation, MAX_ELEVATION), MIN_ELEVATION)
        if self._yaw > PI:
            self._yaw -= TWOPI
        elif self._yaw < -PI:
            self._yaw += TWOPI

    def __update_position(self):
        
        hdist = self._range * cos(self._elevation)
        vdist = self._range * sin(self._elevation)
        
        x = hdist * sin(self._yaw)
        y = vdist
        z = hdist * cos(self._yaw)
        
        self._position[:3] = self._target - (x, -y, z)
        
    def __update_vectors(self):
        
        self._front[:3] = normalize(self._target - self._position)
        self._right[:3] = normalize(cross(self._front, self._up))
        
    def move_target(self, direction):
        
        d = self._speed * get_dt()

        if direction & DIRECTION.FORWARD:
            self._target += Vector3f(d*sin(self._yaw), 0 ,d*cos(self._yaw))
        if direction & DIRECTION.BACKWARD:
            self._target -= [d*sin(self._yaw), 0, d*cos(self._yaw)]        
        if direction & DIRECTION.LEFT:
            self._target -= d*self._right#[d*sin(self._yaw + PI_2), 0, d*cos(self._yaw + PI_2)]
        if direction & DIRECTION.RIGHT:
            self._target += d*self._right#[d*sin(self._yaw + PI_2), 0, d*cos(self._yaw + PI_2)]
        if direction & DIRECTION.UP:
            self._target += [0, d, 0]
        if direction & DIRECTION.DOWN:
            self._target -= [0, d, 0]
            
        self._dirty = True

    def rotate(self, direction):
        
        
        self._yaw += direction * self._rotspeed * get_dt()
        self._dirty = True

    def get_matrix(self):
        
        if self._dirty:
            self.update()
        return self._matrix
    
    def get_elevation(self):
        """ Retrieve the angle off the local horizontal. """
        
        return self._elevation
    
    def get_zenith(self):
        """ Retrieve the angle off the local vertical. """
        
        return PI_2 - self._elevation
    
    
    
