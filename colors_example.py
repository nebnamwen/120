from game import *
import random

class colors_example(game):
    def __init__(self):
        super().__init__()

        AB = { c: random.choice([True, False]) for c in cells }

        for f in faces:
            if AB[facecells[f][0]] != AB[facecells[f][1]]:
                color = random.choice([numpy.array([1,0,0]),
                                       numpy.array([0,1,0]),
                                       numpy.array([0,0,1]),
                                       numpy.array([1,1,0]),
                                       numpy.array([1,0,1]),
                                       numpy.array([0,1,1]),
                                       numpy.array([1,1,1])])
                for e in faceedges[f]:
                    self.display.layers[0].line(verts[edgeverts[e][0]], verts[edgeverts[e][1]], numpy.array([1,1,1]))
                    self.display.layers[0].triangle(faces[f], verts[edgeverts[e][0]], verts[edgeverts[e][1]], color)

if __name__ == "__main__":
    colors_example().run()
