import numpy as np
from glutils import Vao, Vbo

class MemoryChunk(object):
    """ The MemoryChunk class keeps the indexing information for an entity's
    mesh data that is placing within a batch's data array.

    This class is also a node for the double-linked list that represents the
    batch's data references. """

    _COUNT = 0 # Internal indexing

    def __init__(self, start, length, is_gap=False, ref=None):
        """ Constructor.

        Parameters:
        ===========
        * start (:obj:`int`): The start index of the chunk.
        * length (:obj:`length`): The amound of space that this chunk is going
          to occupy.
        * is_gap (:obj:`bool`): Flag that marks this chunk as being unused
          currently (ie, and empty space between two chunks).
        * ref (:obj:`OBJECT`): A reference to the owner of the data being
          dumped into this chunk.
        """

        self._index_first = start
        self._index_last = start + length
        self._is_gap = is_gap
        self._ref = ref

        # This class is also a node for double-linked list
        self._previous = None
        self._next = None

        # Internal referencing
        self._id = MemoryChunk._COUNT
        MemoryChunk._COUNT += 1

    @staticmethod
    def create_empty_chunk(start, length):
        """ Create an empty chunk that will be a gap. """

        return MemoryChunk(0, 0, True)

    @staticmethod
    def create_data_chunk(start, data):
        """ Create an chunk for the input data. """

        # TOOD: We need to determine what the reference data class is going to be
        return MemoryChunk(start, len(data), False, data)

    @staticmethod
    def append(new_chunk, target):
        """ Add this chunk to the input chunk. """

        if target is not None:
            target.set_next(new_chunk)

    def insert_into(self, chunk, manager):
        """ Insert the current chunk into this gap. """

        if self._previous is not None:
            self._previous.set_next(chunk)
        if self.get_length() == chunk.get_length():
            chunk.set_next(self)
            manager.remove_gap(self)
        else:
            chunk.set_next(self)
            self.shrink(chunk.get_length())

    def shrink(self, amount):
        """ Reduce the size of this gap.  Happens at the front end of the
        chunk (i.e., pushes start forward). """

        self._index_first += amount

    def expand(self, amount):
        """ Increases the size of this gap.  Happens at the tail end of the
        chunk (i.e., extends the last index). """

        self._index_last += amount

    def shift(self, amount):
        """ Shifts the indexing values of this chunk by the input `amount`. """

        self._index_first += amount
        self._index_last += amount

    def set_next(self, next_, cont=True):
        """ Set the reference to the next chunk in the chain.

        Parameters:
        ===========
        * next_ (:obj:`MemoryChunk`): The chunk that comes next.
        * cont (:obj:`bool`) Flag that tells the chunk system to set the input
          chunks previous chunk to this chunk.
        """

        self._next = next_
        if (next_ is not None) and cont:
            next_.set_previous(self, False)

    def set_previous(self, previous, cont=True):
        """ Set the reference to the previous chunk in the chain.

        Parameters:
        ===========
        * previous (:obj:`MemoryChunk`): The chunk that comes before this chunk.
        * cont (:obj:`bool`) Flag that tells the chunk system to set the input
          chunks previous chunk to this chunk.
        """

        self._previous = previous
        if (previous is not None) and cont:
            previous.set_next(self, False)

    def get_next(self):
        """ Retreive the chunk that comes after this chunk. """

        return self._next

    def get_previous(self):
        """ Retrieve the chunk that came before this chunk. """

        return self._previous

    def get_index_first(self):
        """ Retrieve the index that marks the start of this chunk's data. """

        return self._index_first

    def get_index_last(self):
        """ Retrieve the index of the last element of this chunks data. """

        return self._index_last

    def get_length(self):
        """ Retrieve the length (size) of this chunk of memory. """

        return self._index_last - self._index_first

    def get_data_ref(self):
        """ Retrieve the reference to the object whose data is associated with
        this chunk of memory. """

        return self._ref

    def is_gap(self):
        """ Determine if this chunk is gap (empty). """

        return self._is_gap

    def get_id(self):
        """ Retrieve the id associate with this chunk.  The id is mainly for
        testing/output purposes and designates when the chunk was created. """

        return self._id

    def __str__(self):

        msg = "MemoryChunk[{:05d}]@({:d},{:d}), is_gap={:b}"
        return msg.format(self._id, self._index_first, self._index_last, self._is_gap)

class Batch(object): pass

class StaticBatch(Batch):
    """ The StaticBatch class if the batch system for objects whose vertex data
    generally does not change on a regular basis. """

    pass

class MemoryManager(object):
    """ Manages the memory associated with a batch.  All the data within a
    batch is stored within one buffer object. """

    MAX_REFACTOR = 300

    def __init__(self, max_size):
        """ Constructor.

        Parameters:
        ===========
        * max_size (:obj:`int`): The maximum number of vertices housed within
          this manager's batch.
        """

        self._max_size = max_size
        self._empty = []
        self._last = None
        self._index_last = 0

        # GPU vertex array, buffer object references
        self._vao = -1
        self._vbo = -1

    def allocate(self, data):
        """ Allocate a memory chunk for the input `data`.  Will use an empty
        chunk if one is available to minimize size of the batch. """

        if (len(data) + self._index_last) / 9 > self._max_size: # TODO: Incorporate VertexFormat
            print "ERROR: Batch is full!"
            return None

        for chunk in self._empty:
            if chunk.get_length() >= len(data):
                new_chunk = self._store_data(chunk.get_index_first(), data)
                chunk.insert_into(new_chunk, self)
                return new_chunk

        new_chunk = self.__store_data(self._index_last, data)
        MemoryChunk.append(new_chunk, self._last)
        self._last = new_chunk
        self._index_last += len(data)
        return new_chunk

    def __store_data(self, start, data):
        """ Internal function to store the data into batch memory. """

        new_chunk = MemoryChunk.create_data_chunk(self._index_last, data)
        self.__store_to_gpu(start, data)
        return new_chunk

    def __store_to_gpu(self, start, data):
        """ Internal function to place the data within the vertex array/buffer
        objects. """

        pass

    def remove(self, chunk):
        """ Remove the input `chunk` from this batch. """

        next_ = chunk.get_next()

if __name__ == "__main__":

    chunks = [] ; start = 0
    for _ in xrange(10):
        test_size = np.random.randint(0, 30)
        test_data = np.random.uniform(size=test_size)
        chunks.append(MemoryChunk.create_data_chunk(start, test_data))
        start += test_size

    for chunk in chunks:
        print chunk
