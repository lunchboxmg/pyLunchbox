""" The modeling module is repsonible for handling mesh data.

"""
import numpy as np
from numpy import concatenate
from time import time as _time

__author__ = "lunchboxmg"

from maths import Vector2f, Vector3f, Vector4f
from ecs import Component

class VertexVector(object):
    """ The VertexVector class contains information about a vector that 
    comprised the vertex data for a mess. """

    def __init__(self, size, dtype):

        self._size = size
        self._dtype = dtype
    
    def get_size(self):
        """ Retrieve the number of elements comprising this vertex vector. """

        return self._size

    def get_dtype(self):
        """ Retrieve the datatype associate with this vertex vector. """

        return self._dtype

V3F = VN3F = VT3F = VertexVector(3, Vector3f._UNIT)

V_EMPTY = VertexVector(0, None)
V_POSITION = 1
V_NORMAL = 2
V_TEXTURE = 4
V_TANGENT = 8
V_BITANGENT = 16

class VertexFormat(object):
    """ The VertexFormat class in an enum like class used to designation how
    the data in a mesh is organized. """

    def __init__(self):

        self._position = V_EMPTY
        self._normal = V_EMPTY
        self._texture = V_EMPTY
        self._tangent = V_EMPTY
        self._bitangent = V_EMPTY

    def set(self, which, vector):

        if which & V_POSITION:
            self._position = vector
        if which & V_NORMAL:
            self._normal = vector
        if which & V_TEXTURE:
            self._texture = vector
        if which & V_TANGENT:
            self._tangent = vector
        if which & V_BITANGENT:
            self._bitangent = vector
        
        return self

    def interleave_data(self, mesh_data):

        offset = 0
        for which in [self._position, self._normal, self._texture, self._tangent, self._bitangent]:
            size = which.get_size()
            dtype = which.dtype
            offset += size

V_BASE3 = VertexFormat().set(V_POSITION|V_NORMAL|V_TEXTURE, V3F)

class MeshData(object):
    """" Class for storing the base mesh vertex data.

    In it's current incarnation, this class can be thought of as a blueprint
    for the mesh component.  When an entity is spawned into the system with
    a mesh component, it will manuiplate the base meshdata if need be and then
    load that data onto the GPU, perserving this base data for additional
    future entities.

    As this data will be copied for the GPU, there is no need in attempting to
    interleave or organize the data at the momemnt. """

    def __init__(self, vertices, uvs, normals):

        self.vertices = vertices
        if len(uvs) == 0:
            uvs = [Vector2f(0, 0) for i in xrange(len(vertices))]
        self.uvs = uvs
        self.normals = normals
        
    def pack(self, transform=None):
        """ Pack the mesh data into a continuous array.

        Parameters
        ----------
        transform : :class:`ndarray`, optional
            Transform matrix that needs to be applied to the mesh data. 
            This is used for static models for transform does not change, so 
            the vertices are converted to model space.

        FIXME: Transforming the vertices causes at least a 10 times increase
        in packing.  Need to improve!
        """

        if transform is None:
            vs = self.vertices
        else:
            trans = transform.T
            vs = (v.transform(trans) for v in self.vertices)
        a = np.array(zip(vs, self.uvs, self.normals)).flatten()
        r = concatenate(a)
        
        return r

    def clone(self):
        """ Create a clone of this mesh data. """

        v = [v for v in self.vertices]
        u = [u for u in self.uvs]
        n = [n for n in self.normals]

        return MeshData(v, u, n)

    def get_vertex_count(self):
        """ Retrieve the number of vertices for this model. """

        return len(self.vertices)

class MeshBundle(dict):
    """ The MeshBundle class is a container object for meshes. """

    def pack(self, transform=None):
        
        r = []
        for v in self.itervalues():
            r.append(v.pack(transform))
        return concatenate(r)

    def clone(self):
        """ Create a clone. """

        new = MeshBundle()
        for k, v in self.iteritems():
            new[k] = v.clone()
        
        return new


class MeshComponent(Component):

    def __init__(self, bundle=None):

        self.bundle = bundle
    
    def __repr__(self): return self.__str__()

    def __str__(self):
        
        m = "<MeshComponent>(size={:d})"
        return m.format(len(self.bundle) if self.bundle is not None else 0)

class ModelLoader(object):
    """ The ModelLoader class is a helper class used to load mesh/model data
    from input files. """

    def __init__(self):

        self._meshes = dict()

    def load_mesh(self, name, filename):
        """ Load in a mesh from the input data file. 
        
        Parameters
        ----------
        name : :obj:`str`
            The lookup name used to save the meshes in the internal mesh 
            container.
        filename : :obj:`str`
            The path and name for the file containing the mesh's data.
        """

        ext = filename.strip().split(".")[-1]

        # Select the proper loader based upon the file extension
        if ext == "obj": # Wavefront
            mesh = self.load_mesh_from_obj(filename, True, True)
        else:
            return

        if mesh:
            if name in self._meshes:
                i = 1
                while True:
                    new_name = "{:s}_{:d}".format(name, i)
                    if new_name in self._meshes: i += 1
                    else: break
                msg = "WARNING: Mesh <{:s}> already exists, naming to <{:s}>"
                print msg.format(name, new_name)
                name = new_name
            self._meshes[name] = mesh
            return mesh

    def load_mesh_from_obj(self, filename, flip_uv=True, keep_subs=False):
        """ Load the mesh data contained in the input Wavefront file.

        Paramters
        ---------
        filename : :obj:`str`
            Path and name of the wavefront file.
        flip_uv : :obj:`bool`, default `True`
            Flag to flip the uv.y coordinates.
        keep_subs : :obj:`bool`, default `True`
            Flag to keep each subsection as seperate meshes.
            
        Returns
        -------
        :class:`MeshBundle`
        """

        pos = [] ; apos = []
        uvs = [] ; auvs = []
        norm = [] ; anorm = []
        subs = [] ; faces = []
        meshes = MeshBundle()

        with open(filename, "rb") as stream:
            for line in stream:

                tokens = line.strip().split(" ")

                if len(tokens) == 0: continue # empty line
                if len(tokens[0]) == 0: continue # blank line

                first = tokens[0].lower()

                if first[0] == "#": continue # Comment line

                if first[0] == "v": # Vertex Data
                    if len(first) == 1: # position
                        pos.append(Vector3f(tokens[1], tokens[2], tokens[3]))
                    elif first[1] == "n": # normal
                        norm.append(Vector3f(tokens[1], tokens[2], tokens[3]))
                    elif first[1] == "t": # texture coordinates
                        if flip_uv:
                            uvs.append(Vector2f(float(tokens[1]), 1 - float(tokens[2])))
                        else:
                            uvs.append(Vector2f(tokens[1], tokens[2]))

                elif first == "f": # Face index data
                    face = []
                    for token in tokens[1:]:
                        indexes = token.split("/")
                        v = []
                        v.append(int(indexes[0]))
                        # Some obj files don't have textures assigned to them
                        if len(indexes[1]) > 0: v.append(int(indexes[1]))
                        v.append(int(indexes[2]))
                        face.append(v)
                    if len(face) == 4: # Convert the quad to two tris
                        i1, i2, i3, i4 = face
                        faces.append([i1, i2, i4])
                        faces.append([i4, i2, i3])
                    else:
                        faces.append(face)

                elif first == "o" or first == "g": # Section marks
                    if len(subs) > 0:
                        subs[-1][2] = len(faces)
                    subs.append([tokens[1], len(faces), -1])

                else: continue

            if len(subs) > 0:
                subs[-1][2] = len(faces)
            else:
                subs.append([None, 0, len(faces)])

            for sub_name, start, stop in subs:
                if len(faces[start][0]) > 2:
                    for face in faces[start:stop]:
                        for pi, ui, ni in face:
                            apos.append(pos[pi - 1])
                            auvs.append(uvs[ui - 1])
                            anorm.append(norm[ni - 1])
                else:
                    for face in faces[start:stop]:
                        for pi, ni in face:
                            apos.append(pos[pi - 1])
                            anorm.append(norm[ni - 1])
                if keep_subs:
                    if sub_name in meshes:
                        print "WARNING: SubMesh <{:s}> already exist in the meshes."
                    meshes[sub_name] = MeshData(apos, auvs, anorm)
                    apos = []
                    auvs = []
                    anorm = []

        if not keep_subs: meshes["MASTER"] = MeshData(apos, auvs, anorm)

        return meshes

    def iter_meshes(self):

        return self._meshes.iteritems()

class TextureLoader(object): pass

if __name__ == "__main__":

    name = "TEST"
    filename = "../res/cube.obj"
    #filename = "res/Birch1.obj"
    #filename = "res/stall.obj"
    #filename = "res/dragon.obj"

    test_loader = ModelLoader()

    from time import time as _time
    time_start = _time()
    data = test_loader.load_mesh(name, filename)
    print data
    time_end = _time()
    print time_end - time_start

    for name, mesh in data.iteritems():
        print name, mesh.get_vertex_count()
        print mesh.vertices[0]

    name = "TEST"
    filename = "../res/Birch1.obj"
    data = test_loader.load_mesh(name, filename)

    for name, bundle in test_loader.iter_meshes():
        print name, len(bundle)

### OLD STUFF
#        if transform is not None: trans = transform.T
#        
#        vsize = self.vertices[0].size
#        tsize = self.uvs[0].size
#        nsize = self.normals[0].size
#        toffset = vsize
#        noffset = toffset + tsize
#        loffset = noffset + nsize
        
#        stride = vsize + tsize + nsize
#        r = np.empty(len(self.vertices) * stride, dtype=Vector3f._UNIT)
#
#        p = 0
#        for v, vt, vn in zip(self.vertices, self.uvs, self.normals):
#            if transform is None:
#                r[p : p + vsize] = v
#            else:
#                # FIXME: Change the transform attr to matrix attr most likely
#                r[p : p + vsize] = v.transform(trans)
#            r[p + toffset : p + noffset] = vt
#            r[p + noffset : p + loffset] = vn
#            p += stride
