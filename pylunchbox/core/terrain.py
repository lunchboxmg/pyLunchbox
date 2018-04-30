from numpy import zeros as _zeros

__author__

from noise

class Terrain(object):

    def __init__(self, width, height):

        self._elevations = _zeros(width*height)

    def get_elevation(self, x, z):
        """ Retrieve the elevation at the given coordinate (x, z). """

        return self._elevations[x + z]

class TerrainGenerator(object):

    def __init__(self):
        pass

class FlatTerrain(Terrain):

    def __init__(self, world):

        self._world = world

class TerrainSector(object):

    def __init__(self, x, y):

        self._x = x
        self._y = y
