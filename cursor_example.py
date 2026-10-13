from game import *
from shapes import *
import random

class cursor_example(game):
    def update_cursor(self):
        self.display.layers[0].clear()
        for c in cells:
            if self.display.cursor_ray_check(cells[c], 0.3):
                pointfig(self.display.layers[0], c, c, None, (1,1,1), (0.8,0.8,0.8), (False,True,False))

if __name__ == "__main__":
    cursor_example().run()
