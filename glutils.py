from OpenGL.GL import *
import OpenGL.GL.shaders as GLShaders

from maths import Vector2f, Vector3f

UNIFORM_NOT_FOUND = -1

class UniformBase(object):
    """ The UniformBase class is the base class for the various types of
    shader uniforms.

    Shader uniforms are global GLSL variables that act as parameters that
    the user of a shader program can pass to that program. """

    def __init__(self, name):

        self._name = name
        self._location = -1

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

        if (not used or self._value != value):
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
        if value: value = 1.0
        else: value = 0.0
        super(UniformBool, self).load(1.0)

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

        if (not used or self._x != x or self._y != y or self._z != z):
            self._x = x
            self._y = y
            self._z = z
            self._used = True
            glUniform3f(self._location, x, y, z)

class UniformMatrix4f(UniformBase):
    """ The UniformMatrix4f class is used to store a 4x4 float matrix (16 float
    array) into the shader program. """

    def load(self, matrix):
        """ Load the iput `matrix` into this shader. """

        glUniformMatrix4fv(self._location, 1, GL_FALSE, matrix)

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

         self.bind_attributes()
         self.get_all_uniform_locations()

    def start(self): glUseProgram(self._id_program)
    def stop(self): glUseProgram(0)

    def store_locations(self, *uniforms):
        """ Store the locations for the input collection of uniforms. """

        for uniform in uniforms:
            uniform.store_locations(self._id_program)
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

        self._id = glGenVertexArrays()

    def bind(self):
        """ Tell the GPU that we are going to use this VAO. """

        glBindVertexArray(self._id)

    def unbind(self):
        """ Tell the GPU that we are done using this VAO. """

        glBindVertexArray(0)

    def destroy(self):
        """ Delete this VAO from the GPU. """

        glDeleteVertexArrays(self._id)

    def get_id(self):
        """ The the GPU id assigned to this VAO. """

        return self._id

class Vbo(Object):
    """ The Vbo class respresents the OpenGL Vertex Buffer Object.

    The VBO provides a method of uploading vertex data associated with a VAO
    to the GPU. """

    def __init__(self):
        """ Constructor. """

        self._id = glGenBuffers()
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

    def upload(self, target, data, usage):
        """ Upload the `input` data to the GPUself.

        Parameters:
        ===========
        * target (:obj:`int`): Specifies the target to which the buffer object
          is bound for.
        * data (:obj:`ndarray`): Numpy array of the data being pushed to the
          GPU.
        * usage (:obj:`int`): Specifies the expected usage pattern of the data
          being stored.

        NOTE: see https://www.khronos.org/registry/OpenGL-Refpages/gl4/html/glBufferData.xhtml
        """

        glBufferData(target, data.nbytes, data, usage)
