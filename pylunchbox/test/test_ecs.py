from . import ecs

class TestComponent(ecs.Component):

    def __init__(self, x, y):
        self.x = x
        self.y = y

if __name__ == "__main__":

    comp1 = TestComponent(1, 3)
    print comp1.x, comp1.y
