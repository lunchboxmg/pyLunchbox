from random import randint

from pylunchbox.core import ecs

class StatComponent(ecs.Component):

    def __init__(self, value=-1):

        self.value = value

class DiceBlueprint(ecs.ComponentBlueprint):

    def __init__(self, component_type, num, sides, base):

        super(DiceBlueprint, self).__init__(component_type)
        self._num = num
        self._sides = sides
        self._base = base

    def roll(self):

        result = self._base
        for _ in xrange(self._num):
            result += randint(1, self._sides)
        return result

    def create(self):

        return self._type(self.roll())

class StatBlueprint(DiceBlueprint):

    def __init__(self, component_type, num, sides, base):

        super(StatBlueprint, self).__init__(component_type, num, sides, base)

    def create(self):

        return StatComponent(self.roll())

if __name__ == "__main__":

    comp1 = (1, 3)
    print comp1.value
