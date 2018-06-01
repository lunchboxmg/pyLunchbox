import glfw
import random
import os
import inspect

from pylunchbox import core
from pylunchbox.core import device, modeling, maths
from pylunchbox.core.main import MainApp
from pylunchbox.core.world import World
from pylunchbox.core.camera import Camera
from pylunchbox.core.glutils import *
from sample.input import InputSystem

class WorldTestApp(MainApp):
    
    @classmethod
    def init(cls):

        # Get the proper path
        filename = inspect.getframeinfo(inspect.currentframe()).filename
        this_path = os.path.dirname(os.path.abspath(filename))
        path_parts = this_path.split("\\")
        while path_parts[-1] != "pylunchbox":
            path_parts.pop()
        cls.path = "/".join(path_parts)

        # Initialize parts        
        device.init(cls, cls.get_full_title())
        cls.world = World()
        init_world(cls.world)
        cls.camera = Camera(cls.world)
        cls.input = InputSystem(cls)
        cls.renderer = TestRenderer(cls)

    @classmethod
    def main(cls):
        """ Main function to run the app. """

        cls.init()
        keyboard = device.keyboard
        while device.is_window_open():
            device.update()
            cls.input.process()
            cls.camera.update()
            #print device.Time.get_fps()
            if keyboard.is_key_pressed(glfw.KEY_ESCAPE):
                print "Bye Bye!"
                device.request_window_closure()
            cls.renderer.render()
            device.swap()
        cls.destroy()
    
    @classmethod
    def destroy(cls):
        cls.world.batch.destroy()
        #cls.world.shader.destroy()
        core.device.shutdown()

TEST_TEXTURE = None

class TestShader(ShaderProgram):
    
    def __init__(self, name, vs, fs):
        super(TestShader, self).__init__(name, vs, fs)
        
        self.model = UniformMatrix4f("model")
        self.view = UniformMatrix4f("view")
        self.proj = UniformMatrix4f("proj")
        self.camera_pos = UniformVector3f("camera_pos")
        self.lights = UniformLights("lights")
        
        self.store_locations(self.model, self.view, self.proj, 
                             self.camera_pos, self.lights)

class TestRenderer(object):
    
    FOV = 60.0
    NEAR_PLANE = 0.1
    FAR_PLANE = 100.0
    
    def __init__(self, app):
        
        self.world = app.world
        self.camera = app.camera
        proj = maths.perspective_RH(60.0, device.window.get_aspect(), 0.1, 1000.0)
        self.shader = shader = TestShader("Test",
                                 app.path + "/res/shaders/basic8.vs",
                                 app.path + "/res/shaders/basic8.fs")

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
        r = 5
        w = 0.25
        x = r * maths.cos(w*t)
        z = r * maths.sin(w*t)

        self.camera_pos = cam = maths.Vector3f(10+x, 4, 10+z)
        self.shader.camera_pos.load(*cam)
        view = maths.look_at_RH(self.camera_pos, 
                                maths.Vector3f(10, 0, 10),
                                maths.Vector3f(0, 1, 0))
        self.shader.view.load(self.camera.get_matrix())
        model = maths.identity(4, dtype=maths.FLOAT32)
        #model = maths.translate(model, maths.Vector3f(5, 0, 0))
        #model = maths.rotate(model, -t, maths.Vector3f(1, 0, 0))
        #model = maths.scale(model, maths.Vector3f(maths.sin(w*w*t), 1, 1))
        self.shader.model.load(model)
        size = self.world.batch._manager._index_last

        vao = self.world.batch.get_vao()
        vao.bind()
        vao.enable(3)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, TEST_TEXTURE._id)
        glDrawArrays(GL_TRIANGLES, 0, size)

        vao.disable()
        vao.unbind()
        
        self.shader.stop()

def init_world(world):

    global TEST_TEXTURE
    path = WorldTestApp.path

    # Load the test mesh
    filename = path + "/res/cube.obj"
    #filename = path + "res/stall.obj"
    #filename = path + "/res/birch1.obj"
    #filename = path + "/res/dragon.obj"
    cube_mesh = world.loader.load_mesh("Cube", filename)
    
    # Load test texture
    filename = path + "/res/textures/wildtextures-seamless-paper-texture.jpg"
    filename = path + "/res/textures/some_green.png"
    filename = path + "/res/textures/grid1.png"
    #filename = "../res/MSX2-palette.png"
    TEST_TEXTURE = world.tm.load(filename)
    
    # Create the first entity
    cube_entity = world.em.create()
    cube_bundle_comp = world.cm.create(cube_entity.get_id(), modeling.MeshComponent)
    cube_bundle_comp.bundle = cube_mesh
    cube_transform = world.cm.create(cube_entity.get_id(), maths.Transformation)
    cube_transform.set_position(maths.Vector3f(0, 0, 0))
    cube_transform.set_scale(maths.Vector3f(2, 1, .5))
    world.batch.add(cube_entity)
    
    # Create the second entity
    cube_entity = world.em.create()
    cube_bundle_comp = world.cm.create(cube_entity.get_id(), modeling.MeshComponent)
    cube_bundle_comp.bundle = cube_mesh
    cube_transform = world.cm.create(cube_entity.get_id(), maths.Transformation)
    cube_transform.set_position(maths.Vector3f(0, 0, 1))
    cube_transform.set_rotation(maths.Vector3f(20, 30, -40))
    cube_transform.set_scale(maths.Vector3f(0.75, 1.5, 2.0))
    world.batch.add(cube_entity)

    for i in xrange(10):
        for j in xrange(10):
            cube_entity = world.em.create()
            cube_bundle_comp = world.cm.create(cube_entity.get_id(), modeling.MeshComponent)
            cube_bundle_comp.bundle = cube_mesh
            cube_transform = world.cm.create(cube_entity.get_id(), maths.Transformation)
            cube_transform.set_position(maths.Vector3f(i, random.uniform(-.2,.2), j)) #
            #cube_transform.set_scale(maths.Vector3f(0.05, 0.05, 0.05))
            #cube_transform.set_rotation(maths.Vector3f(random.uniform(0,60), random.uniform(0,60), random.uniform(0,60)))
            world.batch.add(cube_entity)
            
if __name__ == "__main__":
    
    WorldTestApp.main()

    
        
    
