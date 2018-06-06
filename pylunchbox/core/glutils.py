from OpenGL.GL import *
import OpenGL.GL.shaders as GLShaders
from ctypes import c_void_p

__author__ = "lunchboxmg"

from maths import Vector2f, Vector3f, concatenate

UNIFORM_NOT_FOUND = -1

class UniformBase(object):
    """ The UniformBase class is the base class for the various types of
    shader uniforms.

    Shader uniforms are global GLSL variables that act as parameters that
    the user of a shader program can pass to that program. """

    def __init__(self, name):

        self._name = name
        self._location = UNIFORM_NOT_FOUND

    def store_location(self, id_program):
        """ Store the variable location of this shader uniform. """

        self._location = glGetUniformLocation(id_program, self._name)
        if self._location == UNIFORM_NOT_FOUND:
            print "ERROR: No uniform variable [{:s}] found!".format(self._name)

    def get_name(self):
        """ Retrieve this uniform variable's name. """

        return self._name

    def get_location(self):
        """ Retreive the variable location of this shader uniform. """

        return self._location

class UniformFloat(UniformBase):
    """ The UniformFloat class is used to store a float variable into the
    shader program. """

    def __init__(self, name):
        super(UniformFloat, self).__init__(name)
        self._value = None
        self._used = False

    def load(self, value):
        """ Load the input `value` into this shader uniform. """

        if (not self._used or self._value != value):
            glUniform1f(self._location, value)
            self._used = True
            self._value = value

class UniformBool(UniformFloat):
    """ The UniformBool class is used to store a boolean variable into the
    shader program. """

    def __init__(self, name):
        super(UniformBool, self).__init__(name)

    def load(self, value):
        """ Load the input `value` into this shader uniform. """

        super(UniformBool, self).load(1.0 if value else 0.0)

class UniformVector3f(UniformBase):
    """ The UniformVector3f class is used to store a Vector3f into the
    shader program uniforms. """

    def __init__(self, name):
        super(UniformVector3f, self).__init__(name)
        self._x = 0
        self._y = 0
        self._z = 0
        self._used = False

    def load(self, x, y, z):
        """ Load the 3 input values into the shader vec3f uniform. """

        if (not self._used or self._x != x or self._y != y or self._z != z):
            self._x = x
            self._y = y
            self._z = z
            self._used = True
            glUniform3f(self._location, x, y, z)

class UniformMatrix4f(UniformBase):
    """ The UniformMatrix4f class is used to store a 4x4 float matrix (16 float
    array) into the shader program. """

    def load(self, matrix):
        """ Load the input `matrix` into this shader. """

        glUniformMatrix4fv(self._location, 1, GL_FALSE, matrix)

class UniformLights(UniformBase):
    
    def load(self, lights):
        
        data = concatenate([light.to_array() for light in lights])
        glUniformMatrix4fv(self._location, len(lights), GL_FALSE, data)
            
            
class ShaderProgram(object):
    """ The ShaderProgram is the base class for creating OpenGL shader
    programs. """

    def __init__(self, name, fn_vertex, fn_fragment):
        """ Constructor.

        Parameters:
        ===========
        * name (:obj:`string`): Name of this shader.
        * fn_vertex (:obj:`string`): File path and name of the vertex shader
          source.
        * fn_fragment (:obj:`string`): File path and name of the fragment
          shader source.
        """

        self._name = name
        self._source = {}
        self._id_vertex = self.__load_shader(fn_vertex, GL_VERTEX_SHADER)
        self._id_fragment = self.__load_shader(fn_fragment, GL_FRAGMENT_SHADER)
        self._id_program = self.__create_program()
        
    def start(self): glUseProgram(self._id_program)
    def stop(self): glUseProgram(0)

    def store_locations(self, *uniforms):
        """ Store the locations for the input collection of uniforms. """

        for uniform in uniforms:
            uniform.store_location(self._id_program)
        glValidateProgram(self._id_program)

    def __bind_attribute(self, attrib, name):
        """ Bind the input attribute. """

        glBindAttribLocation(self._id_program, attrib, name)

    def __load_shader(self, filename, type_):
        """ Loader the input shader source file for the input `type`. """

        self._source[type_] = source = self.__get_shader_source(filename)
        return self.__compile_shader_source(source, type_)

    def __get_shader_source(self, filename):
        """ Load the source from the input `filename` into a string. """

        source = ""
        with open(filename, "r") as fo:
            source = fo.read()
        return str.encode(source)

    def __compile_shader_source(self, source, type_):
        """ Compile the input shader `source` code. """

        id_ = GLShaders.compileShader(source, type_)
        if self.__check_compile_errors(id_, GL_COMPILE_STATUS):
            return id_
        print "ERROR: Could not compile shader code" # TODO:
        exit(-1)

    def __check_compile_errors(self, id_, type_):
        """ Check the compiled source on the GPU for errors. """

        if not glGetShaderiv(id_, GL_COMPILE_STATUS):
            info = glGetShaderInfoLog(id_)
            print info
            # TODO: PRINT ERROR
            return False
        return True

    def __create_program(self):
        """ Create the shader program on the GPU. """

        shaders = [self._id_vertex, self._id_fragment]
        return GLShaders.compileProgram(*shaders)

    def destroy(self):
        """ Unload the shader from the GPU. """

        glUseProgram(0)
        glDetachShader(self._id_program, self._id_vertex)
        glDetachShader(self._id_program, self._id_fragment)
        glDeleteShader(self._id_vertex)
        glDeleteShader(self._id_fragment)
        glDeleteProgram(self._id_program)

    def get_id(self):
        """ Retrieve the shader program id. """

        return self._id_program

class Vao(object):
    """ The VAO class is basically designed to make using Vertex Array Objects
    `prettier`. """

    def __init__(self):

        self._id = glGenVertexArrays(1)
        self._temp_num_attribs = -1
        self._vbos = []

    def bind(self):
        """ Tell the GPU that we are going to use this VAO. """

        glBindVertexArray(self._id)

    def unbind(self):
        """ Tell the GPU that we are done using this VAO. """

        glBindVertexArray(0)

    def enable(self, num_attribs):
        """ Enable the input number of attributes associated with this buffer
        object. """

        self._temp_num_attribs = num_attribs
        for i in xrange(num_attribs): glEnableVertexAttribArray(i)

    def disable(self):
        """ Disable the attributes associated with this buffer object. """

        for i in xrange(self._temp_num_attribs): glDisableVertexAttribArray(i)

    def destroy(self, include_vbos=False):
        """ Delete this VAO from the GPU. """

        if include_vbos:
            for vbo in self._vbos: vbo.destroy()
        glDeleteVertexArrays(1, [self._id])

    def attach_vbo(self, vbo):
        """ Attach a Vertex Buffer Object to this VAO. """

        self._vbos.append(vbo)

    def get_id(self):
        """ The the GPU id assigned to this VAO. """

        return self._id

class Vbo(object):
    """ The Vbo class respresents the OpenGL Vertex Buffer Object.

    The VBO provides a method of uploading vertex data associated with a VAO
    to the GPU. """

    def __init__(self, size=None):
        """ Constructor. """

        self._id = glGenBuffers(1)

        self._usage = None
        self._temp_target = -1

    def bind(self, target):
        """ Tell the GPU that we are going to use utilize this buffer object.

        Parameters:
        ===========
        * target (:obj:`int`): Specifies the target to which the buffer object
          is boundself.

        NOTE: See https://www.khronos.org/registry/OpenGL-Refpages/gl4/html/glBindBuffer.xhtml
        """

        glBindBuffer(target, self._id)
        self._temp_target = target

    def unbind(self):
        """ Tell the GPU we are done using this buffer object. """

        glBindBuffer(self._temp_target, 0)

    def allocate(self, size, usage, lengths=None):
        """ Preallocate the VBO to the input `size`. """
        
        glBufferData(self._temp_target, size, c_void_p(0), usage)
        self._usage = usage
        
        if lengths:
            stride = sum(lengths) * 4 # TODO
            total = 0
            for i, length in enumerate(lengths):
                glVertexAttribPointer(i, length, GL_FLOAT, GL_FALSE, 
                                      stride, c_void_p(total*4))
                total += length

    def upload(self, target, data, usage=None):
        """ Upload the `input` data to the GPUself.

        Parameters
        ----------
        target : :obj:`int`
            Specifies the target to which the buffer object is bound for.
        data : :obj:`ndarray`
            Numpy array of the data being pushed to the GPU.
        usage : :obj:`int`
            Specifies the expected usage pattern of the data being stored.

        NOTE: see https://www.khronos.org/registry/OpenGL-Refpages/gl4/html/glBufferData.xhtml
        """
        
        if usage is not None: self._usage = usage
        if self._usage is None: 
            m = "ERROR: Usage flag has not been set for this VBO."
            raise TypeError(m)
        glBufferData(target, data.nbytes, data, self._usage)

    def upload_sub(self, offset, data):
        """ Upload the input data to a portion of this buffer object.

        Parameters
        ----------
        target : :obj:`int`
            Specifies the target buffer object. The symbolic constant must be 
            GL_ARRAY_BUFFER, GL_ELEMENT_ARRAY_BUFFER, GL_PIXEL_PACK_BUFFER, or 
            GL_PIXEL_UNPACK_BUFFER.
        offset : :obj:`int`
            Specifies the offset into the buffer object's data store where 
            data replacement will begin, measured in bytes.
        size : :obj:`int`
            Specifies the size in bytes of the data store region being replaced.
        data : :obj:`ndarray`
            Specifies the new data that will be copied into the data store.

        NOTE: https://www.khronos.org/registry/OpenGL-Refpages/gl4/html/glBufferSubData.xhtml
        """

        datatype_size = data.nbytes / data.size
        glBufferSubData(self._temp_target, offset*datatype_size, data.nbytes, data)

    def destroy(self):
        """ Tell the GPU that we are done using this buffer object. """

        glDeleteBuffers(1, [self._id])
        
def create_batch_buffer(size, layout, usage):
    """ Creates a vertex array and buffer for a batch.
    
    Parameters
    ----------
    size : :obj:`int`
        The size in bytes that buffer.
    layout : :obj:`list` of :obj:`int`
        List of the sizes of each component of the vertex data.\n 
        i.e., [3, 2, 3] => v(x,y,z), vt(s,t), vn(x,y,z)
    usage : :obj:`int`
        Specifies the expected usage pattern of the data being stored.
        
    Returns
    -------
    :class:`Vao`, :class:`Vbo`
    """
    
    vao = Vao()
    vao.bind()

    vbo = Vbo()
    vbo.bind(GL_ARRAY_BUFFER)
    vbo.allocate(size, usage, layout)
    vao.attach_vbo(vbo)
    
    vbo.unbind()
    vao.unbind()
    
    return vao, vbo
