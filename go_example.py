from game import *
import random

class go_example(game):
    bg_color = (0.8, 0.6, 0.4)

    def __init__(self):
        super().__init__()

        AB = { c: random.choice([True, False]) for c in cells }

        for e in edges:
            fs = [ f for f in edgefaces[e] if AB[facecells[f][0]] != AB[facecells[f][1]] ]
            if fs:
                n = 10
                spline = [ (faces[fs[0]] * (1 - x/n) + edges[e] * x/n) * (1 - x/n) +
                           (edges[e] * (1 - x/n) + faces[fs[1]] * x/n) * x/n
                           for x in range(n+1) ]
                for i in range(n):
                    self.display.layers[0].line(spline[i], spline[i+1], numpy.array([0,0,0]))

if __name__ == "__main__":
    go_example().run()
