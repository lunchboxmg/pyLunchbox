from numpy import zeros as _zeros

class Terrain(object): 

    def create_meshgrid(self, width, height):

        size = width * height



class FlatTerrain(Terrain):

    def __init__(self, world):

        self._world = world

class TerrainSector(object):

    def __init__(self, x, y):

        self._x = x
        self._y = y
