""" The text module contains implementations for creating text to be displayed 
on the screen via the GPU.

NOTE: It may be of benefit to use a text batch.
"""

__author__ = "lunchboxmg"

from maths import Vector2f, Vector3f, make_float_array, empty, FLOAT32
from glutils import create_batch_buffer, GL_STATIC_DRAW, GL_ARRAY_BUFFER, GL_CLAMP_TO_EDGE
from font import Font, FontRenderer, LINE_HEIGHT
from texture import TextureBuilder

ASCII_SPACE = 32

class _Word(object):
    """ The _Word class is a helper for creating the text structure. """

    def __init__(self, fontsize):
        """ Constructor.

        Parameters
        ----------
        fontsize : :obj:`float`
            Size of the font being used for this word.
        """
        
        self._fontsize = fontsize
        self._width = 0
        self._glyphs = []

    def add_glyph(self, glyph):
        """ Add a new glyph to this word.

        Parameters
        ----------
        glyph : :class:`Glyph`
            The glyph being added to this word.
        """

        self._glyphs.append(glyph)
        self._width += glyph.advance_x * self._fontsize

    def iter_glyphs(self):
        """ Iterate over the glyphs in this word."""

        for glyph in self._glyphs: yield glyph

    def get_width(self):
        """ Retrieve the width of this word in screen space. """

        return self._width
    
    width = property(get_width, doc=get_width.__doc__)

class _Line(object):
    """ The _Line class is a helper class for create the text's structure.
    The _Line contains a collection of words. """

    def __init__(self, space_width, fontsize, max_len):
        """ Constructor.

        Parameters
        ----------
        space_width : :obj:`float`
            The width of a space glyph in screen space.
        fontsize : :obj:`float`
            The size of the font relative to the height of a line.
        max_len : :obj:`float`
            The maximum allowable length of line relative to the screen's
            width.
        """

        self._space = space_width * fontsize
        self._max_len = max_len
        self._len = 0
        self._words = []  # local word cache

    def add_word(self, word):
        """ Attempt to add a word to the line.  If adding the word causes the
        line to be too large, will return :obj:`False`. """

        word_width = word.width
        if len(self._words) > 0: word_width += self._space
        if self._len + word_width <= self._max_len:
            self._words.append(word)
            self._len += word_width
            return True
        return False

    def get_length(self):
        """ Retrieve the length of the line in screen space. """

        return self._len

    length = property(get_length, doc=get_length.__doc__)

    def get_max_length(self):
        """ Retrieve the maximum allowable length in screen space for this 
        line. """

        return self._max_len

    max_length = property(get_max_length, doc=get_max_length.__doc__)

    def iter_words(self):
        """ Iterate over the words in this line. """

        for word in self._words: yield word

    def __len__(self):
        """ Overloaded length (size) of this text. """

        return self._len


class Text(object):

    def __init__(self, text, font, fontsize, position, max_line_len,
                 centered=False, color=None):

        self._text = text
        self._font = font
        self._fontsize = fontsize
        self._position = position

        self._max_line_len = max_line_len
        self._centered = centered
        self._color = color
        self._mesh_data = None

        self._loaded = False

    def get_text(self):
        """ Retrieve the text string. """

        return self._text

    def set_text(self, text):
        """ Set the text string. """

        if text == self._text: return

        self._text = text
        if self._loaded:
            self._mesh_data.vao.destroy(True)
            if len(text) == 0:
                self._loaded = False
            else:
                self._mesh_data = self._font.loader.create(self)
    
    text = property(get_text, doc=get_text.__doc__)

    def get_font(self):
        """ Retrieve the Font class that this text uses. """

        return self._font

    font = property(get_font, doc=get_font.__doc__)

    def get_fontsize(self):
        """ Retrieve the fontsize.  The value is a multiple of LINE_HEIGHT. """

        return self._fontsize
    
    fontsize = property(get_fontsize, doc=get_fontsize.__doc__)

    def get_length(self):

        return self._max_line_len

    def get_position(self):

         return self._position

    position = property(get_position, doc=get_position.__doc__)

    def get_centered(self):

        return self._centered
    
    centered = property(get_centered)

    def get_mesh_data(self):
        """ Retrieve the TextMeshData object for this text. """

        return self._mesh_data

    def set_mesh_data(self, data):
        """ Set the TextMeshData object for this text. """

        self._mesh_data = data
        self._loaded = True

    mesh_data = property(get_mesh_data, doc=get_mesh_data.__doc__)

    def is_loaded(self):
        """ Determine if this Text object is loaded onto the GPU. """

        return self._loaded

    def destroy(self):
        """ Kill this loaded text. """

        self._mesh_data.vao.destroy(True)
        self._mesh_data = None
        self._text = ""

class TextLoader(object):

    def __init__(self, font):

        self._font = font

    def create(self, text):

        lines = self.__create_structure(text)
        pos, uvs, width, height = self.__load_structure(text, lines)
        vao = TextLoader.load_to_gpu(pos, uvs)
        return TextMeshData(vao, len(pos)//2, width, height, len(lines))

    def __create_structure(self, text):

        space = self._font.get_space()
        fontsize = text.get_fontsize()
        max_len = text.get_length()

        lines = []
        line = _Line(space, fontsize, max_len)
        word = _Word(fontsize)

        for c in text.text:
            ascii_ = ord(c)
            if ascii_ == ASCII_SPACE:
                added = line.add_word(word)
                if not added:
                    lines.append(line)
                    line = _Line(space, fontsize, max_len)
                    line.add_word(word)
                word = _Word(fontsize)
                continue
            glyph = self._font[ascii_]
            word.add_glyph(glyph)
        added = line.add_word(word)
        if not added:
            lines.append(line)
            line = _Line(space, fontsize, max_len)
            line.add_word(word)
        lines.append(line)

        return lines

    def __load_structure(self, text, lines):

        indent = 0
        cursor_x = 0
        cursor_y = 0

        vertices = []
        coords = []

        width = 0
        for line in lines:
            cursor_x = indent # TODO: Add indent parameter to text line
            if text.centered:
                cursor_x = (line.max_length - line.length) * 0.5
            for word in line.iter_words():
                for glyph in word.iter_glyphs():
                    self.__add_vertices(cursor_x, cursor_y, glyph, 
                                        text.fontsize, vertices)
                    self.__add_coords(glyph, coords)
                    cursor_x += glyph.advance_x * text.fontsize 
                cursor_x += self._font.get_space() * text.fontsize
            if cursor_x > width:
                width = line.length
            cursor_y += LINE_HEIGHT * text.fontsize

        vertices = make_float_array(vertices)
        coords = make_float_array(coords)

        return vertices, coords, width, cursor_y
    
    def __add_vertices(self, cursor_x, cursor_y, glyph, fontsize, vertices):
        """ Add the vertices associated with the input glyph to the array. """

        x1, y1 = p1 = Vector2f(cursor_x, cursor_y) + glyph.offset*fontsize
        x2, y2 = p1 + glyph.size*fontsize

        vertices += [x1,y1, x1,y2, x2,y2, x2,y2, x2,y1, x1,y1]

    def __add_coords(self, glyph, coords):
        """ Add the texture coordinates associated with the glyph into the 
        array. """

        x1, y1 = glyph.tex_start
        x2, y2 = glyph.tex_stop

        coords += [x1,y1, x1,y2, x2,y2, x2,y2, x2,y1, x1,y1]

    @staticmethod
    def load_to_gpu(pos, uvs):

        # Interleave the data
        data = empty(len(pos)*2, dtype=FLOAT32)
        di = 0 ; ci = 0
        for i in xrange(len(pos)//2):
            data[di]   = pos[ci]
            data[di+1] = pos[ci+1]
            data[di+2] = uvs[ci]
            data[di+3] = uvs[ci+1]
            di += 4 ; ci += 2

        # Create the VAO/VBOs
        vao, vbo = create_batch_buffer(data.nbytes, [2,2], GL_STATIC_DRAW)
        vbo.bind(GL_ARRAY_BUFFER)
        vbo.upload_sub(0, data)
        vbo.unbind()

        return vao

class TextMeshData(object):

    def __init__(self, vao, count, width, height, num_lines):

        self._vao = vao
        self._count = count
        self._width = width
        self._height = height
        self._num_lines = num_lines

    def get_vao(self):
        """ Retrieve the Vertex Array Object containing the data. The VAO also 
        contains the reference to the Vertex Buffer Object. """

        return self._vao

    vao = property(get_vao, doc=get_vao.__doc__)

    def get_count(self):
        """ Retrieve the vertex count. """

        return self._count

    count = property(get_count, doc=get_count.__doc__)

    def get_width(self):
        """ Retrieve the true width of the text.  This value is the size of the
        screen space that the actual vertex data takes up, not the maximum line
        length associated with the text. """

        return self._width
    
    width = property(get_width, doc=get_width.__doc__)

    def get_height(self):
        """ Retrieve the height of the text in screen space. """

        return self._height

    height = property(get_height, doc=get_height.__doc__)

    def get_num_lines(self):
        """ Retrieve the number of lines that the text takes up. """

        return self._num_lines
    
    num_lines = property(get_num_lines, doc=get_num_lines.__doc__)

class TextManager(object):
    """ The TextManager class is responsible for handling the creation of 
    text to be displayed on the screen. """

    def __init__(self, app):
        """ Constructor.

        Parameters
        ----------
        app : :class:`MainApp`
            Reference to the master application.
        """

        self._app = app # Reference to the master application

        self._fonts =  {} # local cache of fonts
        self._loaders = {} # local cahce of TextLoaders
        self._texts = {} # Local cace of Texts
        
        self._font_path = app.res.path + "/fonts/"

        self._renderer = FontRenderer(app)

    def render(self):
        """ Render the appropriate text within this manager. """

        self._renderer.render(self._texts)

    def load_font(self, name, path=None):
        """ Add a new font to this manager. 
        
        Parameters
        ----------
        name : :obj:`str`
            The name of the font.  The font's metafile and texture filename's 
            should also be this value with the appropriate file extensions. 
        path : :obj:`str`, optional
            File path the font files. If not supplied will use the default 
            `res/fonts/` path.
        """

        if path is None: path = self._font_path

        # Load in the font texture atlas
        tex_file = path + name + ".png"
        image = self._app.tex_mgr.load_image(name, tex_file)
        builder = TextureBuilder().set_filtered(True).set_wrapped(GL_CLAMP_TO_EDGE)
        texture = self._app.tex_mgr.load_texture(name, image, builder)

        # Create the font object which automatically loades the font metadata
        font_file = path + name + ".fnt"
        font = Font(name, font_file, texture)

        # Add font to local caches and create loader obj
        self._fonts[font.name] = font
        self._loaders[font] = loader = TextLoader(font)
        self._texts[font] = []
        font._loader = loader # Attempting to not expose a set option

        return font

    def add_text(self, text):

        font = text.font
        mesh_data = self._loaders[font].create(text)
        text.set_mesh_data(mesh_data)
        self._texts[font].append(text)

    def get_font(self, name):
        """ Retrieve the :obj:`Font` object for the input font name. """

        return self._fonts.get(name, None)

    def get_app(self):
        """ Retrieve the app that own's this manager. """

        return self._app

    app = property(get_app, doc=get_app.__doc__)

    def destroy(self):

        for _, batch in self._texts.iteritems():
            for text in batch:
                text.destroy()
