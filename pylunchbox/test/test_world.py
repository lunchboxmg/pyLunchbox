from pylunchbox import core
from pylunchbox.core.main import MainApp
from pylunchbox.core.world import World


class WorldTestApp(MainApp):
    
    @classmethod
    def init(cls):
        
        core.device.init(cls, cls.get_full_title())
        cls.world = World()
    
    @classmethod
    def destroy(cls):
        cls.world.batch.destroy()
        core.device.shutdown()

if __name__ == "__main__":
    
    WorldTestApp.main()
    
        
    
