import pygame
import numpy

from geom import *
from display import display

class game:
    bg_color = (0, 0, 0)

    def __init__(self):
        self.display = display(self.bg_color)
    
    def run(self):
        self.running = True
        while self.running:

            for event in pygame.event.get():
                self.handle_event(event)

            self.display.update()

        self.display.quit()

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
