from OpenGL.GL import *
from PIL import Image as _Image
from numpy import array as _array, uint8 as UINT8
import imageio

__author__ = "lunchboxmg"

class Texture2D(object):
    
    def __init__(self):
        
        self._id = glGenTextures(1)

    def bind(self):

        glBindTexture(GL_TEXTURE_2D, self._id)
    
    def unbind(self):
        
        glBindTexture(GL_TEXTURE_2D, 0)

    def clamp_edge(self):
        
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
	
    def repeat(self):
        
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    def filter_none(self):
        
        glParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

    def filter_linear(self):
        
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    def get_id(self):
        
        return self._id

class TextureAtlas(object) : pass

class TextureManager(object):
    
    def __init__(self, world):
        
        self.world = world
        self.textures = []
        
    def load(self, filename):
        
        data = imageio.imread(filename).astype(UINT8)
        h, w, _ = data.shape
        
        texture = Texture2D()
        texture.bind()
        texture.repeat()
        texture.filter_linear()
        
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, w, h, 0, GL_RGB, 
                     GL_UNSIGNED_BYTE, data.flatten())
        
        texture.unbind()
        
        self.textures.append(texture)
        return texture
        
        
if __name__ == "__main__":
    
    tm = TextureManager()
    tm.load("../res/white_crumpled_paper_texture.jpg")
        
