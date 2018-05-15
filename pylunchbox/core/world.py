__author__ = "lunchboxmg"

import ecs
import memory
import modeling
import glutils
import device
import maths
import texture

from glutils import *

class World(object):
    """ The World class is the centralized class for storing data that
    currently apart of the main system. """

    def __init__(self):

        # Initialize the ECS architecture for this world
        self.em = ecs.EntityManager(self)
        self.cm = ecs.ComponentManager(self)
        self.tm = texture.TextureManager(self)

        self.batch = memory.StaticBatch(memory.MemoryManager(300000), self)
        self.loader = modeling.ModelLoader()
        
        filename = "../res/cube.obj"
        #filename = "../res/stall.obj"
        #filename = "../res/birch1.obj"
        #filename = "../res/dragon.obj"
        self.cube = self.loader.load_mesh("Cube", filename)
        
        e_cube = self.em.create()
        m_cube = self.cm.create(e_cube.get_id(), modeling.MeshComponent)
        m_cube.bundle = self.cube
        print m_cube.bundle
        
        self.batch.add(e_cube)

        self.tex_test = self.tm.load("../res/textures/wildtextures-seamless-paper-texture.jpg")
        
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
        self.camera_pos = glutils.UniformVector3f("camera_pos")
        
        self.store_locations(self.model, self.view, self.proj, 
                             self.camera_pos)

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
        #glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        self.shader.start()
        
        t = device.Time.get_time_current()
        r = 2
        w = 0.5
        x = r * maths.cos(w*t)
        z = r * maths.sin(w*t)

        self.camera_pos = cam = maths.Vector3f(x, 1, z)
        self.shader.camera_pos.load(*cam)
        view = maths.look_at_RH(self.camera_pos, 
                                maths.Vector3f(0, 0, 0),
                                maths.Vector3f(0, 1, 0))
        self.shader.view.load(view)
        model = maths.identity(4, dtype=maths.FLOAT32)
        #model = maths.translate(model, maths.Vector3f(5, 0, 0))
        #model = maths.rotate(model, -t, maths.Vector3f(1, 0, 0))
        #model = maths.scale(model, maths.Vector3f(maths.sin(w*w*t), 1, 1))
        self.shader.model.load(model)
        size = self.world.batch._manager._index_last

        vao = self.world.batch.get_vao()
        vao.bind()
        vao.enable(3)
        glutils.glActiveTexture(glutils.GL_TEXTURE0)
        glutils.glBindTexture(glutils.GL_TEXTURE_2D, self.world.tex_test._id)
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
    

