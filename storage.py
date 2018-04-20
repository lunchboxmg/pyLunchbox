""" The storage module contains storage classes.

Storage classes:
- BitArray
- Bag

"""

import array
from numpy import empty

__author__ = "lunchboxmg"

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

class Bag(object):
    """ The Bag class is a data container. """

    def __init__(self, type_, size=64):
        """ Constructor. 

        Parameters:
        ===========
        * type_ (:obj:`class`): A reference to the type of data that will be
          stored in this bag.
        * size (:obj:`int`): The base size of a bag.
        """

        self._contents = empty(size, dtype=type_)
        self._type = type_
        self._size = 0

    def add(self, item):
        """ Add an item to this bag. """

        if not isinstance(item, self._type): return None # TODO: Do need?
        if self._size == self._contents.size:
            self.__expand(self._size * 2)
        self._contents[self._size] = item
        self._size += 1
        return item
    
    def set(self, item, index):
        """ Set the contents of the bag at position `index` to the input 
        `item`. """

        if not isinstance(item, self._type): return None # TODO: Do need?
        if index >= self._contents.size:
            self.__expand(max(self._contents.size * 2, index + 1))
        self._size = max(self._size, index + 1)
        self._contents[index] = item
        return item

    def unsafe_set(self, item, index):
        """ Set the contents of the bag at position `index` to the input
        `item` without checking if the bag has the capacity first. """

        self._contents[index] = item

    def __expand(self, new_size):
        """ Internal function to expand the size of the data array. """

        size = self._contents.size
        self._contents.resize(new_size)
        self._contents[size:new_size] = None

    def is_empty(self):
        """ Determine if this bag has no contents. """

        return self._size == 0

    def get_capacity(self):
        """ Retrieve the current capacity for this bag. """

        return self._contents.size

class _Dummy(object):

    def __init__(self, a, b):

        self.a = a
        self.b = b

    def __str__(self): return "Dummy({:d},{:d})".format(self.a, self.b)

class _Dummy2(_Dummy) : pass

class _DummyX(_Dummy) : pass

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

    test_bag = Bag(_Dummy2)
    test_bag.add(_Dummy2(1, 2))
    for item in test_bag._contents:
        if item is not None: print item
    print test_bag._contents.dtype, test_bag._type

    d2 = _DummyX(1,3)
    print isinstance(d2, test_bag._type)

    print test_bag.add(d2)