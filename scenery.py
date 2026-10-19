import pygame
import random
from settings import *
from sprites import draw_mountain, draw_tree, draw_barrier

class Scenery:
    def __init__(self):
        # Randomize some scenery for variety
        self.mountains = [
            {"x": 100, "y": 300, "w": 200, "h": 150, "color": GRAY},
            {"x": 400, "y": 350, "w": 300, "h": 200, "color": DARK_GRAY},
            {"x": 700, "y": 320, "w": 150, "h": 120, "color": GRAY}
        ]
        self.trees = []
        # Populate some random trees along the road
        for i in range(10):
            tx = random.randint(100, 700)
            ty = random.randint(350, 500)
            self.trees.append({"x": tx, "y": ty, "scale": random.uniform(0.8, 1.5)})

    def update(self, dt, speed):
        # Scenery is currently mostly static for Phase 1, 
        # but we can add movement logic here later.
        pass

    def draw(self, surface):
        # Draw mountains
        for m in self.mountains:
            draw_mountain(surface, m["x"], m["y"], m["w"], m["h"], m["color"])
        
        # Draw trees
        for t in self.trees:
            draw_tree(surface, t["x"], t["y"], t["scale"])

        # Draw some barriers
        draw_barrier(surface, 0, 400, SCREEN_WIDTH, 20)
