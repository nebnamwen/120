import pygame
from collections import defaultdict

from geom import *
from display import display

class game:
    bg_color = (0, 0, 0)

    def __init__(self):
        self.display = display(self.bg_color)

        self.undo_stack = []
        self.draw_things = []
        self.remove_things = []

        self.things = defaultdict(list)

        self.players = [ player(self, "red", (1,0,0)),
                         player(self, "blue", (0,0,1)) ]
        self.playern = 0

        self.verbs = [verb()]
        self.verbn = 0

    def add_thing(self, t):
        self.things[t.location].append(t)
        self.draw_things.append(t)
        self.add_undo(lambda: self.things[t.location].remove(t))
        self.add_undo(lambda: self.remove_things.append(t))
        return t

    def remove_thing(self, t):
        self.things[t.location].remove(t)
        self.remove_things.append(t)
        self.add_undo(lambda: self.things[t.location].append(t))
        self.add_undo(lambda: self.draw_things.append(t))
        return t

    def update_thing(self, t, **kwargs):
        for key, value in kwargs.items():
            if key == 'location': self.remove_thing(t)
            old_val = getattr(t, key)
            self.add_undo(lambda: setattr(t, key, old_val))
            setattr(t, key, value)
            if key == 'location': self.add_thing(t)
        return t

    def add_undo(self, f):
        if self.undo_stack:
            self.undo_stack[-1].append(f)

    def undo(self):
        if self.undo_stack:
            uf = self.undo_stack.pop()
            uf.reverse()
            for f in uf: f()
            self.draw_updated_things()

    def do_verb(self, v, p, c):
        self.undo_stack.append([])
        v.action(p, c)
        if self.undo_stack and not self.undo_stack[-1]: self.undo_stack.pop()
        self.draw_updated_things()

    def draw_updated_things(self):
        remove_layers = defaultdict(list)
        for t in self.remove_things:
            remove_layers[t.layer].append(t.id)
        for l in remove_layers:
            self.display.layers[l].remove(*remove_layers[l])

        for t in self.draw_things:
            t.draw(self.display.layers[t.layer])

        self.remove_things = []
        self.draw_things = []

    def run(self):
        self.draw_updated_things()

        self.running = True
        while self.running:

            for event in pygame.event.get():
                self.handle_event(event)

            self.display.update()
            self.update_cursor()
            self.display.draw()

        self.display.quit()

    def update_cursor(self):
        pass

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False

class player:
    def __init__(self, g, name, color):
        self.game = g
        self.name = name
        self.color = color

class thing:
    _id = 0
    layer = 1
    kind = None

    def __init__(self, location=None, color=None, **kwargs):
        self.color = color
        self.location = location

        self.id = thing._id
        thing._id += 1

    def draw(self, layer):
        pass

class verb:
    pass
