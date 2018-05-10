__author__ = "lunchboxmg"

import ecs
import memory
import modeling
import glutils
import device
import maths

from glutils import *

class World(object):
    """ The World class is the centralized class for storing data that
    currently apart of the main system. """

    def __init__(self):

        # Initialize the ECS architecture for this world
        self.em = ecs.EntityManager(self)
        self.cm = ecs.ComponentManager(self)

        self.batch = memory.StaticBatch(memory.MemoryManager(300000), self)
        self.loader = modeling.ModelLoader()
        
        #filename = "../res/cube.obj"
        filename = "../res/stall.obj"
        filename = "../res/birch1.obj"
        filename = "../res/dragon.obj"
        self.cube = self.loader.load_mesh("Cube", filename)
        
        e_cube = self.em.create()
        m_cube = self.cm.create(e_cube.get_id(), modeling.MeshComponent)
        m_cube.bundle = self.cube
        print m_cube.bundle
        
        self.batch.add(e_cube)
        
        self.shader = TestShader("Test",
                                 "../res/shaders/basic8.vs",
                                 "../res/shaders/basic8.fs")
        
        self.renderer = TestRenderer(self)

class TestShader(glutils.ShaderProgram):
    
    def __init__(self, name, vs, fs):
        super(TestShader, self).__init__(name, vs, fs)
        
        self.model = glutils.UniformMatrix4f("model")
        self.view = glutils.UniformMatrix4f("view")
        self.proj = glutils.UniformMatrix4f("proj")
        
        self.store_locations(self.model, self.view, self.proj)

class TestRenderer(object):
    
    FOV = 60.0
    NEAR_PLANE = 0.1
    FAR_PLANE = 100.0
    
    def __init__(self, world):
        
        self.world = world
        proj = maths.perspective_RH(60.0, device.window.get_aspect(), 0.1, 1000.0)
        self.shader = shader = world.shader
        shader.start()
        shader.proj.load(proj)
        shader.stop()
        
    def render(self):
        
        glEnable(GL_DEPTH_TEST)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        glClearColor(0.2, 0.2, 0.2, 1.0)
        glCullFace(GL_FRONT_AND_BACK)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        self.shader.start()
        
        t = device.Time.get_time_current()
        r = 20
        w = 0.5
        x = r * maths.cos(w*t)
        z = r * maths.sin(w*t)

        view = maths.look_at_RH(maths.Vector3f(x, 15, z), 
                                maths.Vector3f(0, 10, 0),
                                maths.Vector3f(0, 1, 0))
        self.shader.view.load(view)
        self.shader.model.load(maths.identity(4, dtype=maths.FLOAT32))
        size = self.world.batch._manager._index_last

        vao = self.world.batch.get_vao()
        vao.bind()
        vao.enable(3)
        glutils.glDrawArrays(glutils.GL_TRIANGLES, 0, size)
        vao.disable()
        vao.unbind()
        
        self.shader.stop()

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
    

