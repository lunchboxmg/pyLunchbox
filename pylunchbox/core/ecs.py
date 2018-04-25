""" This module contains the Entity Component System (ECS).

The ECS treats entities as collections of components instead of using a super 
complex taxonomic hierarchy using inheritence.

Example
-------
Entity<Wolf> <- Entity<Canine> <- Entity<Animal> <- ... <- Entity<Base>
.. becomes ..
Entity<Wolf>.Components[Hostile, Trainable, Movement, ... ]

Essentially an entities is a collection of data that describes what it is.

Source of Inspiration:
https://github.com/libgdx/ashley/tree/master/ashley/src/com/badlogic/ashley
https://github.com/junkdog/artemis-odb/tree/master/artemis-core/artemis/src/main/java/com/artemis

"""

__author__ = "lunchboxmg"

from storage import Bag

class Component(object):
    """ The Component class is the base class for other components. """

    def get_class(self): 
        """ Retrieve a reference to this component's class object. """
        
        return self.__class__

    def save(self):
        """ Save the data for this component. """

        msg = "{:s}.save() must be overridden in subclasses."
        raise NotImplementedError(msg.format(self.__class__.__name__))

class ComponentBlueprint(object):
    """ The ComponentBlueprint class is the base class for Blueprints.

    ComponentBlueprints instruct the system on how to create new components for
    the ComponentType associated with the blueprint.

    Example
    -------
    CompA{x, y} .. BlueprintA{CompA() where x random(10) and y random(4,6)}
    BlueprintA.create() may return CompA(4, 4)
    """

    def __init__(self, component_type):
        """ Constructor. """

        self._type = component_type
    
    def create(self):
        """ Create a new Component from this blueprint. """

        msg = "{:s}.create() must be subclassed!".format(self)
        raise NotImplementedError(msg)

    def get_type(self):
        """ Retrieve the ComponentType associated with this blueprint. """

        return self._type

    def get_class(self):
        """ Retrieve the reference to this class. """

        return self.__class__

    def __str__(self):

        return "ComponentBlueprint<{:s}>".format(self._type._base.__name__)

class ComponentType(object):
    """ The ComponentType class describe the component ... TODO. """

    def __init__(self, index, base):

        self._index = index
        self._base = base

    def __eq__(self, other):
        """ Overloaded equality operator function. """

        if other == self: return True
        if isinstance(other, self):
            return self._base == other.get_base() and self._index == other.get_index()
        return False

    def __hash__(self):
        """ Overloaded hash function. """

        return self._index

    def get_index(self):
        """ Return the lookup index of this type. """

        return self._index

    def get_base(self):
        """ Retrieve the base Component of this type. """

        return self._base

    def __str__(self):

        m = "ComponentType<{:d}, {:s}>"
        return m.format(self._index, self._base.__name__)

class ComponentMapper(object):
    """ The component mapper serves as a container for a single specific
    component class. """

    def __init__(self, type_, size=64):
        """ Constructor. 
        
        Parameters
        ----------
        type_ : :class:`ComponentType`
            Reference to the type that this mapper holds.
        size : :obj:`int`, optional
            Initialize size of the mapper's contents.
        """

        self._type = type_
        self._contents = Bag(type, size)

    def create(self, entity_id, blueprint=None):
        """ Create a new component for this entity. """

        if self.has(entity_id):
            return self._contents.get(entity_id)
        if blueprint: component = blueprint.create()
        else: component = self._type()
        self._contents.set(component, entity_id)
        return component

    def get(self, entity_id):
        """ Get the component for the input entity's id. """

        return self._contents.get(entity_id)

    def set(self, entity_id, component):
        """ Set the component for this entity. """

        self._contents.set(component, entity_id)

    def remove(self, entity_id):
        """ Remove this component type from the input `entity`.
        
        Parameters
        ----------
        entity_id : :obj:`int`
            Identification (index) number for the entity.
        """

        component = self._contents.get(entity_id)
        if component is not None:
            # add to purgatory
            pass

    def has(self, entity_id):
        """ Determines in the input entity has the component that corresponds
        to this mapper. 

        Parameters
        ----------
        entity_id : :obj:`int`
            Identification (index) number for the entity.
        """

        if self._contents.get_size() <= entity_id: return False
        return self._contents.get(entity_id) == None
    
    def __str__(self):

        return "ComponentMapper<{:s}>".format(self._type.__name__)

class ComponentManager(object):
    """ The ComponentManager class manages the components created for the
    entities. """

    def __init__(self, world, init_num_entities=64):
        """ Initialize the ComponentManager class. 
        
        Parameters
        ----------
        world : :class:`World`
            A reference to the world instance.
        init_num_entities : :obj:`int`, optional
            Initialize the internal storage to hold this amount of entities.
        """

        self._world = world
        self._typemap = dict()
        self._types = Bag(ComponentType)
        self._mappers = Bag(ComponentMapper, init_num_entities)

    def create(self, entity_id, component_class, blueprint=None):
        """ Create a new component for the the input entity. 
        
        Parameters
        ----------
        entity_id : :obj:`int`
            Identification (index) number for the entity.
        component_class : :class:`Component`
            Reference to the component's class.
        blueprint : :class:`ComponentBlueprint`, optional
            Blueprint used to initialize the data for this new component.
        """

        return self.get_mapper(component_class).create(entity_id, blueprint)

    def get_mapper(self, component_class):
        """ Retrieve the bag of components corresponding to the input 
        component's class. """

        type_ = self.get_type_for(component_class)
        return self._mappers.get(type_.get_index())

    def get_type_for(self, component_class):
        """ Retrieve the ComponentType for the input component's class. """

        if component_class not in self._typemap:
            self._typemap[component_class] = self.__create_type(component_class)
        return self._typemap[component_class]

    def __create_type(self, component_class):
        """ Internal function that will create a new ComponentType for the 
        input compontent's class when a type if fetched for a class that does 
        not have a type associated with the class yet. """

        type_ = ComponentType(self._types.get_size(), component_class)
        self._typemap[component_class] = type_
        self._types.add(type_)
        self.__create_mapper(type_)
        return type_

    def __create_mapper(self, component_type):
        """ Internal function that will create a mapper for the input 
        component's type the first time that the mapper is requested by the
        manager. """

        index = component_type.get_index()
        mapper = ComponentMapper(component_type.get_base())
        self._mappers.set(mapper, index)

class _TestComponent1(Component):

    def __init__(self, x, y):

        self.x = x
        self.y = y

class Entity(object):
    """ The Entity class serves as a linkage point for a collection of 
    components that describes an object. """

    def __init__(self, entity_id):
        """ Constructor.

        Parameters
        ----------
        entity_id : :obj:`int`
            Identification (index) number assigned to this entity.
        """

        self._id = entity_id

    def get_id(self):
        """ Retrieve the identification of this entity that links it's 
        components. """

        return self._id
    
    def __eq__(self, other):

        if self == other: return True
        if isinstance(self, other):
            return self._id == other.get_id()
        return False

    def __hash__(self):
        
        return self._id

class EntityBlueprint(object):
    """ The EntityBlueprint class serves as instructions (factory) for creating
    a particular Entity. """

    def __init__(self, name):
        """ Constructor. """

        self._name = name
        self._blueprints = {}

    def create(self, entity_id):
        """ Create a new entity using the instructions represented by this
        blueprint.

        Parameters
        ----------
        entity_id : :obj:`int`
            Identification (index) number for the entity.
        """

        # TODO
        for blueprint in self._blueprints.itervalues():
            component = blueprint.create()

        return Entity(entity_id)
           

    def add_blueprint(self, component_type, blueprint):
        """ Add the input blueprint to this EntityBlueprint.

        Parameters
        ----------
        component_type : :class:`ComponentType`
            Which component the blueprint is for.
        blueprint : :class:`ComponentBlueprint`
            Instructions for creating the new component for a new entity.
        """
        
        if isinstance(component_type, ComponentType):
            if isinstance(blueprint, ComponentBlueprint):
                self._blueprints[component_type] = blueprint
        
    def get_name(self):
        """ Retrieve the name given to this particular blueprint. """

        return self._name

class EntityManager(object):
    """ The EntityManager class manages all the entity instances. """

    def __init__(self, world):
        """ Constructor. """

        self._world = world
        self._entities = Bag(Entity)
        self._next_id = 0
        self._blueprints = dict()

    def create(self, blueprint=None):
        """ Create a new entity.

        Parameters
        ----------
        blueprint : :class:`EntityBlueprint`
            Instructions for building new particular entities.
        """

        if isinstance(blueprint, EntityBlueprint):
            entity = blueprint.create(self._next_id)
        else:
            entity = Entity(self._next_id)
        self._entities.set(entity, self._next_id)
        self._next_id += 1

    def remove(self, entity_id): pass

    def get(self, entity_id):
        """ Retrieve the entity with the input id number. """

        return self._entities.get(entity_id)

    def add_blueprint(self, blueprint):
        """ Add an EntityBlueprint for later use.

        Parameters
        ----------
        blueprint : :class:`EntityBlueprint`
            Instructions for building new particular entities.
        """

        if isinstance(blueprint, EntityBlueprint):
            self._blueprints[blueprint.get_name()] = blueprint

    def destory(self):
        """ Kill this class and unload all the data. """

        # Loop over entities, clearing components (esp mesh data)
        pass

    



if __name__ == "__main__":

    cm = ComponentManager(None)
    ct1 = _TestComponent1(1, 2)
    mapper = cm.get_mapper(ct1.get_class())
    type_ = cm.get_type_for(ct1.get_class())
    print mapper
    
    bt1 = ComponentBlueprint(type_)
    print bt1
    print bt1._type
    #print bt1.create()
    print ct1.save()


