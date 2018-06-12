from OpenGL.GL import *
from PIL import Image as _Image
from numpy import array as _array, uint8 as UINT8
import imageio

__author__ = "lunchboxmg"

from material import ColorRGB, ColorRGBA
from maths import make_float_array, Vector2f

class Texture2D(object):
    """ The Texture2D class houses the links between a local image and its 
    texture reference on the GPU. """
   
    def __init__(self, name, image):
        """ Constructor.

        Parameters
        ----------
        name : :obj:`str`
            The name associated with this texture for lookup.
        image : :obj:`ImageData`
            The data and parameters for the image this texture uses.
        """
        
        self._name = name
        self._image = image
        self._id = glGenTextures(1)

    def bind(self):
        """ Let the gpu know that the rendered is going to use this 
        texture. """

        glBindTexture(GL_TEXTURE_2D, self._id)
    
    def unbind(self):
        """ Let the gpu know that the renderer is done using this texure. """
        
        glBindTexture(GL_TEXTURE_2D, 0)

    def get_id(self):
        """ Retrieve the device's id for this texture. """
        
        return self._id

    id = property(get_id, doc=get_id.__doc__)

    def get_name(self):
        """ Retrieve the name associated with this texture. """

        return self._name

    name = property(get_name, doc=get_name.__doc__)

    def get_image(self):
        """ Retrieve the image associated with this texture. """

        return self._image

    image = property(get_image, doc=get_image.__doc__)

    def destroy(self):
        """ Kill this texture, removing it from device. """

        glDeleteTextures([self._id])

class TextureAtlas2D(Texture2D):

    def __init__(self, name, image, xsize, ysize):
        super(TextureAtlas2D, self).__init__(name, image)
        self._xsize = xsize
        self._ysize = ysize
        self._usize = float(xsize) / float(image.width)
        self._vsize = float(xsize) / float(image.width)

    def get_uv_for(self, x, y):
        """ Get the upper right and lower left coordinate of the box that 
        corresponds to the input (x, y) coordinate. """

        x1 = self._usize * x
        y1 = (1.0 - self._vsize * y)
        x2 = x1 + self._usize
        y2 = y1 - self._vsize

        r = [(x1,y1), (x1,y2), (x2,y1), (x2,y1), (x1,y2), (x2,y2)]
        r = [(x1,y1), (x2,y1), (x1,y2), (x1,y2), (x2,y1), (x2,y2)]


        return [Vector2f(x, y) for (x, y) in r]

TEXTURE_WRAP = {"clamp_to_edge": GL_CLAMP_TO_EDGE, 
                "clamp_to_border": GL_CLAMP_TO_BORDER, 
                "repeat": GL_REPEAT, 
                "mirrored_repeat": GL_MIRRORED_REPEAT, 
                "mirror_clamp_to_edge": GL_MIRROR_CLAMP_TO_EDGE}

class TextureBuilder(object):
    """ The TextureBuilder is a helper class for sending image data to the 
    GPU. Each setter method also returns the builder so that method calls 
    can be chained. """

    def __init__(self):
        """ Constructor. """

        self._mipmap = False
        self._filtered = False
        self._wrapped = GL_REPEAT
        self._border_color = ColorRGBA(0, 0, 0, 0)

    def is_mipmap(self):
        """ Determine if the mipmap parameter of this texture is set. """

        return self._mipmap

    def set_mipmap(self, value=True):
        """ A mipmap is an ordered set of arrays representing the same image 
        at progressively lower resolutions. """

        self._mipmap = value
        return self

    def is_filtered(self):
        """ Determine if the texture is filtered (NEAREST) or not (LINEAR) """

        return self._filtered

    def set_filtered(self, value=True):
        """ The texture minifying function is used whenever the level-of-detail 
        function used when sampling from the texture determines that the 
        texture should be minified. 
        
        LINEAR = False , NEAREST = True. """

        self._filtered = value
        return self

    def get_wrapped(self):
        """ Retrieve the wrap parameter for texture coordinates. """

        return self._wrapped

    def set_wrapped(self, value):
        """ Sets the wrap parameter for texture coordinates. """

        if isinstance(value, str):
            if value.lower() in TEXTURE_WRAP.iterkeys():
                self._wrapped = TEXTURE_WRAP[value.lower()]
        else:
            if value in TEXTURE_WRAP.itervalues():
                self._wrapped = value
        return self

    def get_border_color(self):
        """ Retrieve the border color if the wrap parameter is set to 
        GL_CLAMP_TO_BORDER. """

        return self._border_color

    def set_border_color(self, color):
        """ Set the border color if the wrap parameter is set to 
        GL_CLAMP_TO_BORDER. """
        self._border_color[:4] = color[:4]
        return self

class ImageData(object):
    """ The ImageData class houses the data and parameters of an image. """

    def __init__(self, name, data):

        self._name = name
        self._data = data
        self._height, self._width, self._channels = data.shape

    def load_to_gpu(self):
        """ Load this image onto the GPU. """

        glTexImage2D(GL_TEXTURE_2D, 0, self.format, self._width, self._height, 
                     0, self.format, GL_UNSIGNED_BYTE, self._data.flatten())

    def get_name(self):
        """ Retrieve the name associated with this image. """

        return self._name

    name = property(get_name, doc=get_name.__doc__)

    def get_height(self):
        """ Retrieve the pixel height of the image. """

        return self._height

    height = property(get_height, doc=get_height.__doc__)

    def get_width(self):
        """ Retrieve the pixel width of the image. """

        return self._width

    width = property(get_width, doc=get_width.__doc__)

    def get_channels(self):
        """ Retrieve the number of channels associated with a pixel of the 
        image. """

        return self._channels
    
    channels = property(get_channels, doc=get_channels.__doc__)

    def get_format(self):
        """ Retrieve the internal format of this image. """

        if self._channels == 3:
            return GL_RGB
        elif self._channels == 4:
            return GL_RGBA

    format = property(get_format, doc=get_format.__doc__)

    def get_pixel(self, x, y):
        """ Retrieve the values of each channel for the given pixel. """

        return self._data[y, x]

class TextureManager(object):
    
    def __init__(self, world):
        """ Constructor. """
        
        self.world = world
        self._textures = {} # Local Texture cache
        self._images = {} # Local image cache

    def load_image(self, name, filename, format=None, **kwargs):
        """ Load the image data into the app. 

        This function utilizes the imageio imread function.  Parameters for a 
        imread call can also be used in this function call.
        
        Parameters
        ----------
        name : :obj:`str`
            A string used to lookup the image in the internal cache.
        filename : :obj:`str`
            The name of the image file.
        format : :obj:`str`, optional
            The format to use to read the file. By default imageio selects the 
            appropriate for you based on the filename and its contents.
        kwargs: ...
            Further keyword arguments are passed to the reader base on format.
        """

        image = ImageData(name, imageio.imread(filename, format=format, **kwargs))
        self._images[name] = image
        return image

    def load_texture(self, name, image, builder):
        """ Load the texture to the gpu. 
        
        Parameters
        ----------
        name : :obj:`str`
            The name associated with the texure being loaded to be used for 
            fast lookup.
        image : :class:`ImageData`
            The data and parameters for the image this created texture will 
            use.
        builder : :class:`TextBuilder`
            Set of flags dictating how the created texture will be loaded into 
            the GPU.
        """

        texture = Texture2D(name, image)
        self.__build_texture(texture, builder, image)
        self._textures[name] = texture
        return texture

    def load_texture_atlas(self, name, image, builder, xsize, ysize):
        """ Load the texture atlas to the GPU. 
        
        Parameters
        ----------
        name : :obj:`str`
            The name associated with the texure being loaded to be used for 
            fast lookup.
        image : :class:`ImageData`
            The data and parameters for the image this created texture will 
            use.
        builder : :class:`TextBuilder`
            Set of flags dictating how the created texture will be loaded into 
            the GPU.
        xsize : :obj:`int`
            The size of an item in the x-direction (horizontal).
        ysize : :obj:`int`
            The size of an item in the y-direction (vertical).
        """

        texture = TextureAtlas2D(name, image, xsize, ysize)
        self.__build_texture(texture, builder, image)
        self._textures[name] = texture
        return texture

    def __build_texture(self, texture, builder, image):
        """ Internal function to set the parameters of the texture using the 
        values from the input TextureBuilder object. """

        texture.bind()
        if builder.is_mipmap():
            glGenerateMipmap(GL_TEXTURE_2D)
            if builder.is_filtered():
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR )
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR_MIPMAP_LINEAR)
            else:
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST_MIPMAP_NEAREST)
        elif builder.is_filtered():
			glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
			glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        else:
			glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
			glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

        wrap = builder.get_wrapped()
        if wrap == GL_CLAMP_TO_EDGE:
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        elif wrap == GL_REPEAT:
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        elif wrap == GL_CLAMP_TO_BORDER:
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
            glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, builder.get_border_color())

        image.load_to_gpu()
        texture.unbind()

    def destroy(self):
        """ Remove loaded textures from the device. """

        for t in self._textures.itervalues():
            t.destroy()
        self.textures = {}
