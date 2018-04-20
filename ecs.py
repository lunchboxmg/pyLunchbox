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

class Component(object):
    """ The Component class is the base class for other components. """

    def get_class(self): return self.__class__



