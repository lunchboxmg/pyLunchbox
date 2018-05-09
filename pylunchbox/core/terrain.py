from numpy import empty, zeros as _zeros
from numpy.random import RandomState

__author__ = "lunchboxmg"

from noise import NoiseOctaves
from maths import Vector3f, calc_surface_normal
from modeling import MeshBundle, MeshData

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
        positions = empty(size*6, dtype=Vector3f)
        normals = _zeros(size*6, dtype=Vector3f._UNIT)
        colors = empty(size, dtype=Vector3f)

        index = 0
        for iz in xrange(zsize):
            for ix in xrange(xsize):

                # Determine the positions of the quad
                p1 = Vector3f(xoffset + ix , 0, zoffset + iz)
                p2 = Vector3f(xoffset + ix, 0, zoffset + iz + 1)
                p3 = Vector3f(xoffset + ix + 1, 0, zoffset + iz + 1)
                p4 = Vector3f(xoffset + ix + 1, 0, zoffset + iz)
                
                positions[index:index+6] = [p1, p2, p4, p4, p2, p3]


class VariableTerrainGenerator(TerrainGenerator):

    def generate(self, xoffset, zoffset, xsize, zsize, xscale, zscale):

        size = xsize * zsize
        elevs = self.__generate_elevations(xoffset, zoffset, xsize, zsize, xscale, zscale)
        positions = empty(size * 6, dtype=Vector3f)
        normals = empty(size * 6, dtype=Vector3f)
        colors = empty(size * 6, dtype=Vector3f)

        index = 0
        for iz in xrange(zsize):
            for ix in xrange(xsize):

                # Determine the positions of the quad
                p1 = Vector3f(xoffset + ix, elevs[iz<<5|ix], zoffset + iz)
                p2 = Vector3f(xoffset + ix, elevs[(iz+1)<<5|ix], zoffset + iz + 1)
                p3 = Vector3f(xoffset + ix + 1, elevs[(iz+1)<<5|(ix+1)], zoffset + iz + 1)
                p4 = Vector3f(xoffset + ix + 1, elevs[iz<<5|(ix+1)], zoffset + iz)

                # Calculate the normals of the triangles
                n1 = calc_surface_normal(p1, p2, p4)
                n2 = calc_surface_normal(p4, p2, p3)

                # Calculate the colors
                c1 = (1 - p1.y / elevs.max()) * Vector3f(0.0, 1.0, 0.0)
                c2 = (1 - p2.y / elevs.max()) * Vector3f(0.0, 1.0, 0.0)
                c3 = (1 - p3.y / elevs.max()) * Vector3f(0.0, 1.0, 0.0)
                c4 = (1 - p4.y / elevs.max()) * Vector3f(0.0, 1.0, 0.0)

                positions[index:index+6] = [p1, p2, p4, p4, p2, p3]
                normals[index:index+6] = [n1, n1, n1, n2, n2, n2]
                colors[index:index+6] = [c1, c2, c4, c4, c2, c3]

                index += 6

        return MeshBundle(("TERRAIN", MeshData(positions, colors, normals)))

    def __generate_elevations(self, xoffset, zoffset, xsize, zsize, xscale, zscale):

        elevs = self._generator.generate2d(xoffset, zoffset, xsize, zsize, 
                                           xscale, zscale)
        
        return elevs

class FlatTerrain(Terrain):

    def __init__(self, world):

        self._world = world

class TerrainSector(object):

    def __init__(self, x, y):

        self._x = x
        self._y = y

if __name__ == "__main__":

    tgen = VariableTerrainGenerator()
    bundle = tgen.generate(0, 0, 32, 32, 200.0, 200.0)
    print bundle