from numpy import empty, zeros as _zeros
from numpy.random import RandomState

__author__ = "lunchboxmg"

from noise import NoiseOctaves
from maths import Vector3f

class TerrainSettings(object):

    def __init__(self):

        self.num_octaves = 8

class Terrain(object):

    def __init__(self, width, height):

        self._elevations = _zeros(width*height)

    def get_elevation(self, x, z):
        """ Retrieve the elevation at the given coordinate (x, z). """

        return self._elevations[x + z]

class TerrainGenerator(object):

    def __init__(self, seed=42337):
        
        self._seed = seed
        self._rng = RandomState(seed)

        self._generator = NoiseOctaves(self._rng, 8)

    def generate(self, xoffset, zoffset, xsize, zsize, xscale, zscale):

        raise NotImplementedError()

class FlatTerrainGenerator(TerrainGenerator):

    def generate(self, xoffset, zoffset, xsize, zsize, xscale, zscale):

        size = xsize * zsize
        elevs = _zeros(xsize * zsize)
        positions = empty(size, dtype=Vector3f)

        index = 0
        for iz in xrange(zsize):
            for ix in xrange(xsize):
                p0 = Vector3f(xoffset + ix, elevs[iz<<5|ix], zoffset + iz)
                p1 = Vector3f(xoffset + ix, elevs[iz<<5|(ix+1)], zoffset + iz)
                p2 = Vector3f(xoffset + ix, elevs[(iz+1)<<5|ix], zoffset + iz)
                p3 = Vector3f(xoffset + ix, elevs[(iz+1)<<5|(ix+1)], zoffset + iz)

    def __generate_elevations(self, xoffset, zoffset, xsize, zsize, xscale, zscale):

        #elevs = self._generator.generate2d(xoffset, zoffset, xsize, zsize, 
        #                                   xscale, zscale)
        elevs = _zeros(xsize * zsize)

        return elevs



class FlatTerrain(Terrain):

    def __init__(self, world):

        self._world = world

class TerrainSector(object):

    def __init__(self, x, y):

        self._x = x
        self._y = y
