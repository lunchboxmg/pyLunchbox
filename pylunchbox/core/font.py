""" The font module. """

from maths import Vector2f
import device

class Glyph(object):

    def __init__(self, ascii_, offset_x, offset_y, size_x, size_y, tx, ty,
                 tsize_x, tsize_y, advance_x):

        self.ascii = ascii_
        self.size = Vector2f(size_x, size_y)
        self.offset = Vector2f(offset_x, offset_y)
        self.tpos = Vector2f(tx, ty)
        self.tsize = Vector2f(tsize_x, tsize_y)
        self.advance_x = advance_x

_LINE_HEIGHT = 0.03
ASCII_SPACE = 32 # Ascii value for the space glyph (which is empty)

# Padding index values
PAD_TOP = 0
PAD_LEFT = 1
PAD_BOT = 2
PAD_RIGHT = 3
DPAD = 8

class FontFile(object):

    def __init__(self, filename):

        self._aspect = device.window.get_aspect()
        self._data = dict()
        self._values = dict()

        self._padding = [0, 0, 0, 0]
        self._pad_width = 0
        self._pad_height = 0

        self._vpps = 0
        self._hpps = 0
        self._img_width = 0

    def load(self, filename):

        values = self.values

        with open(filename, "r") as fin:
            for uline in fin:

                which = self.__process_line(uline.strip("\n"))
                if which == "char":
                    glyph = self.__load_glyph()
                    if glyph is None: continue
                    self._data[glyph.ascii] = glyph
                if which == "info":
                    padding = map(int, values["padding"].split(","))
                    self._padding = padding
                    self._pad_width = padding[1] + padding[3]
                    self._pad_height = padding[0] + padding[2]
                if which == "common":
                    line_height = float(values["lineHeight"]) - self._pad_height
                    self._vpps = _LINE_HEIGHT / line_height
                    self._hpps = self._vpps / self._aspect
                    self._img_size = float(values["scaleW"])

                
    def __process_line(self, line):
        """ Internal function that parsing the data within the input line 
        from the font file.

        Parameters
        ----------
        line :obj:`str`

        Returns
        -------
        :obj:`str`
            Designated what kind of information was in this line.
        """

        values = self._values
        parts = line.split(" ")

        # The first word in each line of the font file should designate what
        # what kind of information it hows.  If nothing is found, just return
        # a blank line
        try:
            which = parts.pop(0)
        except IndexError:
            return ""
        
        # Split the variable name and values found within the line
        # i.e.: id=127 x=285 ... {id:127, x:285}
        for part in parts:
            pair = part.split("=")
            if len(pair) == 2:
                new_key, new_value = pair
                # String data in the line is stored within quotation marks.
                # Since we are splitting by the " character, strings will be 
                # split amoungst several parts and we must combine them
                if "\"" in new_value:
                    is_string = True
                else:
                    is_string = False
                values[new_key] = new_value
            elif is_string:
                values[new_key] = " " + pair[0]
        
        return which

    def __load_glyph(self):

        values = self._values
        img_size = self._img_size
        p = self._padding

        ascii_ = int(values["id"])
        if ascii_ == ASCII_SPACE:
            self._space = (float(values["xadvance"]) - self._pad_width)
            self._space *= self._hpps
            return None

        # Determine the normalize texture coordinates for the glyph's
        # starting position
        x = (float(values["x"]) + p[PAD_LEFT] - DPAD)/img_size
        y = (float(values["y"]) + p[PAD_TOP] - DPAD)/img_size

        # Determine the glyph's
        w = float(values["width"]) - self._pad_width + 2*DPAD
        h = float(values["height"]) - self._pad_height + 2*DPAD
        
        # Determine the start and stop vertices of glyphs quad in scrren space.
        offset_x = (float(values["xoffset"]) + p[PAD_LEFT] - DPAD)*self._hpps
        offset_y = (float(values["yoffset"]) + p[PAD_TOP] - DPAD)*self._vpps
        qw = w*self._hpps
        qh = h*self._vpps

        # Determine the normalized texture coords of the endpoint of the
        # glyph's quad.S 
        size_x = float(w) / img_size
        size_y = float(h) / img_size

        advance_x = (float(values["xadvance"]) - self._pad_width) * self._hpps

        return Glyph(ascii_, offset_x, offset_y, qw, qh, x, y, size_x, size_y, 
                     advance_x)









class Font(object): pass

class FontShader(object): pass

class FontRenderer(object): pass