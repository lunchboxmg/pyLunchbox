import numpy as np
from numpy import ndarray
from numpy import sqrt as npsqrt, sum as npsum, dot

FLOAT32 = np.float32
UINT32 = np.uint32
FLOAT64 = np.float64

# Vector functions

def get_length(vector):
    """ Retrieve the length of the input vector. """

    return npsqrt(npsum(vector*vector))

def normalize(vector):
    """ Normalize the input vector. """

    norm = npsqrt(npsum(vector*vector))
    return vector / norm

def proj(u, n):
    """ Projection of vector `u` onto the plane whose normal is `n`. """

    top = dot(u, n)
    bot = npsum(n * n)
    return u - (top/bot) * n

def average(vectors):
    """ Take the average of the input list of vectors. """

    summation = Vector3f(0, 0, 0)
    for v in vectors:
        summation += v
    if get_length(summation) == 0:
        print vectors
    return summation / get_length(summation)

# Vector classes

class Vector2f(ndarray):
    """
    The Vector2f class is a subclassed numpy array composed of 2 floats.

    Gives a view of the numpy array made from x, y (or z) that allows the
    user to access elements by their component name.
    """

    _UNIT = FLOAT32

    def __new__(cls, x, y):
        """ Create a numpy array of elements x and y.

        Parameters:
        ===========
        x (:obj:`float`): x-component.
        y (:obj:`float`): y-component.
        """

        obj = np.asarray((x, y), cls._UNIT).view(cls)
        return obj

    def __array_finalize__(self, obj): pass

    def get_x(self): return self[0]
    def set_x(self, value): self[0] = self._UNIT(value)
    x = property(get_x, set_x, doc="X-Component of the Vector.")

    def get_y(self): return self[1]
    def set_y(self, value): self[1] = self._UNIT(value)
    y = property(get_y, set_y, doc="Y-Component of the Vector.")

    def get_length(self):
        """Retrieve the length of this vector. """

        return get_length(self)

    def normalize(self, out=None):
        """ Normalize this vector inplace.

        Parameters (Optional):
        ======================
        * out (:obj:`ndarray`): the ndarray or vector that the result will be
          placed in.
        """

        new_array = normalize(self)
        if out:
            out[:] = new_array[:]
        else:
            self[:] = new_array[:]

class Vector2i(Vector2f):

    _UNIT = UINT32

class Vector2d(Vector2f):

    _UNIT = FLOAT64

class Vector3f(Vector2f):
    """
    The Vector3f class is a subclassed numpy array composed of 3 floats.

    Gives a view of the numpy array made from x, y, z that allows the
    user to access elements by their component name.
    """

    _UNIT = FLOAT32

    def __new__(cls, x, y, z=0):
        """ Create numpy array of elements x, y, z.

        Parameters:
        ===========
        x (:obj:`float`): x-component.
        y (:obj:`float`): y-component.
        z (:obj:`float`): z-component.
        """

        obj = np.asarray((x, y, z), cls._UNIT).view(cls)
        return obj

    def __array_finalize__(self, obj): pass

    def get_z(self): return self[2]
    def set_z(self, value): self[2] = self._UNIT(value)
    z = property(get_z, set_z, doc="Z-Component of the Vector.")

    def get_xy(self):
        """ Retrieve a Vector2f of the x, y components. """

        return Vector2f(self.x, self.y)

    def get_xz(self):
        """ Retrieve a Vector2f of the x, z components. """

        return Vector2f(self.x, self.z)

    def get_yz(self):
        """ Retrieve a Vector2f of the y, z components. """

        return Vector2f(self.y, self.z)

class Vector3i(Vector3f):

    _UNIT = UINT32

# Math functions

def clamp(x, x_min, x_max):
    """ Force the input value `x` to be within the bounds of [x_min, x_max]. """

    if x < x_min: return x_min
    elif x > x_max: return x_max
    return x

if __name__ == "__main__":

    test3f = Vector3f(1, 2, 3) + np.array([1, 2, 3])
    test3f.normalize()

    print type(test3f)
    print test3f.z

    test2f = Vector2f(2, 3)
    print id(test2f.base)
    test2f.normalize()
    print id(test2f.base)

    test2 = Vector3f(test2f.x, test2f.y)
    test2.normalize()
    print test2
    print id(test2.base)

    test2f += [1, 3]
    print id(test2f.base)
    print test2f

    test3 = test2.get_xy()
    print type(test3)
    print id(test3.base)

    vs = [Vector3f(i*.5, i + 2.0, i*3) for i in xrange(4)]
    for v in vs: print v
    print average(vs)
