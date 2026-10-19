import pygame
from settings import *

class Road:
    def __init__(self, horizon_y, screen_width):
        self.horizon_y = horizon_y
        self.screen_width = screen_width
        self.scroll_offset = 0

    def update(self, dt, speed):
        # Scroll the lane markings based on current player speed
        self.scroll_offset += speed * dt * 100
        self.scroll_offset %= 100

    def draw(self, surface):
        # Draw road asphalt with perspective
        for y in range(self.horizon_y, SCREEN_HEIGHT + 1):
            depth = (y - self.horizon_y) / (SCREEN_HEIGHT - self.horizon_y)
            width = ROAD_WIDTH * depth
            x_left = (self.screen_width // 2) - (width // 2)
            # Draw asphalt color
            pygame.draw.rect(surface, DARK_GRAY, (x_left, y, width, 1))

        # Draw lane markings (dashed white lines)
        for y in range(self.horizon_y, SCREEN_HEIGHT + 1):
            depth = (y - self.horizon_y) / (SCREEN_HEIGHT - self.horizon_y)
            width = ROAD_WIDTH * depth
            x_left = (self.screen_width // 2) - (width // 2)

            # Dashes get closer together as they move towards the bottom
            dash_freq = depth * 50 + 10
            if int(self.scroll_offset / dash_freq) % 2 == 0:
                pygame.draw.rect(surface, LANE_MARKING_COLOR, (x_left + width//3, y, width//3, 1))
