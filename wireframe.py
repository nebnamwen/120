from game import *

class wireframe(game):
    def __init__(self):
        super().__init__()

        for e in edges:
            self.display.layers[0].line(verts[edgeverts[e][0]], verts[edgeverts[e][1]], numpy.array([1,1,1]))

if __name__ == "__main__":
    wireframe().run()
