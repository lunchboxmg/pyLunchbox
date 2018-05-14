""" The material module contains the structures for defining a GLSL matieral.

Classes
-------
ColorRGB (Vector3f)
    Represents a RGB color whose values range between 0.0 and 1.0
"""

from math import fabs

__author__ = "lunchboxmg"

from maths import Vector3f, Vector4f, FLOAT32

class ColorRGB(Vector3f):
    
    def __new__(cls, r, g, b):
        
        if r < 0.0 or r > 1.0:
            r = min(fabs(r)/255.0, 1.0)
        if g < 0.0 or g > 1.0:
            g = min(fabs(g)/255.0, 1.0)
        if b < 0.0 or b > 1.0:
            b = min(fabs(b)/255.0, 1.0)
        
        obj = super(ColorRGB, cls).__new__(cls, r, g, b)
        return obj
    
    def __array_finalize__(self, obj):
        
        if obj is None: return

    def get_r(self): return self[0]
    def set_r(self, value): 
        if value < 0.0 or value > 1.0:
            value = min(fabs(value)/255.0, 1.0)
        self[0] = self._UNIT(value)

    r = property(get_r, set_r, doc="RED-Component of the Vector.")

    def get_g(self): return self[1]
    def set_g(self, value):
        if value < 0.0 or value > 1.0:
            value = min(fabs(value)/255.0, 1.0)
        self[1] = self._UNIT(value)

    g = property(get_g, set_g, doc="BLUE-Component of the Vector.")

    def get_b(self): return self[2]
    def set_b(self, value):
        if value < 0.0 or value > 1.0:
            value = min(fabs(value)/255.0, 1.0)
        self[2] = self._UNIT(value)

    b = property(get_b, set_b, doc="GREEN-Component of the Vector.")

class ColorRGBA(Vector4f):
    
    def __new__(cls, r, g, b, a):
        
        if r < 0.0 or r > 1.0:
            r = min(fabs(r)/255.0, 1.0)
        if g < 0.0 or g > 1.0:
            g = min(fabs(g)/255.0, 1.0)
        if b < 0.0 or b > 1.0:
            b = min(fabs(b)/255.0, 1.0)
        if a < 0.0 or a > 1.0:
            a = min(fabs(a)/255.0, 1.0)
        
        obj = super(ColorRGBA, cls).__new__(cls, r, g, b, a)
        return obj
    
    def __array_finalize__(self, obj):
        
        if obj is None: return

    def get_r(self): return self[0]
    def set_r(self, value): 
        if value < 0.0 or value > 1.0:
            value = min(fabs(value)/255.0, 1.0)
        self[0] = self._UNIT(value)

    r = property(get_r, set_r, doc="RED-Component of the Vector.")

    def get_g(self): return self[1]
    def set_g(self, value):
        if value < 0.0 or value > 1.0:
            value = min(fabs(value)/255.0, 1.0)
        self[1] = self._UNIT(value)

    g = property(get_g, set_g, doc="BLUE-Component of the Vector.")

    def get_b(self): return self[2]
    def set_b(self, value):
        if value < 0.0 or value > 1.0:
            value = min(fabs(value)/255.0, 1.0)
        self[2] = self._UNIT(value)

    b = property(get_b, set_b, doc="GREEN-Component of the Vector.")

    def get_a(self): return self[3]
    def set_a(self, value):
        if value < 0.0 or value > 1.0:
            value = min(fabs(value)/255.0, 1.0)
        self[3] = self._UNIT(value)

    a = property(get_a, set_a, doc="ALPHA-Component of the Vector.")

class SpectralFile(object): pass

class CIE_XYZ(object): pass

class Material(object):
    
    def __init__(self, name):

        self._name = name
        self._ka = ColorRGB(1.0, 1.0, 1.0)
        self._kd = ColorRGB(1.0, 1.0, 1.0)

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
        
    def from_file(self, filename):
        
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
        if current is not None:
            self.materials.append(current)

if __name__ == "__main__":

    test = ColorRGB(0.2, 48, 0.2)        
    print test.size
    print test.dtype
    print test
    
    test.r = 218
    print test.r
    
    mat_test = Material("test")
    mat_test.set_ka(4)
    print mat_test.ka
    mat_test.set_ka(test)
    print mat_test.ka
    
    loader = MaterialLoader()
    loader.from_file("../res/Birch1.mtl")
    for m in loader.materials:
        print m.get_name()
        print "ka", m.ka
        print "kd", m.kd
    
    
    
    
    