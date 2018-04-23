""" This module contains the Entity Component System (ECS).

The ECS treats entities as collections of components instead of using a super 
complex taxonomic hierarchy using inheritence.

Example:
========
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

    def get_class(self): return self.__class__

class ComponentBlueprint(object):
    """ The ComponentBlueprint class is the base class for Blueprints.

    ComponentBlueprints instruct the system on how to create new components for
    the ComponentType associated with the blueprint.

    Example:
    ========
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

        print "+++", self._index
        return self._index

    def get_index(self):
        """ Return the lookup index of this type. """

        return self._index

    def get_base(self):
        """ Retrieve the base Component of this type. """

        return self._base

class ComponentMapper(object):
    """ The component mapper serves as a container for a single specific
    component class. """

    def __init__(self, type_, size=64):
        """ Constructor. """

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

    def remove(self, entity):
        """ Remove this component type from the input `entity`. """

        component = self._contents.get(entity.get_id())
        if component is not None:
            # add to purgatory
            pass

    def has(self, entity_id):
        """ Determines in the input entity has the component that corresponds
        to this mapper. """

        if self._contents.size <= entity_id: return False
        return self._contents.get(entity_id) == None

class ComponentManager(object):
    """ The ComponentManager class manages the components created for the
    entities. """

    def __init__(self, init_num_entities=64):
        """ Constructor. """

        self._typemap = dict()
        self._types = Bag(ComponentType)
        self._mappers = Bag(ComponentMapper, init_num_entities)

    def create(self, entity_id, component_class, blueprint=None):
        """ Create a new component for the the input entity. 
        
        Parameters:
        ===========
        * entity_id (:obj:`int`): ID (index) number for the entity.
        * component_class (:obj:`Component`): Reference to the component's 
          class.
        * blueprint (:obj:`ComponentBlueprint): Blueprint used to initialize 
          the data for this new component.
        """

        self.get_mapper(component_class).create(entity_id, blueprint)

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

if __name__ == "__main__":

    cm = ComponentManager()
    ct1 = _TestComponent1(1, 2)
    mapper = cm.get_mapper(ct1.get_class())
    type_ = cm.get_type_for(ct1.get_class())
    
    bt1 = ComponentBlueprint(type_)
    print bt1
    print bt1._type
    print bt1.create()


