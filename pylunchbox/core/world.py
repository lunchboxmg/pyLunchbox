__author__ = "lunchboxmg"

import ecs
import memory
import modeling

class World(object):
    """ The World class is the centralized class for storing data that
    currently apart of the main system. """

    def __init__(self):

        self.batch = memory.StaticBatch(memory.MemoryManager(1000))
        self.loader = modeling.ModelLoader()
        self.cube = self.loader.load_mesh("Cube", "../res/cube.obj")
        
        self.em = ecs.EntityManager(self)
        self.cm = ecs.ComponentManager(self)

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

