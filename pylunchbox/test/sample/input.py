from functools import partial

#import pylunchbox.core.device as device
from pylunchbox.core.camera import DIRECTION
from pylunchbox.core.constants import *
from pylunchbox.core import device

class KeyBind(object):

    def __init__(self, command, key=None, mod1=None, mod2=None):

        self.command = command
        self.key = key
        self.mod1 = mod1
        self.mod2 = mod2

class KeySettings(object):
    
    def __init__(self):

        self.commands = c = dict()
        self.move_left  = c["MOVE.LEFT"]  = KeyBind("MOVE.LEFT", GLFW_KEY_Q)
        self.move_right = c["MOVE.RIGHT"] = KeyBind("MOVE.RIGHT", GLFW_KEY_E)
        self.move_front = c["MOVE.FRONT"] = KeyBind("MOVE.FRONT", GLFW_KEY_W)
        self.move_back  = c["MOVE.BACK"]  = KeyBind("MOVE.BACK", GLFW_KEY_S)
        self.move_up    = c["MOVE.UP"]    = KeyBind("MOVE.UP", GLFW_KEY_SPACE)
        self.move_down  = c["MOVE.DOWN"]  = KeyBind("MOVE.DOWN", GLFW_KEY_LEFT_SHIFT)
        self.turn_left  = c["TURN.LEFT"]  = KeyBind("TURN.LEFT", GLFW_KEY_A)
        self.turn_right = c["TURN.RIGHT"] = KeyBind("TURN.RIGHT", GLFW_KEY_D)
        self.view_up    = c["VIEW.UP"]    = KeyBind("VIEW.UP", GLFW_KEY_R)
        self.view_down  = c["VIEW.DOWN"]  = KeyBind("VIEW.DOWN", GLFW_KEY_F)
        self.zoom_in    = c["ZOOM.IN"]    = KeyBind("ZOOM.IN", GLFW_KEY_HOME)
        self.zoom_out   = c["ZOOM.OUT"]   = KeyBind("ZOOM.OUT", GLFW_KEY_END)
        self.move_up1   = c["MOVE.UP1"]   = KeyBind("MOVE.UP1", GLFW_KEY_T)
        self.move_down1 = c["MOVE.DOWN1"] = KeyBind("MOVE.DOWN1", GLFW_KEY_G)

class InputSystem(object):
    
    def __init__(self, world):
        
        self.world = world
        self._keyboard = device.keyboard
        self._mouse = device.mouse
        self._keybinds = KeySettings()

    def process(self):

        keyboard = self._keyboard
        mouse = self._mouse
        keybinds = self._keybinds

        # Camera movement
        camera = self.world.camera
        if keyboard.is_key_held(keybinds.move_front.key):
            camera.move_target(DIRECTION.FORWARD)
        if keyboard.is_key_held(keybinds.move_back.key):
            camera.move_target(DIRECTION.BACKWARD)
        if keyboard.is_key_held(keybinds.move_left.key):
            camera.move_target(DIRECTION.LEFT)
        if keyboard.is_key_held(keybinds.move_right.key):
            camera.move_target(DIRECTION.RIGHT)
        if keyboard.is_key_held(keybinds.move_up.key):
            camera.move_target(DIRECTION.UP)
        if keyboard.is_key_held(keybinds.move_down.key):
            camera.move_target(DIRECTION.DOWN)
        if keyboard.is_key_held(keybinds.turn_left.key):
            camera.rotate(1)
        if keyboard.is_key_held(keybinds.turn_right.key):
            camera.rotate(-1)
        if keyboard.is_key_held(keybinds.view_up.key):
            camera.rotate(pitch=1)
        if keyboard.is_key_held(keybinds.view_down.key):
            camera.rotate(pitch=-1)
        if keyboard.is_key_held(keybinds.zoom_in.key):
            camera.zoom(-1)
        if keyboard.is_key_held(keybinds.zoom_out.key):
            camera.zoom(1)
        if keyboard.is_key_held(keybinds.move_up1.key):
            camera.move_vertical(1)
        if keyboard.is_key_held(keybinds.move_down1.key):
            camera.move_vertical(-1)

    def move_camera(self, direction):

        self.world.camera(direction)