from game import *
from geom import *
from shapes import *

class halma(game):
    def __init__(self):
        super().__init__()
        self.verbs = [ click(self) ]

        for f in faces:
            self.add_thing(edge(f))

        self.home = { p.name: [] for p in self.players }
        self.pawns = { p.name: [] for p in self.players }
        for p, c in [ (self.players[0], "I000"),
                      (self.players[1], "i000") ]:
            self.home[p.name].append(c)
            for cc in cellcells[c]: self.home[p.name].append(cc)

            for cc in self.home[p.name]:
                for f in cellfaces[cc]:
                    if len([ c for c in facecells[f] if c in self.home[p.name] ]) == 2:
                        if not [ t for t in self.things[f] if t.kind == "homerod" ]:
                            self.add_thing(homerod(f, p.color))

            for P in self.players:
                if P.name != p.name:
                    for C in self.home[p.name]:
                        t = pawn(C, P.color)
                        self.pawns[P.name].append(t)
                        self.add_thing(t)

        self.cursor = cursor()
        self.jumped = False
        self.add_thing(self.cursor)

    def switched_player(self):
        self.update_thing(self.cursor, location=None)
        self.update_thing(self, jumped=False)

class edge(thing):
    layer = 0
    def draw(self, layer):
        decaprism(layer, self.id, self.location, None, (1,1,1), 1, 0.05, 5)

class homerod(thing):
    layer = 0
    kind = "homerod"
    def draw(self, layer):
        pentaprism(layer, self.id, self.location, self.color, (1,1,1), 1, 0.15, 5)

class pawn(thing):
    kind = "pawn"
    def draw(self, layer):
        geodesic(layer, self.id, self.location, self.color, (1,1,1), 0.75)

class cursor(thing):
    kind = "cursor"
    shape = [ (0.1,0,0,False), (True,False,True), (0.15,0.3,0.3,True), (True,False,True), (0.25,0,0,False) ]

    def draw(self, layer):
        for f in cellfaces[self.location]:
            prism(layer, self.id, (f, self.location), (0,1,0), (1,1,1), *self.shape)

class star(thing):
    kind = "star"
    def draw(self, layer):
        pointfig(layer, self.id, self.location, (1,1,0), (1,1,1), (0.8, 0.6, 0.55), (True,True,True))

class click(verb):
    name = "click"

    def all_cursors(self):
        C = self.game.cursor.location
        if C is None:
            for p in self.game.pawns[self.game.player().name]:
                c = p.location
                yield (c, cells[c], cellfaced * 0.8)
        else:
            for c in cellcells[C]:
                if [ t for t in self.game.things[c] if t.kind == "pawn" ]:
                    cc = cellcelljump(C,c)
                    if not [ t for t in self.game.things[cc] if t.kind == "pawn" ]:
                        yield (cc, cells[cc], cellfaced * 0.8)
                else:
                    if not self.game.jumped:
                        yield (c, cells[c], cellfaced * 0.8)

    def draw_cursor(self, layer, c, active):
        geodesic(layer, None, c, None, self.cursor_color(active), 0.8)

    def action(self, c, player):
        cur = self.game.cursor
        C = cur.location
        if C is None:
            self.game.update_thing(cur, location=c)
        else:
            p = [ t for t in self.game.things[C] if t.kind == "pawn" ][0]
            self.game.update_thing(p, location=c)
            if c in cellcells[C]:
                self.game.update_thing(cur, location=None)
            else:
                self.game.update_thing(cur, location=c)
                self.game.update_thing(self.game, jumped=True)

            # check victory condition
            if not [ h for h in self.game.home[self.game.player().name]
                     if not [ t for t in self.game.things[h]
                              if t.kind == "pawn" and t.color == self.game.player().color ] ]:
                # stop accepting clicks
                self.game.update_thing(self.game, verbs=[verb(self.game)])
                self.game.update_thing(cur, location=None)

                # draw victory stars
                for h in self.game.home[self.game.player().name]:
                    self.game.add_thing(star(h))

if __name__ == "__main__":
    halma().run()
