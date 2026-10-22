from game import *
from geom import *
from shapes import *

class cursor_example(game):
    def __init__(self):
        super().__init__()
        self.verbs = [ place_token(self) ]

        for e in edges:
            self.add_thing(edge(e))

class edge(thing):
    layer = 0
    def draw(self,layer):
        hexaprism(layer, self.id, self.location, None, (1,1,1), 1, 0)

class token(thing):
    def draw(self, layer):
        icosahedron(layer, self.id, self.location, self.color, (1,1,1), 0.75)

class place_token(verb):
    def allcursors(self):
        return [ (c, cells[c], cellfaced) for c in cells if not self.game.things[c] ]

    def draw_cursor(self, layer, c, active):
        dodecahedron(layer, None, c, None, self.cursor_color(active), 0.9)

    def action(self, c, player):
        self.game.add_thing(token(c, player.color))

if __name__ == "__main__":
    cursor_example().run()
