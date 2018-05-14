""" This module is responsible for handling the movement of data to the GPU.

This system attempts to utilize a batching system.  There will be two types
of batching ...
    * static - vertex data that rarely changes
    * dynamic - vertex data that either constantly changes or is toggled.

TODO:
    * VertexFormat - Need to decide if the the batch or the memory chunk
      should be responsible for keeping track of the format / float_count
      of the data associated with it.
"""

import numpy as np
from numpy import zeros as _zeros, float32 as FLOAT32
from functools import partial
from ctypes import c_void_p

__author__ = "lunchboxmg"

from glutils import (Vao, Vbo, GL_ARRAY_BUFFER, GL_STATIC_DRAW, 
                     glVertexAttribPointer, GL_FLOAT, GL_FALSE)
from glutils import create_batch_buffer
from modeling import MeshComponent

class MemoryChunk(object):
    """ The MemoryChunk class keeps the indexing information for an entity's
    mesh data that is placing within a batch's data array.

    This class is also a node for the double-linked list that represents the
    batch's data references. 
    
    TODO: MAX_FLOAT_COUNT should reflect the VertexFormat of the associated
    data.  These chunks will be assigned to MemoryManagers for batch and 
    those batches will be associated with particular shaders.  There is no
    guarantee each shader will utilize the same vertex data format.  """

    MAX_FLOAT_COUNT = 3 + 3 + 3
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

class MemoryManager(object):
    """ Manages the memory associated with a batch.  All the data within a
    batch is stored within one buffer object. 
    
    Example Layout:
    
    +----+----+-----+---+------+-----+-----------------+
    | E1 | E2 | E4  |   |  E5  | E6  |                 |
    +----+----+-----+---+------+-----+-----------------+
    E# - Entity Mesh Data
    Blanks - Gaps, Unused space    
    """

    MAX_REFACTOR = 300 # Maximum amount of data to be refactored within a step

    def __init__(self, max_size, stride=8):
        """ Constructor.

        Parameters
        -----------
        max_size : (:obj:`int`)
            The maximum number of vertices housed within this manager's batch.
        stride : (:obj:`int`)
            The element size of one vertex.
        """

        self._max_size = max_size
        self._stride = stride
        self._empty = []
        self._last = None
        self._index_last = 0

        # GPU vertex array, buffer object references
        self._data = _zeros(max_size * stride, dtype=FLOAT32)
        self._vao, self._vbo = create_batch_buffer(self._data.nbytes, [3,2,3], GL_STATIC_DRAW)

    def allocate(self, data):
        """ Allocate a memory chunk for the input `data`.  Will use an empty
        chunk if one is available to minimize size of the batch. """

        if (len(data) + self._index_last) / self._stride > self._max_size:
            print "ERROR: Batch is full!"
            return None

        for chunk in self._empty:
            if chunk.get_length() >= len(data):
                new_chunk = self.__store_data(chunk.get_index_first(), data)
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

        vbo = self._vbo
        vbo.bind(GL_ARRAY_BUFFER)
        vbo.upload_sub(start, data)
        # TODO: Fix hardcode
        stride = self._stride * 4
        vbo.unbind()

    def remove(self, chunk):
        """ Remove the input `chunk` from this batch. """

        next_ = chunk.get_next()
        prev = chunk.get_previous()
        if next_ is None:
            self.__remove_last(chunk, next_, prev)
        elif next_.is_gap():
            self.__remove_near_gap(chunk, next_, prev)
        else:
            self.__remove_near_data(chunk, next_, prev)
    
    def __remove_near_data(self, chunk, next_, prev):
        """ Internal function to remove a chunk that is adjacent to a chunk 
        that contains data."""

        if prev is not None and prev.is_gap():
            # The previous chunk is a gap, dissolve this node into the gap
            prev.expand(chunk.get_length())
            prev.set_next(next_)
        else:
            # Data chunks are on both sides of this chunk, convert to a gap
            gap = MemoryChunk.create_empty_chunk(chunk.get_index_first(), 
                                                 chunk.get_length())
            self._empty.append(gap)
            gap.set_previous(prev)
            gap.set_next(next_)

    def __remove_near_gap(self, chunk, next_, prev):
        """ Internal function to remove a chunk that is adjacent to a gap. """

        if prev is not None and prev.is_gap():
            # The previous and next chunks are both gaps.  Dissolve all three
            # into one big bap
            self._empty.remove(next_)
            prev.set_next(next_.get_next())
            prev.expand(chunk.get_length() + next_.get_length())
        else:
            next_.shrink(-chunk.get_length())
            next_.set_previous(prev)
        # TODO: Store zeros in this place in the vbo maybe

    def __remove_last(self, chunk, next_, prev):
        """ Internal function to remove the last memory chunk. """

        if prev is not None and prev.is_gap():
            # This chunk is the last and the previous is a gap, so make the
            # last chunk be the previous previous
            self._empty.remove(prev)
            if prev.get_previous() is not None:
                # TODO: shouldn't be two gaps next to each other but 
                # make sure that cannot happen.
                prev.get_previous().set_next(None)
            self._last = prev.get_previous()
            self._index_last -= chunk.get_length() + prev.get_length()
        else:
            # Dump this chunk and make the previous the new last chunk
            if prev is not None:
                prev.set_next(None)
            self._last = prev
            self._index_last -= chunk.get_length()
    
    def remove_gap(self, gap):
        """ Remove the input empty chunk from the internal empty storage 
        array. """

        self._empty.remove(gap)

    def defrag_quick(self):
        """ Refactor the first empty chunk in the batch. """

        if len(self._empty) == 0: return False

        # Pop the first gap and link the prev and next chunks together
        removed = self._empty.pop(0)
        removed.get_next().set_previous(removed.get_previous())
        rlength = removed.get_length()

        accum = [] ; length = 0
        current = removed.get_next()
        while current is not None and current.is_gap() and length < MemoryManager.MAX_REFACTOR:
            current.shift(-rlength)
            accum.append(current.get_data())
            length += current.get_length() / MemoryChunk.MAX_FLOAT_COUNT
            current = current.get_next()

        if current is None:
            # TODO: Need to flatten the accumulated array
            self.__store_to_gpu(removed.get_index_first(), accum)
            self._index_last -= rlength
        else:
            
            accum.append(_zeros(rlength))
            self.__store_to_gpu(removed.get_index_first(), accum)
            if current.is_gap():
                # Next chunk is already a gap, so just make that gap bigger
                current.shrink(-rlength)
            else:
                # Add empty bubble at the end of the accumulated refactor data
                bubble = MemoryChunk.create_empty_chunk(current.get_previous().get_index_last(), rlength)
                self._empty.insert(0, bubble)
                bubble.set_previous(current.get_previous())
                bubble.set_next(current)

        return True

    def defrag_full(self):
        """ Defragment the entire batch until all the gaps are removed. """

        if len(self._empty) == 0: return False
        
        removed = self._empty.pop(0)
        removed.get_next().set_previous(removed.get_previous())
        rlength = removed.get_length()

        accum = [] ; length = 0 ; done = False
        current = removed.get_next()
        while not done:
            if current is None: # Hit the end of the chunk chain
                # TODO: Need to flatten the accumulated array
                self.__store_to_gpu(removed.get_index_first(), accum)
                self._index_last -= rlength
                done = True
            elif current.is_gap():
                removed = self._empty.pop(0)
                removed.get_next().set_previous(removed.get_previous())
                rlength += removed.get_length()
            else:
                current.shift(rlength)
                accum.append(current.get_data())
                length += current.get_length() / MemoryChunk.MAX_FLOAT_COUNT #TODO: Do we need
            current = current.get_next()

        return True

    def destroy(self):
        """ Kill this memory manager. """

        self._vbo.destroy()
        self._vao.destroy()
        self._data = None
        self._empty = None

class Batch(object): pass

class StaticBatch(Batch):
    """ The StaticBatch class if the batch system for objects whose vertex data
    generally does not change on a regular basis. """

    def __init__(self, manager, world):
        """ Constructor.

        Parameters:
        ===========
        * manager (:obj:`MemoryManager`): The manager that is responsible for 
          managing this batch's memory.
        """

        self._manager = manager
        self._world = world
        self._entity_map = dict()
        self._mtype = world.cm.get_type_for(MeshComponent)
        self._get_mesh = partial(world.cm.get, component_type=self._mtype)
        print self._get_mesh

    def add(self, entity):

        # Get the entity's mesh data
        component = self._get_mesh(entity.get_id())
        # TODO: Once the meshbundle has been pulled for the input entity, we
        #       must transform (interleave) the data into a flattened array.
        data = component.bundle.pack()
        # Create a memory chunk for the data
        self._manager.allocate(data)
        # NOTE: As this is static data, make sure to transform the data first
        # Add the data to the master array

    def remove(self, entity):
        """ Remove the input `entity` from this batch. """

        if entity in self._entity_map:
            chunk = self._entity_map[entity]
            self._manager.remove(chunk)
            del self._entity_map[entity]

    def defrag(self, full=False):
        """ Defragment / Refactor this batch's memory array. """

        if full: return self._manager.defrag_full()
        return self._manager.defrag_quick()

    def destroy(self):
        """ Kill this batch and free the linked memory in this batch's 
        manager. """

        self._manager.destroy()
        
    def get_vao(self):
        """ Retrieve the Vertex Array Object associated with this batch. """
        
        return self._manager._vao

class DynamicBatch(Batch):
    """ Handles batches for mesh data that is constantly being altered. """

    MAX_VERTEX_COUNT = 40000

    def __init__(self):
        """ Constructor. """

        self._manager = MemoryManager(DynamicBatch.MAX_VERTEX_COUNT)
        self._vao = None
        self._vbo = None

    def add(self, entity): pass

    def remove(self, entity): pass
    
    def defrag(self, full=False):
        """ Defragment / Refactor this batch's memory array. """

        if full: return self._manager.defrag_full()
        return self._manager.defrag_quick()

    def destroy(self): pass

if __name__ == "__main__":

    chunks = [] ; start = 0
    for _ in xrange(10):
        test_size = np.random.randint(0, 30)
        test_data = np.random.uniform(size=test_size)
        chunks.append(MemoryChunk.create_data_chunk(start, test_data))
        start += test_size

    for chunk in chunks:
        print chunk
