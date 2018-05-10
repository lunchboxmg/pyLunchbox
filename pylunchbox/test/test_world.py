import glfw

from pylunchbox import core
from pylunchbox.core import device
from pylunchbox.core.main import MainApp
from pylunchbox.core.world import World
from pylunchbox.core import maths


class WorldTestApp(MainApp):
    
    @classmethod
    def init(cls):
        
        core.device.init(cls, cls.get_full_title())
        cls.world = World()

    @classmethod
    def main(cls):
        """ Main function to run the app. """

        cls.init()
        keyboard = device.keyboard
        while device.is_window_open():
            device.update()
            if keyboard.is_key_pressed(glfw.KEY_ESCAPE):
                print "Bye Bye!"
                device.request_window_closure()
            cls.world.renderer.render()
            device.swap()
        cls.destroy()
    
    @classmethod
    def destroy(cls):
        cls.world.batch.destroy()
        #cls.world.shader.destroy()
        core.device.shutdown()

        
        

if __name__ == "__main__":
    
    WorldTestApp.main()
    
        
    
