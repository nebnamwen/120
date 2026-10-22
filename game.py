import pygame
from collections import defaultdict

from geom import *
from display import display

class game:
    bg_color = (0, 0, 0)
    cursor_color = { False: (0.5, 0, 0.5), True: (1, 0, 1) }

    def __init__(self):
        self.display = display(self.bg_color)

        self.undo_stack = []
        self.draw_things = []
        self.remove_things = []

        self.things = defaultdict(list)

        self.players = [ player(self, "red", (1,0,0)),
                         player(self, "blue", (0,0,1)) ]
        self.playern = 0

        self.verbs = [verb(self)]
        self.verbn = 0

        self.allcursors = []
        self.cursors = []
        self.cursorn = 0

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

    def do_verb(self):
        self.undo_stack.append([])
        self.verbs[self.verbn].action(self.cursors[self.cursorn], self.players[self.playern])
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

        self.update_allcursors()

    def run(self):
        self.draw_updated_things()

        self.running = True
        while self.running:

            for event in pygame.event.get():
                self.handle_event(event)

            self.display.update()
            self.update_cursors()
            self.display.draw()

        self.display.quit()

    def update_allcursors(self):
        self.allcursors = list(self.verbs[self.verbn].allcursors())
        self.update_cursors()

    def update_cursors(self):
        new_cursors = [ c[1] for c in sorted(self.display.cursor_ray_check(self.allcursors)) ]
        if not new_cursors == self.cursors:
            self.cursors = new_cursors
            self.cursorn = 0
            self.draw_cursors()

    def draw_cursors(self):
        layer = self.display.layers[2]
        layer.clear()

        for c in self.cursors:
            # [ c[0] for c in self.allcursors ]
            # if pygame.key.get_pressed()[pygame.K_TAB]
            # and not pygame.mouse.get_pressed()[0]
            # else self.cursors:
            self.verbs[self.verbn].draw_cursor(layer, c, c == self.cursors[self.cursorn])

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_z:
                self.undo()

            if event.key == pygame.K_p:
                self.playern = (self.playern + 1) % len(self.players)
                self.update_allcursors()

            if event.key == pygame.K_v:
                self.verbn = (self.verbn + 1) % len(self.verbs)
                self.update_allcursors()

            if event.key == pygame.K_TAB:
                self.cursorn = (self.cursorn + 1) % len(self.cursors)
                self.draw_cursors()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.cursors:
                self.do_verb()

class player:
    def __init__(self, game, name, color):
        self.game = game
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
    name = "verb"

    def __init__(self, game):
        self.game = game

    def cursor_color(self, is_active):
        return self.game.cursor_color[is_active]

    def allcursors(self):
        return []

    def draw_cursor(self, location, is_active):
        raise NotImplementedError

    def action(self, location, player):
        raise NotImplementedError
