__author__ = "lunchboxmg"

import ecs
import memory
import modeling

class World(object):
    """ The World class is the centralized class for storing data that
    currently apart of the main system. """

    def __init__(self):

        # Initialize the ECS architecture for this world
        self.em = ecs.EntityManager(self)
        self.cm = ecs.ComponentManager(self)

        self.batch = memory.StaticBatch(memory.MemoryManager(1000), self)
        self.loader = modeling.ModelLoader()
        
        filename = "../res/cube.obj"
        #filename = "../res/stall.obj"
        #filename = "../res/dragon.obj"
        self.cube = self.loader.load_mesh("Cube", filename)
        
        e_cube = self.em.create()
        m_cube = self.cm.create(e_cube.get_id(), modeling.MeshComponent)
        m_cube.bundle = self.cube
        print m_cube.bundle
        
        self.batch.add(e_cube)
        

if __name__ == "__main__":
    
    world = World()
    print world.cube['cube'] # <-- has mesh data, need to add to a component
    
    entity = world.em.create()
    print entity
    
    comp = world.cm.create(entity.get_id(), modeling.MeshComponent)
    print comp
    comp.bundle = world.cube["cube"]
    print comp.bundle
    
    # Now we need a way to load the mesh from the batch into the gpu
    print world.cm.get_type_for(modeling.MeshComponent)
    world.batch.destroy()
    

