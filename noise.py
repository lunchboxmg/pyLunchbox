from numpy import array, zeros, arange, stack, meshgrid, floor as npfloor
from numpy.random import RandomState
from time import time as _time

# Plotting import for testing
import matplotlib.pyplot as plt
from matplotlib import cm

GRAD2D = array([[0,1],[0,-1],[1,0],[-1,0]])

class PerlinNoise(object):
    """ The PerlinNoise class is responsible for generating ... noise. """

    def __init__(self, rng):
        """ Constructor.

        Parameters:
        ===========
        * rng (:obj:``): Random number generator.
        """

        # Randomize the permutation table table
        p = arange(256, dtype=int)
        for _ in xrange(5): rng.shuffle(p)
        self._p = stack([p, p]).flatten()

        # Offsets for this particular noise generator
        self._xoffset = rng.rand() * 256.0
        self._yoffset = rng.rand() * 256.0
        self._zoffset = rng.rand() * 256.0

    def get_noise_array_2D(self, noise, xoffset, zoffset, xsize, zsize, xscale,
                           zscale, noise_scale):
        """ Create a 2D grid of noise values. """

        p = self._p

        x = arange(xsize) * xscale + xoffset + self._xoffset
        z = arange(zsize) * zscale + zoffset + self._zoffset
        x, z = meshgrid(x, z)

        xi = npfloor(x).astype(int) & 255
        zi = npfloor(z).astype(int) & 255

        xf = x - npfloor(x)
        zf = z - npfloor(z)

        u = fade(xf)
        v = fade(zf)

        n00 = gradient2d(p[p[xi] + zi], xf, zf)
        n01 = gradient2d(p[p[xi] + zi + 1], xf, zf - 1)
        n11 = gradient2d(p[p[xi + 1] + zi + 1], xf - 1, zf - 1)
        n10 = gradient2d(p[p[xi + 1] + zi], xf - 1, zf)

        x1 = lerp(n00, n10, u)
        x2 = lerp(n01, n11, u)
        noise += lerp(x1, x2, v) / noise_scale

def lerp(a, b, x): return a + x * (b - a)

def fade(t): return t*t*t * (6*t*t - 15*t + 10)

def gradient2d(h, x, y):

    g = GRAD2D[h & 3]
    return g[:,:,0] * x + g[:,:,1] * y

class NoiseOctaves(object):

    def __init__(self, rng, num_octaves):
        """ Constructor.

        Parameters:
        ===========
        * rng (:obj:`RandomState`): The random number generator which is a numpy
          RandomState object initialized with the seed.
        * num_octaves (:obj:`int`): The number of octaves.
        """

        self._num_octaves = num_octaves
        self._generators = [PerlinNoise(rng) for _ in xrange(num_octaves)]

    def generate2d(self, xsector, zsector, xsize, zsize, xscale, zscale):
        """ Generate the layered 2d noise array. """

        amplitude = 1.0
        max_amplitude = 0.0

        noise = zeros((xsize, zsize))

        for gen in self._generators:
            u = xsector * amplitude * xscale
            w = zsector * amplitude * zscale
            gen.get_noise_array_2D(noise, u, w, xsize, zsize, xscale * amplitude,
                                   zscale * amplitude, amplitude)
            max_amplitude += 1.0 / amplitude
            amplitude *= 0.5

        return noise / max_amplitude

def test_display_heightmap(xoffset, zoffset, data):

    plt.imshow(data, origin="upper", interpolation="none", cmap=cm.gray)
    plt.colorbar()
    plt.show()


if __name__ == "__main__":

    SEED = 42337
    RNG = RandomState(SEED)

    num_octaves = 16
    noise_gen = NoiseOctaves(RNG, num_octaves)

    # Test Inputs
    xsector, zsector = -24, 82
    xsize = zsize = 16
    xscale, zscale = 200, 200

    # Test a grid of sectors
    xgrid = zgrid = 20
    noise_grid = zeros((xgrid * xsize, zgrid * zsize))

    time_start = _time()
    for i in xrange(xgrid):
        xoffset = (xsector + i) * xsize
        for j in xrange(zgrid):
            zoffset = (zsector + j) * zsize
            noise = noise_gen.generate2d(xoffset, zoffset, xsize, zsize,
                                         xscale, zscale)
            noise_grid[j*zsize: (j+1)*zsize, i*xsize:(i+1)*xsize] = noise[:]
    time_stop = _time()

    print "Total time: {:.4f}".format(time_stop - time_start)
    print "Avg time per: {:.4f}".format((time_stop - time_start)/xgrid/zgrid)

    xoffset = xsector * xsize
    zoffset = zsector * zsize
    test_display_heightmap(xoffset, zoffset, noise_grid)
