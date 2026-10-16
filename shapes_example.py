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

                hexaprism(self.display.layers[0], e, e, color, (1,1,1), 0.6, 0.1)

        for f in faces:
            if random.random() < 0.2:
                color = random.choice(colors)

                decaprism(self.display.layers[0], f, f, color, (1,1,1), 0.1, 0.6)

        for c in cells:
            if random.random() < 0.15:
                color = random.choice(colors)

                icosahedron(self.display.layers[0], c, c, color, (1,1,1), 0.3)

        for v in verts:
            if random.random() < 0.15:
                color = random.choice(colors)

                rhombic12hedron(self.display.layers[0], v, v, color, (1,1,1), 0.45)

if __name__ == "__main__":
    shapes_example().run()
