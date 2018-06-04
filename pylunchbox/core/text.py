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

    def __len__(self):

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

    def get_fontsize(self):

        return self._fontsize

class _MeshCreater(object):

    def __init__(self, font):

        self._font = font

    def create(self, text):

        lines = self.__create_structure(text)
        data = self.__load_structure(text, lines)

    def __create_structure(self, text):

        space = self._font.get_space()
        fontsize = text.get_fontsize()

class TextManager(object):
    """ The TextManager class is responsible for handling the creation of 
    text to be displayed on the screen. """

    def __init__(self, app):

        self.app = app

        self.fonts =  {}
        self.texts = {}