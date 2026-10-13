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

                prism(self.display.layers[0], e, e, color, (1,1,1), (0,0.1,0.05,False), (True,True,True), (0.6,0.1,0.05,True), (True,False,False), (0.6,0,0,False))

        for f in faces:
            if random.random() < 0.2:
                color = random.choice(colors)

                prism(self.display.layers[0], f, f, color, (1,1,1), (0,0.6,0.6,False), (True,False,True), (0.1,0.6,0.6,True), (True,False,False), (0.1,0,0,False))

        for c in cells:
            if random.random() < 0.15:
                color = random.choice(colors)

                pointfig(self.display.layers[0], c, c, color, (1,1,1), (0.3,0.3,0.3), (False,True,False))

        for v in verts:
            if random.random() < 0.15:
                color = random.choice(colors)

                pointfig(self.display.layers[0], v, v, color, (1,1,1), (0.45,0.27,0.15), (True,True,False))

if __name__ == "__main__":
    shapes_example().run()
