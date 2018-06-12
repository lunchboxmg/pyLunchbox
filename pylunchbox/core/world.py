__author__ = "lunchboxmg"

import ecs
import memory
import modeling
import texture

class World(object):
    """ The World class is the centralized class for storing data that
    currently apart of the main system. """

    def __init__(self, app):

        self._app = app

        # Initialize the ECS architecture for this world
        self._em = ecs.EntityManager(self)
        self._cm = ecs.ComponentManager(self)

        self._batch = memory.StaticBatch(memory.MemoryManager(300000), self)
        self._loader = modeling.ModelLoader()

    def get_app(self):
        """ Retrieve the reference to the master application. """

        return self._app

    app = property(get_app, doc=get_app.__doc__)

    def get_em(self):
        """ Retrieve the entity manager for this scene. """

        return self._em
    
    em = property(get_em, doc=get_em.__doc__)

    def get_cm(self):
        """ Retrieve the component manager for this scene. """

        return self._cm
    
    cm = property(get_cm, doc=get_cm.__doc__)

    def get_batch(self):
        """ Retrive the batch for this scene. """

        return self._batch

    batch = property(get_batch, doc=get_batch.__doc__)

    def get_loader(self):
        """ Retrieve the model loader for this scene. """

        return self._loader

    loader = property(get_loader, doc=get_loader.__doc__)
