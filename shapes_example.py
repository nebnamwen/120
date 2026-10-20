from game import *
from shapes import *
import random

class shapes_example(game):
    def __init__(self):
        super().__init__()

        colors = [(1,0,0),
                  (0,1,0),
                  (0,0,1),
                  (1,1,0),
                  (1,0,1),
                  (0,1,1),
                  (1,1,1)]

        for e in edges:
            if random.random() < 0.2:
                color = random.choice(colors)
                self.add_thing(rod(location=e, color=color))

        for f in faces:
            if random.random() < 0.2:
                color = random.choice(colors)
                self.add_thing(token(location=f, color=color))

        for c in cells:
            if random.random() < 0.15:
                color = random.choice(colors)
                self.add_thing(ball(location=c, color=color))

        for v in verts:
            if random.random() < 0.15:
                color = random.choice(colors)
                self.add_thing(vertex(location=v, color=color))

class rod(thing):
    layer=1
    def draw(self,layer):
        hexaprism(layer, self.id, self.location, self.color, (1,1,1), 0.6, 0.1)

class token(thing):
    layer=1
    def draw(self,layer):
        decaprism(layer, self.id, self.location, self.color, (1,1,1), 0.1, 0.6)

class ball(thing):
    layer=1
    def draw(self,layer):
        icosahedron(layer, self.id, self.location, self.color, (1,1,1), 0.3)

class vertex(thing):
    layer=1
    def draw(self,layer):
        rhombic12hedron(layer, self.id, self.location, self.color, (1,1,1), 0.45)

if __name__ == "__main__":
    shapes_example().run()
