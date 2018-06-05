from maths import Vector2f, make_float_array
from font import Font

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

    def __init__(self, space_width, fontsize, max_len):

        self._space = space_width * fontsize
        self._max_len = max_len
        self._len = 0
        self._words = []

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

    def get_text(self):

        return self._text
    
    text = property(get_text, doc=get_text.__doc__)

    def get_fontsize(self):

        return self._fontsize
    
    fontsize = property(get_fontsize, doc=get_fontsize.__doc__)

    def get_length(self):

        return self._max_line_len

    def get_centered(self):

        return self._centered
    
    centered = property(get_centered)

class _MeshCreater(object):

    def __init__(self, font):

        self._font = font

    def create(self, text):

        lines = self.__create_structure(text)
        data = self.__load_structure(text, lines)
        return data

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

        return make_float_array(vertices), make_float_array(coords)
    
    def __add_vertices(self, cursor_x, cursor_y, glyph, fontsize, vertices):
        """ Add the vertices associated with the input glyph to the array. """

        p1 = Vector2f(cursor_x, cursor_y) + glyph.offset*fontsize
        p2 = p1 + glyph.size*fontsize

        # Convert to device space
        x1 =  2 * p1.x - 1
        y1 = -2 * p1.y + 1
        x2 =  2 * p2.x - 1
        y2 =  2 * p2.y + 1

        vertices += [x1,y1, x1,y2, x2,y2, x2,y2, x2,y1, x1,x2]

    def __add_coords(self, glyph, coords):
        """ Add the texture coordinates associated with the glyph into the 
        array. """

        x1, y1 = glyph.tex_start
        x2, y2 = glyph.tex_stop

        coords += [x1,y1, x1,y2, x2,y2, x2,y2, x2,y1, x1,y1]

class TextManager(object):
    """ The TextManager class is responsible for handling the creation of 
    text to be displayed on the screen. """

    def __init__(self, app):

        self._app = app

        self._fonts =  {}
        self._loaders = {}
        self._texts = {}

    def add_font(self, font):
        """ Add a new font to this manager. """

        self._fonts[font.name] = font
        self._loaders[font] = _MeshCreater(font)

    def load_font(self, name, font_filename, texture_filename):

        texture = None
        font = Font(name, font_filename, texture)
        self.add_font(font)

        return font

    def get_font(self, name):

        return self._fonts.get(name, None)

    def get_app(self):
        """ Retrieve the app that own's this manager. """

        return self._app

    app = property(get_app, doc=get_app.__doc__)

if __name__ == "__main__":

    from resource import ResourceManager

    rm = ResourceManager()
    filename = rm.path + "/fonts/berlin.fnt"

    tm = TextManager(None)
    font = tm.load_font("Berlin", filename, None)

    msg = "Hello World!"
    pos = Vector2f(0, 0)
    text = Text("Hello World!", font, 12, pos, 200)

    v, t =tm._loaders[font].create(text)
    print v
    print t