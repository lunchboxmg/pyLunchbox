""" The font module. """

from maths import Vector2f, Vector3f
import device
from glutils import *

class Glyph(object):
    """ The Glyph class containes the vertice and texture coordinate 
    information for a character in a font texture atlas. 
    
    Attributes
    ----------
    ascii : :obj:`int`
        The ascii id number for the character being represented.
    offset : :obj:`Vector2f`
        Position relative to the cursor in which to start this glyph's
        quad (top-left).
    size : :obj:`Vector2f`
        The size of the glyph's quad in screen space.
    tex_start : :obj:`Vector4f`
        The starting position (top-left) of the glyph's normalize texture 
        coordinates.
    tex_stop : : obj:`Vector2f`
        The ending position (bottom-right) of the glyph's normalize texture
        coordinates.
    advance_x : :obj:`float`
        How far to advance the cursor in the x direction.
    """

    def __init__(self, ascii_, offset_x, offset_y, size_x, size_y, tx, ty,
                 tsize_x, tsize_y, advance_x):

        self.ascii = ascii_
        self.offset = Vector2f(offset_x, offset_y)
        self.size = Vector2f(size_x, size_y)
        self.tex_start = Vector2f(tx, ty)
        self.tex_stop = Vector2f(tx + tsize_x, ty + tsize_y)
        self.advance_x = advance_x

LINE_HEIGHT = 0.03
ASCII_SPACE = 32 # Ascii value for the space glyph (which is empty)

# Padding index values
PAD_TOP = 0
PAD_LEFT = 1
PAD_BOT = 2
PAD_RIGHT = 3
DPAD = 8

class FontFile(object):

    def __init__(self, filename):

        self._aspect = 1280.0/720.0#device.window.get_aspect()
        self._data = dict()
        self._values = dict()
        self._space = 0

        self._padding = [0, 0, 0, 0]
        self._pad_width = 0
        self._pad_height = 0

        self._vpps = 0
        self._hpps = 0
        self._img_width = 0

        self.load(filename)

    def load(self, filename):

        values = self._values

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
                    self._vpps = LINE_HEIGHT / line_height
                    self._hpps = self._vpps / self._aspect
                    self._img_size = float(values["scaleW"])

        return self

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
        """ Internal function to load the data parsed from a font data line 
        into a :class:`Glyph`."""

        values = self._values
        img_size = self._img_size
        p = self._padding

        # Retrieve the ascii value and check if space, space is just sizing
        ascii_ = int(values["id"])
        if ascii_ == ASCII_SPACE:
            self._space = (float(values["xadvance"]) - self._pad_width)
            self._space *= self._hpps
            return None

        # Determine the normalize texture coordinates for the glyph's
        # starting corner's position
        x = (float(values["x"]) + p[PAD_LEFT] - DPAD)/img_size
        y = (float(values["y"]) + p[PAD_TOP] - DPAD)/img_size

        # Determine the glyph's size
        w = float(values["width"]) - self._pad_width + 2*DPAD
        h = float(values["height"]) - self._pad_height + 2*DPAD
        
        # Determine the starting vertex (upper left) for starting this glyph's
        # quad and the end vertex (lower right) of the vertex
        offset_x = (float(values["xoffset"]) + p[PAD_LEFT] - DPAD)*self._hpps
        offset_y = (float(values["yoffset"]) + p[PAD_TOP] - DPAD)*self._vpps
        qw = w*self._hpps
        qh = h*self._vpps

        # Determine the normalized texture coords of the endpoint of the
        # glyph's quad.S 
        size_x = float(w) / img_size
        size_y = float(h) / img_size

        # How far the cursor need to move to signify the start of the next
        # glyph
        advance_x = (float(values["xadvance"]) - self._pad_width) * self._hpps

        return Glyph(ascii_, offset_x, offset_y, qw, qh, x, y, size_x, size_y, 
                     advance_x)

    def get_glyph(self, ascii_):
        """ Get the glyph for the input character's ascii value. """

        return self._data.get(ascii_, None)

    def get_space(self):
        """ Retrieve the size of the space (" ") character in glyph space. """

        return self._space
    
    def __getitem__(self, value):
        """ Overloaded. """

        return self._data.get(value)

class Font(object):

    def __init__(self, name, filename, texture):

        self._name = name
        self._metadata = FontFile(filename)
        self._texture = texture

    def get_space(self):

        return self._metadata._space

    def get_name(self):
        """ Retrieve the name given to this font. """

        return self._name

    name = property(get_name, doc=get_name.__doc__)

    def get_texture(self):
        """ Retrieve the font texture atlas associated with this font. """

        return self._texture

    texture = property(get_texture, doc=get_texture.__doc__)

    def __getitem__(self, name):

        return self._metadata[name]


class FontShader(ShaderProgram):

    FILE_VS = "/res/shaders/font.vs"
    FILE_FS = "/res/shaders/font.fs"

    def __init__(self, path):
        super(FontShader, self).__init__("FONT", path + FontShader.FILE_VS,
                                         path + FontShader.FILE_FS)

        self.transform = UniformVector3f("transform")
        self.color = UniformVector3f("color")
        self.outline_color = UniformVector3f("outline_color")

        self.store_locations(self.transform, self.color, self.outline_color)

class FontRenderer(object):

    def __init__(self, app):

        self.app = app
        self._shader = FontShader(app.path)

    def render(self, texts):

        self.prepare()
        for font, batch in texts.iteritems():
            glActiveTexture(GL_TEXTURE0)
            font.get_texture().bind()
            for text in batch:
                self._shader.transform.load(text.position.x, text.position.y, 1.0)
                vao = text.get_vao()
                vao.bind()
                vao.enable(2)
                glDrawArrays(GL_TRIANGLES, 0, text.mesh_size)
                vao.disable()
                vao.unbind()
            font.get_texture().unbind()
        self.finish()

    def prepare(self):
        """ Prepare the device for rendering. """

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDisable(GL_DEPTH_TEST)
        #glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        self._shader.start()
        self._shader.color.load(1, 1, 1)
        self._shader.outline_color.load(0, 0, 0)

    def finish(self):

        self._shader.stop()
        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)

    def destroy(self):

        self._shader.destroy()
    
        




if __name__ == "__main__":

    import inspect
    import os

    filename = inspect.getframeinfo(inspect.currentframe()).filename
    this_path = os.path.dirname(os.path.abspath(filename))
    path_parts = this_path.split("\\")
    while path_parts[-1] != "pylunchbox":
        path_parts.pop()
    path = "/".join(path_parts)

    filename = path +"/res/fonts/berlin.fnt"
    test_font = Font("Berlin", filename, None)
    print test_font[ord("B")]