#import pylunchbox.core.device as device
from pylunchbox.core.camera import DIRECTION
from pylunchbox.core.constants import *
from pylunchbox.core import device

class InputMapItem(object):

    def __init__(self, command, key):
        
        self.command = command
        self.key = key

class InputMap(object):
    
    def __init__(self):
        
        self.commands = c = dict()
        self.move_left  = c["MOVE.LEFT"]  = InputMapItem("MOVE.LEFT", GLFW_KEY_Q)
        self.move_right = c["MOVE.RIGHT"] = InputMapItem("MOVE.RIGHT", GLFW_KEY_E)
        self.move_front = c["MOVE.FRONT"] = InputMapItem("MOVE.FRONT", GLFW_KEY_W)
        self.move_back  = c["MOVE.BACK"]  = InputMapItem("MOVE.BACK", GLFW_KEY_S)
        self.move_up    = c["MOVE.UP"]    = InputMapItem("MOVE.UP", GLFW_KEY_SPACE)
        self.move_down  = c["MOVE.DOWN"]  = InputMapItem("MOVE.DOWN", GLFW_KEY_LEFT_SHIFT)
        self.turn_left  = c["TURN.LEFT"]  = InputMapItem("TURN.LEFT", GLFW_KEY_A)
        self.turn_right = c["TURN.RIGHT"] = InputMapItem("TURN.RIGHT", GLFW_KEY_D)
        
class InputSystem(object):
    
    def __init__(self, world):
        
        self.world = world
        self._keyboard = device.keyboard
        self._input_map = InputMap()
        
    def process(self):

        keyboard = self._keyboard
        map_ = self._input_map
        
        if keyboard.is_key_held(map_.move_front.key):
            self.world.camera.move_target(DIRECTION.FORWARD)
        if keyboard.is_key_held(map_.move_back.key):
            self.world.camera.move_target(DIRECTION.BACKWARD)
        if keyboard.is_key_held(map_.move_left.key):
            self.world.camera.move_target(DIRECTION.LEFT)
        if keyboard.is_key_held(map_.move_right.key):
            self.world.camera.move_target(DIRECTION.RIGHT)
        if keyboard.is_key_held(map_.move_up.key):
            self.world.camera.move_target(DIRECTION.UP)
        if keyboard.is_key_held(map_.move_down.key):
            self.world.camera.move_target(DIRECTION.DOWN)
        if keyboard.is_key_held(map_.turn_left.key):
            self.world.camera.rotate(-1)
        if keyboard.is_key_held(map_.turn_right.key):
            self.world.camera.rotate(1)