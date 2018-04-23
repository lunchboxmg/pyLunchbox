class Terrain(object): pass

class FlatTerrain(Terrain):

    def __init__(self, world):

        self._world = world

class TerrainSector(object):

    def __init__(self, x, y):

        self._x = x
        self._y = y
