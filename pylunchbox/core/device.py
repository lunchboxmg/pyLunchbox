""" The device module handles events pertaining to the input/output devices.

Classes:
========
* Window: Handles interacting the with the device context.
* Keyboard: Handles user keyboard interactions.
* Mouse: Handles user mouse interactions.
* DeviceTime: Used to keep track of the timing of the system.
* DeviceManager: Manages all the above classes together.

This module contains an internal DeviceManager instance that instances the 
other device classes so that they may be imported by various other modules.
"""
import glfw
from OpenGL.GL import *

__author__ = "lunchboxmg"

class Window(object):
    """ The Window class is repsonsible for displaying the results of the GPU
    rendering to a window handle. """

    def __init__(self, title="Test", width=1280, height=720):
        """ Constructor.

        Parameters:
        ===========
        * title (:obj:`string`): Text to display in the window's titlebar.
        * width (:obj:`int`): Width of the window in pixels.
        * height (:obj:`int`): Height of the window in pixels.
        """

        self._instance = None
        self.set_dimensions(width, height)
        self._title = title
        self.__create_window()

    def __create_window(self):
        """ Internal function repsonsible for creating the window's
        handle/instance. """

        # Set window context prarameters
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.RESIZABLE, GL_FALSE)

        self._instance = glfw.create_window(self._width, self._height, self._title, None, None)

        if not self._instance:
            print "ERROR: Window creation failed!"
            glfw.terminate()
            exit(-1)

        # Create the context
        glfw.make_context_current(self._instance)
        #glfw.swap_interval(0) # VYSNC
        glViewport(0, 0, self._width, self._height)
        self._close_requested = False

    def set_dimensions(self, width, height):
        """ Set the dimensions of the window. """

        self._width = width
        self._height = height
        self._aspect = float(width) / float(height)
        # TODO: Trigger window resizing

    def swap(self):
        """ Swap out the display buffer with the back buffer. """

        glfw.swap_buffers(self._instance)

    def close(self):
        """ Tell the system to close this window. """

        glfw.set_window_should_close(self._instance, GL_TRUE)

    def request_closure(self):
        """ Request that this window be closed. """

        self._close_requested = True

    def is_close_requested(self):
        """ Determine if a closure has been requested for this window. """

        return self._close_requested

    def is_open(self):
        """ Check if GLFW hasn't close this window of that the user hasn't
        requested that this window be closed. """

        return not glfw.window_should_close(self._instance) and not self._close_requested

    def destroy(self):
        """ Kill this window's handle. """

        glfw.destroy_window(self._instance)

    def get_instance(self):
        """ Retrieve the window's instance handle. """

        return self._instance

    def get_title(self):
        """ Retrieve the window's title string. """

        return self._title

    def get_width(self):
        """ Retrieve the width of this window in pixels. """

        return self._width

    def get_height(self):
        """ Retrieve the height of this window in pixels. """

        return self._height

    def get_aspect(self):
        """ Retrieve this window's aspect ratio. """

        return self._aspect

class Keyboard(object):
    """ The Keyboard class if repsonsible for keeping track of the status of
    keyboard keys each frame. """

    def __init__(self, window_instance):
        """ Constructor.

        Parameters:
        ===========
        * window_instance (:obj:`int`): Reference to the current window used to
          attach the keyboard event handler functions to.
        """

        self._keys_pressed = set()
        self._keys_held = set()
        self._keys_released = set()
        self._mod_bitfield = 0

        glfw.set_key_callback(window_instance, self.handle)

    def update(self):
        """ Clear internal store of keys that were pressed and release during
        the previous frame. """

        self._keys_pressed.clear()
        self._keys_released.clear()
        self._mod_bitfield = 0

    def handle(self, window, key, scancode, action, mods):
        """ Event handler for when the user interacts with this keyboard. """

        # During testing, hard assign Ctrl+C to force close the window
        if key == glfw.KEY_C and mods & glfw.MOD_CONTROL:
            glfw.set_window_should_close(window, GL_TRUE)

        # Save the keystate
        if 0 <= key <= 1024:
            if action == glfw.PRESS:
                if key not in self._keys_pressed:
                    self._keys_pressed.add(key)
                    self._keys_held.add(key)
            if action == glfw.RELEASE:
                self._keys_held.remove(key)
                self._keys_released.add(key)
            self._mod_bitfield = mods

    def is_key_pressed(self, key):
        """ Determine if the input `key` was pressed. """

        return key in self._keys_pressed

    def is_key_held(self, key):
        """ Determine if the input `key` is being held down. """

        return key in self._keys_held

    def is_key_released(self, key):
        """" Determine if the input `key` was released. """

        return key in self._keys_released

    def is_mod_pressed(self, mod):
        """ Determines in the input `mod`ifier key was held down during the
        last keystroke. """

        return self._mod_bitfield & mod

    def iter_keys_pressed(self):
        """ Retrieve an iterator of the keys pressed. """

        return iter(self._keys_pressed)

    def iter_keys_held(self):
        """ Retrieve an iterator of the keys being held down. """

        return iter(self._keys_held)

    def iter_keys_release(self):
        """ Retrieve an iterator of the keys that were released. """

        return iter(self._keys_released)

class Mouse(object):
    """ The Mouse class is repsonsible for handling mouse iteractions within
    the assigned Window. """

    def __init__(self, window_instance):
        """ Constructor.

        Parameters:
        ===========
        * window_instance (:obj:`int`): Reference to the current window used to
          attach the keyboard event handler functions to.
        """

        # Button state collections
        self._buttons_pressed = set()
        self._buttons_held = set()
        self._buttons_released = set()
        self._mod_bitfield = 0

        # Mouse scroll wheel offsets
        self._scroll_offset_x = 0
        self._scroll_offset_y = 0

        # Mouse positioning parameters
        self._x = self._y = self._dx = self._dy = 0.0

        # Set window callback functions for mouse
        self._window = window_instance
        glfw.set_mouse_button_callback(window_instance, self.handle_button)
        glfw.set_scroll_callback(window_instance, self.handle_scroll)

    def update(self):
        """ Update the mouse state for this frame. """

        # Reset button state collections
        self._buttons_pressed.clear()
        self._buttons_released.clear()
        self._bit_modfield = 0

        # Update mouse positioning
        new_x, new_y = glfw.get_window_pos(self._window)
        self._dx = new_x - self._x
        self._dy = new_y - self._y
        self._x = new_x
        self._y = new_y

        # Reset scroll wheel offsets
        self._scroll_offset_x = 0
        self._scroll_offset_y = 0

    def handle_button(self, window, button, action, mods):
        """ Event handler for when the user interacts with the mouse buttons. """

        if 0 <= button <= glfw.MOUSE_BUTTON_LAST:
            if action == glfw.PRESS:
                if button not in self._buttons_held:
                    self._buttons_pressed.add(button)
                    self._buttons_held.add(button)
            if action == glfw.RELEASE:
                self._buttons_held.remove(button)
                self._buttons_released.add(button)
            self._mod_bitfield = mods

    def handle_scroll(self, window, xoffset, yoffset):
        """ Event handler for when the user interacts with the mouse's
        scroll wheel. """

        self._scroll_offset_x = xoffset
        self._scroll_offset_y = yoffset

    def is_button_pressed(self, button):
        """ Determine if the input `button` was pressed. """

        return button in self._buttons_pressed

    def is_button_held(self, button):
        """ Determine if the input `button` is being held down. """

        return button in self._buttons_held

    def is_button_released(self, button):
        """ Determine if the input `button` was released. """

        return button in self._buttons_released

    def is_mod_pressed(self, mod):
        """ Determine if the input `mod`ifier key was pressed in conjuction
        with the last keystroke. """

        return self._mod_bitfield & mod

    def did_mouse_move(self):
        """ Determine if the mouse moved from its position between frames. """

        return self._dx != 0.0 or self._dy != 0.0

    def did_mouse_scroll(self):
        """ Determine if the mouse wheel was scrolled this frame. """

        return self._scroll_offset_x != 0.0 or self._scroll_offset_y != 0.0

    def get_x(self):
        """ Retrieve the current `x`-component of the mouse's current position. """

        return self._x

    def get_y(self):
        """ Retrieve the current 'y'-component of the mouse's current position. """

        return self._y

    def get_position(self):
        """ Retrieve the current x, y components of the mouse's position. """

        return self._x, self._y

    def get_dx(self):
        """ Retrieve the amount of distance the mouse moved in the x-direction. """

        return self._dx

    def get_dy(self):
        """ Retrieve the amount of distance the mouse moved in the y-direction. """

        return self._dy

    def get_offsets(self):
        """ Retrieve the offset of the mouse's current position from it's
        position during the previous frame. """

        return self._dx, self._dy

    def get_scroll_x(self):
        """ Retrieve the amount this mouse's scroll wheel moved in the x-direction. """

        return self._scroll_offset_x

    def get_scroll_y(self):
        """ Retrieve the amount this mouse's scroll wheel moved in the y-direction. """

        return self._scroll_offset_y

    def get_scroll_offsets(self):
        """ Retreive the amount this mouse's scroll wheel was moved in both x,y
        directions. """

        return self._scroll_offset_x, self._scroll_offset_y

class DeviceTime(object):
    """ The DeviceTime class is responsible for keeping the timing of the
    main device system. """

    def __init__(self):

        self._time_current = self._time_previous = self.__get_time()
        self._time_delta = self._frame_count = self._fps = 0

    def update(self):
        """ Update the timing between frames. """

        now = self.__get_time()
        self._time_delta = now - self._time_current
        self._time_previous = self._time_current
        self._time_current = now
        self._fps = 1.0 / self._time_delta
        self._frame_count += 1

    def __get_time(self):
        """ Internal function to retrieve the GPU's current time. """

        return glfw.get_time()

    def get_time_current(self):
        """ Retrieve the current time. """

        return self._time_current

    def get_time_delta(self):
        """ Retrieve the time difference between the current and last frame. """

        return self._time_delta

    def get_dt(self):
        """ Retrieve the time difference between the current and last frame. """

        return self._time_delta

    def get_fps(self):
        """ Retrieve the current frames per second. """

        return self._fps

    def get_frame_count(self):
        """ Retrieve the number of frames rendered. """

        return self._frame_count

class DeviceManager(object):
    """ The DeviceManger is a helper class that hold the device class instances
    so that they may be shared between mutilple files. """

    def __init__(self):
        """ Constructor. """

        self.app = None
        self.window = None
        self.mouse = None
        self.keyboard = None
        self.timing = None

    def init(self, app, title="Test", width=1280, height=720):
        """ Initialize this device manager.

        Parameters:
        ===========
        * app (:obj:`MainApp`): Reference to the main application.
        * title (:obj:`string`): Text to display in the window's titlebar.
        * width (:obj:`int`): Width of the window in pixels.
        * height (:obj:`int`): Height of the window in pixels.

        NOTE: This should be called immediately as soon as the referenced
        `MainApp` is initalized.
        """

        global window, keyboard, mouse, Time

        self._app = app

        # Intialize GLFW
        if not glfw.init():
            print "ERROR: GLFW could not be initialized."
            exit(-1)

        self.window = window = Window(title, width, height)
        self.mouse = mouse = Mouse(window.get_instance())
        self.keyboard = keyboard = Keyboard(window.get_instance())

        # Set time
        self.timing = Time = DeviceTime()

    def update(self):
        """ Update the attached devices. """

        # Update the devices and handle device events
        try:
            self.keyboard.update()
            self.mouse.update()
            glfw.poll_events()
            self.timing.update()
        except Exception as e:
            print "ERROR: Device manager could not update ...\n\t{:s}".format(e)
            self.shutdown()

    def shutdown(self):
        """ Shutdown the device manager. """

        self.window.close()
        self.window.destroy()
        glfw.terminate()


_DEVICE = DeviceManager() # Local reference

# Localized function shortcuts
init = _DEVICE.init
update = _DEVICE.update
shutdown = _DEVICE.shutdown

# Localized referencing shortcuts
window = _DEVICE.window
keyboard =_DEVICE.keyboard
mouse = _DEVICE.mouse
Time = _DEVICE.timing # TODO: May change to help not confuse with system time module

def is_window_open():
    """ Determine if the window is currently open. """

    return window.is_open()

def request_window_closure():
    """ Request that the window being closed. """

    window.request_closure()

def swap():
    """ Swap window buffers. """

    window.swap()

def get_dt():
    """ Get the time difference between the previous and this frame. """
    
    return Time.get_dt()