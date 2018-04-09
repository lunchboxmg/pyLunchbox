import glfw
from OpenGL.GL import *

class _Window(object):

    def __init__(self):

        self._instance = None
        self._width = 0
        self._height = 0
        self._aspect = 0

    def create(self, title, width, height):

        # Set window context prarameters
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.RESIZABLE, GL_FALSE)

        self._instance = glfw.create_window(width, height, title, None, None)

        if not self.instance:
            print "ERROR: Window creation failed!"
            glfw.terminate()
            return False

        # Set local parameters
        self._width = width
        self._height = height
        self._aspect = float(width)/height

        # Create the context
        cls.make_context_current(self._instance)
        #glfw.swap_interval(0) # VYSNC
        glViewport(0, 0, width, height)

        return True

    def get_instance(self): return self._instance

class Keyboard(Object):
    pass

class Mouse(Object):
    pass

class DeviceManager(object):

    def __init__(self, app):

        self.app = app
        self.window = None
        self.mouse = None
        self.keyboard = None

    def create_window(self, title="Test", width=1080, height=720):

        self.window_class = _Window()
        self.window = self.window_class.create()
