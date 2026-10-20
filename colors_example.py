from game import *
from shapes import *
import random

class colors_example(game):
    def __init__(self):
        super().__init__()

        AB = { c: random.choice([True, False]) for c in cells }

        for f in faces:
            if AB[facecells[f][0]] != AB[facecells[f][1]]:
                color = random.choice([(1,0,0),
                                       (0,1,0),
                                       (0,0,1),
                                       (1,1,0),
                                       (1,0,1),
                                       (0,1,1),
                                       (1,1,1)])
                self.add_thing(face(location=f, color=color))

class face(thing):
    layer = 0
    def draw(self,layer):
        facepolygon(layer, self.id, self.location, self.color, (1,1,1), 1)

if __name__ == "__main__":
    colors_example().run()
