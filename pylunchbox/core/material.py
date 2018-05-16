""" The material module contains the structures for defining a GLSL matieral.

Classes
-------
ColorRGB (Vector3f)
    Represents a RGB color whose values range between 0.0 and 1.0
"""

from math import fabs
import numpy as np

__author__ = "lunchboxmg"

from maths import Vector3f, Vector4f, FLOAT32

class ColorRGB(np.ndarray):
    """ The ColorRBG class is a 3 dimensional vector representation of the 
    red, green, and blue components of a color. """
    
    _UNIT = FLOAT32
    
    def __new__(cls, r, g, b):
        """ Internal function produces a new ndarray casted to this class. """
        
        if r < 0.0 or r > 1.0:
            r = min(fabs(r)/255.0, 1.0)
        if g < 0.0 or g > 1.0:
            g = min(fabs(g)/255.0, 1.0)
        if b < 0.0 or b > 1.0:
            b = min(fabs(b)/255.0, 1.0)
        
        obj = np.asarray((r, g, b), FLOAT32).view(cls)
        return obj
    
    def __array_finalize__(self, obj):
        """ Internal function to finalize additional attribues added to the 
        base ndarray class. """
        
        if obj is None: return

    def get_r(self): 
        """ Retrieve the value of this color's RED component. """
        
        return self[0]

    def set_r(self, value): 
        """ Set the value of this color's RED component.
        
        NOTE: The value will be normalized if above 1. """
        
        if value < 0.0 or value > 1.0:
            value = min(fabs(value)/255.0, 1.0)
        self[0] = self._UNIT(value)

    r = property(get_r, set_r, doc="RED-Component of the Vector.")

    def get_g(self):
        """ Retrieve the value of this color's GREEN component. """
        
        return self[1]
    def set_g(self, value):
        """ Set the value of this color's GREEN component.
        
        NOTE: The value will be normalized if above 1. """

        if value < 0.0 or value > 1.0:
            value = min(fabs(value)/255.0, 1.0)
        self[1] = self._UNIT(value)

    g = property(get_g, set_g, doc="GREEN-Component of the Vector.")

    def get_b(self):
        """ Retrieve the value of this color's BLUE component. """

        return self[2]

    def set_b(self, value):
        """ Set the value of this color's BLUE component.
        
        NOTE: The value will be normalized if above 1. """

        if value < 0.0 or value > 1.0:
            value = min(fabs(value)/255.0, 1.0)
        self[2] = self._UNIT(value)

    b = property(get_b, set_b, doc="BLUE-Component of the Vector.")

class ColorRGBA(ColorRGB):
    """ The ColorRBGA is a 4d vector representation of color with the RED, 
    GREEN, BLUE additive components and an additional opactiy value (ALPHA).
    """
    
    def __new__(cls, r, g, b, a):
        """ Internal function produces a new ndarray casted to this class. """
        
        if r < 0.0 or r > 1.0:
            r = min(fabs(r)/255.0, 1.0)
        if g < 0.0 or g > 1.0:
            g = min(fabs(g)/255.0, 1.0)
        if b < 0.0 or b > 1.0:
            b = min(fabs(b)/255.0, 1.0)
        if a < 0.0 or a > 1.0:
            a = min(fabs(a)/255.0, 1.0)
        
        obj = np.asarray((r, g, b, a), FLOAT32).view(cls)
        return obj
    
    def __array_finalize__(self, obj):
        """ Internal function to finalize additional attribues added to the 
        base ndarray class. """
        
        if obj is None: return

    def get_a(self):
        """ Retrieve the opacity (alpha) value associated with this color. """

        return self[3]

    def set_a(self, value):
        """ Set the value of this color's ALPHA (opactiy) component.
        
        NOTE: The value will be normalized if above 1. """

        if value < 0.0 or value > 1.0:
            value = min(fabs(value)/255.0, 1.0)
        self[3] = self._UNIT(value)

    a = property(get_a, set_a, doc="ALPHA-Component of the Vector.")

class Light(object):
    """ The Light class is a collection of properties that dictate how the
    light interacts with objects. 
    
    Attributes
    ----------
    position : :class:`Vector4f`
        The current position of the light.  The 4th component designates if 
        the light is point light (0) or directional (1).
    direction : :class:`Vector3f`
        Direction of the source is pointed.
    ambient : :class:`ColorRGB`
        The amount of base light in per RGB channel. (The color of the light).
    diffuse : :class:`ColorRGB`
        The amount of light reflected per RGB channel.
    specular : :class:`ColorRGB`
        The intensity of reflected light relative to the observers position.
    attn : :class:`Vector3f`
        Attenuation scaling factors\n
        coeffecient {x}, linear (y), quadratic (z) where, 
        :math:'a = x + y*d + z*d*d' with d = distance between light source and
        object.
    """
    
    def __init__(self):
        
        self._position = Vector4f(0.0, 0.0, 0.0, 0.0)
        self._direction = Vector3f(0.0, 0.0, 0.0)
        self._ambient = ColorRGB(1.0, 1.0, 1.0)
        self._diffuse = ColorRGB(1.0, 1.0, 1.0)
        self._specular = ColorRGB(1.0, 1.0, 1.0)
        self._attn = Vector3f(1.0, 0.0, 0.0)
        # TODO: add floats for falloff
        
    def get_position(self): return self._position
    def set_position(self, vector):
        self._position[:3] = vector[:3]
    position = property(get_position)
    
    def get_direction(self): return self._direction
    def set_direction(self, vector):
        self._direction[:3] = vector[:3]
    direction = property(get_direction)
    
    def get_ambient(self): return self._ambient
    def set_ambient(self, color):
        self._ambient[:3] = color[:3]
    ambient = property(get_ambient)

    def get_diffuse(self): return self._diffuse
    def set_diffuse(self, color):
        self._diffuse[:3] = color[:3]
    diffuse = property(get_diffuse)

    def get_specular(self): return self._specular
    def set_specular(self, color):
        self._specular[:3] = color[:3]
    specular = property(get_specular)

    def get_attn(self): return self._attn
    def set_attn(self, vector):
        self._attn[:3] = vector[:3]
    attn = property(get_attn)

    def get_coeffecient(self): return self._attn[0]
    def set_coeffecient(self, value):
        self._attn.x = value
    coeffecient = property(get_coeffecient, set_coeffecient)

    def get_linear(self): return self._attn[1]
    def set_linear(self, value):
        self._attn.y = value
    linear = property(get_linear, set_linear)
    
    def get_quadratic(self): return self._attn[2]
    def set_quadratic(self, value):
        self._attn.z = value
    quadratic = property(get_quadratic, set_quadratic)
    
    def make_directional(self):
        
        self.position[3] = 1

    def is_directional(self):
        
        return self.position[3]

    def to_array(self):
        
        return np.concatenate((self._position, self._direction, self._ambient,
                               self._diffuse, self._specular, self._attn))

class Material2(object):
    
    def __init__(self, name):

        self._name = name
        self._ambient = ColorRGB(1.0, 1.0, 1.0)
        self._diffuse = ColorRGB(1.0, 1.0, 1.0)
        self._specular = ColorRGB(1.0, 1.0, 1.0)
        self._shininess = 1.0

    def get_ambient(self): return self._ambient
    def set_ambient(self, color):
        self._ambient[:3] = color[:3]
    ambient = property(get_ambient)

    def get_diffuse(self): return self._diffuse
    def set_diffuse(self, color):
        self._diffuse[:3] = color[:3]
    diffuse = property(get_diffuse)

    def get_specular(self): return self._specular
    def set_specular(self, color):
        self._specular[:3] = color[:3]
    specular = property(get_specular)

    def to_array(self): pass

class Material(object):
    
    def __init__(self, name):

        self._name = name
        self._ka = ColorRGB(1.0, 1.0, 1.0)
        self._kd = ColorRGB(1.0, 1.0, 1.0)
        
    def send(self):
        """ Transfers this material's data to the GPU. """
        pass

    def __set_color(self, r, g, b):
    
        try:
            if r.size == 3:
                return r
            else:
                return r.xyz
        except AttributeError:
            if g is None:
                g = r
            if b is None:
                b = r
            return ColorRGB(r, g, b)

    def set_ka(self, r, g=None, b=None):
        """ Set the the `Ka` (Ambient) component of this material. """
        
        self._ka = self.__set_color(r, g, b)
            
    def get_ka(self):
        """ Retrieve the the `Ka` (Ambient) component of this material. """
        
        return self._ka
    
    ka = property(get_ka, set_ka, doc="Retrieve the `Ka` ambient component.")

    def set_kd(self, r, g=None, b=None):
        """ Set the the `Ka` (Ambient) component of this material. """
        
        self._kd = self.__set_color(r, g, b)
            
    def get_kd(self):
        """ Retrieve the the `Ka` (Ambient) component of this material. """
        
        return self._kd
    
    kd = property(get_kd, set_kd, doc="Retrieve the `Kd` diffuse component.")

    def get_name(self):
        
        return self._name

class MaterialLoader(object):
    
    def __init__(self):
        
        self.materials = []
        
    def from_mtl_file(self, filename):
        
        current = None
        with open(filename, "r") as fin:
            for uline in fin:
                
                tokens = uline.strip().split(" ")

                if len(tokens) == 0: continue # empty line
                if len(tokens[0]) == 0: continue # blank line

                first = tokens[0].lower()

                if first[0] == "#": continue # Comment line
                
                if first == "newmtl": # Starting a new material
                    if current is not None:
                        self.materials.append(current)
                    current = Material(tokens[1])
                    
                elif first == "ka": # Ambient color
                    if len(tokens) == 2:
                        current.set_ka(FLOAT32(tokens[1]))
                    else:
                        current.set_ka(FLOAT32(tokens[1]), FLOAT32(tokens[2]), FLOAT32(tokens[3]))

                elif first == "kd": # Diffuse color
                    if len(tokens) == 2:
                        current.set_kd(FLOAT32(tokens[1]))
                    else:
                        current.set_kd(FLOAT32(tokens[1]), FLOAT32(tokens[2]), FLOAT32(tokens[3]))

        # Make sure to save the last material
        if current is not None:
            self.materials.append(current)

if __name__ == "__main__":

    test = ColorRGB(0.2, 48, 0.2)        
    print test.size
    print test.dtype
    print test
    
    test.r = 218
    print test.r
    
    test2 = ColorRGBA(0.2, 48, .01, 1.3)
    test2.r = 0x3F
    print test2
    
    mat_test = Material("test")
    mat_test.set_ka(4)
    print mat_test.ka
    mat_test.set_ka(test)
    print mat_test.ka
    
    loader = MaterialLoader()
    loader.from_mtl_file("../res/Birch1.mtl")
    for m in loader.materials:
        print m.get_name()
        print "ka", m.ka
        print "kd", m.kd
    
    test_light = Light()
    test_light.position.x = 4
    print test_light.position
    new_position = Vector3f(1, 2, 3)
    test_light.set_position(new_position)
    print test_light.position
    
    print test_light.to_array
    test_light.set_direction(new_position)
    print test_light.direction
    test_light.coeffecient *= 4
    print test_light.attn
    Light()
    
    