import array

class BitArray(object):
    """ The BitArray class is used to store a collection of flags as bits in an
    array of longs.

    Example: Python Long has 32 bits (4 bytes of memory). For 4 bytes you can
    represent 32 booleans.
    """

    MAX_VALUE = 4294967295L
    BITS_PER = 32
    SPAN = 5

    def __init__(self, num_bits):
        """ Constructor.

        Parameters:
        ===========
        * num_bits (:obj:`int`): Number of bits needed.
        """

        self._bits = array.array('L')
        self.__check_capacity(num_bits >> 5)

    def get(self, index):
        """ Get the value of the bit at position `index`. """

        self.__check_capacity(index >> 5)
        return (self._bits[index >> 5] & (1 << (index & 0x1F))) != 0

    def set(self, index):
        """ Set the value of the bit at position `index`. """

        self.__check_capacity(index >> 5)
        self._bits[index >> 5] |= 1 << (index & 0x1F)

    def set_all(self):
        """ Set all the bits within this array. """

        for i in xrange(len(self._bits)):
            self._bits[i] = BitArray.MAX_VALUE

    def clear(self, index):
        """ Clear the bit at position `index`. """

        self.__check_capacity(index >> 5)
        self._bits[index >> 5] &= ~(1 << (index & 0x1F))

    def clear_all(self):
        """ Clear all the bits in this array. """

        for i in xrange(len(self._bits)):
            self._bits[i] = 0L

    def toggle(self, index):
        """ Toggle the bit at position `index`. """

        self._bits[index >> 5] ^= 1 << (index & 0x1F)

    def __check_capacity(self, size):
        """ Check if the array contains enough elements (size) to provide the
        desired number of bits. """

        if (size >= len(self._bits)):
            self._bits.extend((0L,)*(size + 1 - len(self._bits)))

    def __str__(self):

        out = []
        for i in xrange(len(self._bits)*BitArray.BITS_PER):
            out.append("{:b}".format(self.get(i)))
        return "".join(out)

if __name__ == "__main__":

    from time import time as _time

    test1 = BitArray(200)
    print test1

    NUM = 20000

    time_start = _time()
    for i in xrange(NUM):
        test1.get(42)
    time_done = _time()
    print (time_done - time_start)/NUM
