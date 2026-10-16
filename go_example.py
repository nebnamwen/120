from game import *
from shapes import *
import random

class go_example(game):
    bg_color = (0.8, 0.6, 0.4)

    def __init__(self):
        super().__init__()

        AB = { c: random.choice([True, False]) for c in cells }

        for e in edges:
            fs = [ f for f in edgefaces[e] if AB[facecells[f][0]] != AB[facecells[f][1]] ]
            if fs:
                dihedralspline(self.display.layers[0], e, fs, (0,0,0), None, 0.05)

        for f in faces:
            if AB[facecells[f][0]] != AB[facecells[f][1]]:
                if random.random() < 0.1:
                    color = random.choice([ (0,0,0), (1,1,1) ])
                    spheroid(self.display.layers[0], f, f, color, (0.5,0.5,0.5), 0.25, 0.75)

if __name__ == "__main__":
    go_example().run()
