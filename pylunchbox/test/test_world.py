import glfw
import random
import os
import inspect
from time import time as _time

from pylunchbox import core
from pylunchbox.core import device, modeling, maths
from pylunchbox.core.main import MainApp
from pylunchbox.core.world import World
from pylunchbox.core.camera import Camera
from pylunchbox.core.glutils import *
from pylunchbox.core.text import TextManager, Text, Font
from pylunchbox.core.texture import TextureManager, TextureBuilder
from pylunchbox.core.resource import ResourceManager
from sample.input import InputSystem
from sample.blocks import BlockGenerator

CAMERA_MSG = "Camera Position: {:.2f}, {:.2f}, {:.2f}"
CAMTGT_MSG = "Camera Target: {:.2f}, {:.2f}, {:.2f}"

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
        cls.res = ResourceManager()
        cls.world = World(cls)
        cls.tex_mgr = TextureManager(cls)
        cls.txt_mgr = TextManager(cls)
        init_world(cls)
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
            TEXT_CAMERA.set_text(CAMERA_MSG.format(*cls.camera.position))
            TEXT_CAMTGT.set_text(CAMTGT_MSG.format(*cls.camera.target_pos))

            #print device.Time.get_fps()
            if keyboard.is_key_pressed(glfw.KEY_ESCAPE):
                print "Bye Bye!"
                device.request_window_closure()
            cls.renderer.render()
            cls.txt_mgr.render()
            device.swap()
        cls.destroy()
    
    @classmethod
    def destroy(cls):
        cls.txt_mgr.destroy()
        cls.tex_mgr.destroy()
        cls.world.batch.destroy()
        #cls.world.shader.destroy()
        core.device.shutdown()

TEST_TEXTURE = None
TEXT_CAMERA = None
TEXT_CAMTGT = None

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

def init_world(app):

    global TEST_TEXTURE, TEXT_CAMERA, TEXT_CAMTGT

    start = _time()
    world = app.world
    path = app.path

    # Load the test mesh
    filename = path + "/res/cube.obj"
    #filename = path + "/res/stall.obj"
    #filename = path + "/res/birch1.obj"
    #filename = path + "/res/dragon.obj"
    cube_mesh = world.loader.load_mesh("Cube", filename)
    
    # Load test texture
    filename = path + "/res/textures/wildtextures-seamless-paper-texture.jpg"
    filename = path + "/res/textures/some_green.png"
    filename = path + "/res/textures/grid1.png"
    filename = path + "/res/textures/test_16-16.png"
    #filename = "../res/MSX2-palette.png"
    image = app.tex_mgr.load_image("TEST", filename, "PNG-PIL")
    builder = TextureBuilder().set_wrapped('repeat')
    TEST_TEXTURE = app.tex_mgr.load_texture("TEST", image, builder)
    
    # Create the first entity
    cube_entity = world.em.create()
    cube_bundle_comp = world.cm.create(cube_entity.get_id(), modeling.MeshComponent)
    cube_bundle_comp.bundle = cube_mesh
    cube_transform = world.cm.create(cube_entity.get_id(), maths.Transformation)
    cube_transform.set_position(maths.Vector3f(-2, 2, -2))
    cube_transform.set_scale(maths.Vector3f(2, 1, .5))
    world.batch.add(cube_entity)
    
    # Create the second entity
    cube_entity = world.em.create()
    cube_bundle_comp = world.cm.create(cube_entity.get_id(), modeling.MeshComponent)
    cube_bundle_comp.bundle = cube_mesh
    cube_transform = world.cm.create(cube_entity.get_id(), maths.Transformation)
    cube_transform.set_position(maths.Vector3f(-3, 2, -4))
    cube_transform.set_rotation(maths.Vector3f(20, 30, -40))
    cube_transform.set_scale(maths.Vector3f(0.75, 1.5, 2.0))
    world.batch.add(cube_entity)

    for i in xrange(6):
        for j in xrange(1):
            cube_entity = world.em.create()
            cube_bundle_comp = world.cm.create(cube_entity.get_id(), modeling.MeshComponent)
            cube_bundle_comp.bundle = cube_mesh
            cube_transform = world.cm.create(cube_entity.get_id(), maths.Transformation)
            cube_transform.set_position(maths.Vector3f(i, 0, j)) #random.uniform(-.2,.2)
            #cube_transform.set_scale(maths.Vector3f(0.9, 0.9, 0.9))
            #cube_transform.set_rotation(maths.Vector3f(random.uniform(0,60), random.uniform(0,60), random.uniform(0,60)))
            world.batch.add(cube_entity)
    
    # Try loading some text
    font1 = app.txt_mgr.load_font("segoeUI")
    font2 = app.txt_mgr.load_font("consolas_asc")
    TEXT_CAMERA = Text("Camera Position: 4, 3, 1", font2, 1.0, Vector2f(0.0, 0.0), 1.0)
    app.txt_mgr.add_text(TEXT_CAMERA)
    TEXT_CAMTGT = Text("Target Position: 0, 1, 0", font2, 1.0, Vector2f(0.0, TEXT_CAMERA.mesh_data.height), 1.0)
    app.txt_mgr.add_text(TEXT_CAMTGT)

    gen = BlockGenerator(app, cube_mesh)

    filename = path + "/res/textures/test_16-16.png"
    image = app.tex_mgr.load_image("atlas_test", filename)
    builder = TextureBuilder().set_wrapped('repeat')
    atlas = app.tex_mgr.load_texture_atlas("atlas_test", image, builder, 16, 16)

    block1 = gen.create_block()
    block1.trans.set_position(maths.Vector3f(5, 5, 5))
    #block1.trans.set_rotation(maths.Vector3f(45, 45, 45))
    gen.set_face_texture(block1, 0, atlas, 2, 0)
    gen.set_face_texture(block1, 1, atlas, 1, 0)
    gen.set_face_texture(block1, 2, atlas, 2, 0)
    gen.set_face_texture(block1, 3, atlas, 2, 0)
    gen.set_face_texture(block1, 4, atlas, 0, 0)
    gen.set_face_texture(block1, 5, atlas, 2, 0)
    gen.load_block(block1)

    done = _time()

    print done - start

if __name__ == "__main__":
    
    WorldTestApp.main()

    
        
    
