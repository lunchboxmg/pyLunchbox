class _Word(object): pass

class _Line(object): pass

class Text(object): pass

class _MeshCreater(object): pass

class TextManager(object):
    """ The TextManager class is responsible for handling the creation of 
    text to be displayed on the screen. """

    def __init__(self, app):

        self.app = app

        self.fonts =  {}
        self.texts = {}