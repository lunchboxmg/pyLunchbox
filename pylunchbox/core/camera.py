from math import pi as PI, cos, sin, atan2, sqrt
from functools import partial

from constants import *
from maths import Vector3f, look_at_RH, cross, normalize, clamp, look_at_LH
from device import get_dt

class CAMERA_MODE: pass

class DIRECTION:
    """ Enum-like flag class for designating camera direction. """
    
    LEFT     = 0x01
    RIGHT    = 0x02
    FORWARD  = 0x04
    BACKWARD = 0x08
    UP       = 0x10
    DOWN     = 0x20

class ROTATE:
    """ Enum-like flag class for designating camera rotation direction. """
    
    LEFT  =  1
    RIGHT = -1

# TODO: Eventually create a CameraSettings class.

MIN_ELEVATION = 10.00*D2R
MAX_ELEVATION = 89.99*D2R
MIN_ZOOM = 0.5
MAX_ZOOM = 2.0

_clamp_elev = partial(clamp, x_min=MIN_ELEVATION, x_max=MAX_ELEVATION)
_clamp_zoom = partial(clamp, x_min=MIN_ZOOM, x_max=MAX_ZOOM)

class Camera(object):
    """ Camera class contains the setting for manipulating the view matrix. """
    
    def __init__(self, world):
        
        self.world = world
        self._position = Vector3f(5, 2, 5)
        self._target = Vector3f(0, 0, 0)
        self._matrix = None
        
        # View direction coordinates
        self._front = Vector3f(0, 0, 0) # Camera Z-Axis
        self._right = Vector3f(0, 0, 0) # Camera X-Axis
        self._up = Vector3f(0, 1, 0)    # Local vertical
        
        # Third person camera parameters
        self._range = 10.0
        self._zoom = 1.0
        self._elevation = 10.0 * D2R
        self._yaw = PI#PI_2
        self._speed = 5
        self._rotspeed = 2
        self._speed_zoom = 2
        
        self._dirty = True
        self.update()

    def update(self):
        """ Update the camera.

        NOTE: If the camera has registered no changes, nothing happens.
        """
        
        # Update view matrix
        if self._dirty:
            self.__constrain_angles()
            self.__update_position()
            self.__update_vectors()
            self._dirty = False
        
    def __constrain_angles(self):
        """ Internal function to constrain the rotation angles. """

        self._elevation = max(min(self._elevation, MAX_ELEVATION), MIN_ELEVATION)
        if self._yaw > PI:
            self._yaw -= TWOPI
        elif self._yaw < -PI:
            self._yaw += TWOPI

    def __update_position(self):
        """ Internal function to recalculate the camera's position relative to 
        the target. """
        
        hdist = self._range * self._zoom * cos(self._elevation)
        vdist = self._range * self._zoom * sin(self._elevation)
        
        x = hdist * sin(self._yaw)
        y = vdist
        z = hdist * cos(self._yaw)
        
        self._position[:3] = self._target - (x, -y, z)
        
    def __update_vectors(self):
        """ Update the local camera coordinates. """
        
        self._matrix = m = look_at_RH(self._position, self._target, self._up)
        self._front[:3] = normalize(m[:3,2])
        self._right[:3] = normalize(m[:3,0])
        
    def move_target(self, direction):
        """ Move the camera's target position.

        Parameters
        ----------
        direction :obj:`int` from :class:`DIRECTION`
            Combination of directions the user wants the target to move.
        """
        
        d = self._speed * get_dt()

        if direction & DIRECTION.FORWARD:
            self._target += Vector3f(d*sin(self._yaw), 0 ,d*cos(self._yaw))
        if direction & DIRECTION.BACKWARD:
            self._target -= [d*sin(self._yaw), 0, d*cos(self._yaw)]        
        if direction & DIRECTION.LEFT:
            self._target -= d*self._right
        if direction & DIRECTION.RIGHT:
            self._target += d*self._right
        if direction & DIRECTION.UP:
            self._target += [0, d, 0]
        if direction & DIRECTION.DOWN:
            self._target -= [0, d, 0]
            
        self._dirty = True

    def rotate(self, yaw=0.0, pitch=0.0, is_direction=True):
        """ Rotate the camera's yaw or pitch angles.

        Parameters
        ----------
        yaw : :obj:`float`
            The amount to rotate the yaw angle.
        pitch : :obj:`float`
            The amount to rotate the pitch (elevation) angle.
        is_direction : :obj:`bool`, default is :obj:`True`
            Dictates if the angle value are directions if true, else the values
            are amounts in radians.
        """

        if is_direction:
            if yaw: yaw = yaw / abs(yaw)
            if pitch: pitch = pitch / abs(pitch)
        self._yaw += yaw * self._rotspeed * get_dt()
        self._elevation += pitch * self._rotspeed * get_dt()
        self._dirty = True

    def zoom(self, amount, is_direction=True):
        """ Zoom. """

        if is_direction:
            amount = amount / abs(amount)
            self._zoom += amount * self._speed_zoom * get_dt()
        else:
            self._zoom = amount
        self._zoom = _clamp_zoom(self._zoom)
        self._dirty = True

    def move_vertical(self, amount, is_direction=True):

        hdist = self._range * self._zoom * cos(self._elevation)
        vdist = self._range * self._zoom * sin(self._elevation)

        if is_direction:
            amount = amount/abs(amount) * self._speed * get_dt()

        new_vdist = vdist + amount
        new_elevation = _clamp_elev(atan2(new_vdist, hdist))
        r = sqrt(hdist*hdist + new_vdist*new_vdist)
        new_zoom = _clamp_zoom(r / self._range)
        
        if new_elevation != self._elevation and new_zoom != self._zoom:
            print r, new_zoom
            self._elevation = new_elevation
            self._zoom = new_zoom
            self._dirty = True

    def get_position(self):
        """ Retrieve the camera's position vector. """

        return self._position

    position = property(get_position, doc=get_position.__doc__)

    def get_target_pos(self):
        """ Retrieve the position of the camera's target. """

        return self._target
    
    target_pos = property(get_target_pos, doc=get_target_pos.__doc__)

    def get_matrix(self):
        """ Retrieve the camera's tview matrix. """
        
        if self._dirty:
            self.update()
        return self._matrix

    view = property(get_matrix, doc="Retrieve the camera's view matrix.")
    
    def get_elevation(self):
        """ Retrieve the angle about the target's local horizontal. """
        
        return self._elevation

    elevation = property(get_elevation, 
                         "Retrieve the angle about the target's local horizontal")
    
    def get_zenith(self):
        """ Retrieve the angle about the target's local vertical. """
        
        return PI_2 - self._elevation
    
    
    
