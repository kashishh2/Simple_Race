import pygame
from settings import *
from sprites import draw_car_rear

class Player:
    def __init__(self):
        # Start in the middle of the road at the bottom
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT - 100
        self.width = 40
        self.height = 60
        
        self.speed = 0.0
        self.max_speed = TARGET_SPEED
        self.acceleration = ACCELERATION
        
        # Lateral movement variables
        self.lateral_pos = 0  # Relative to center

    def update(self, keys, dt):
        # Automatic acceleration (towards target speed)
        if self.speed < self.max_speed:
            self.speed += self.acceleration * dt * 10 # Scale for visibility
        
        # Steering logic (A/D keys)
        steering = 0
        if keys[pygame.K_a]:
            steering -= 1
        if keys[pygame.K_d]:
            steering += 1

        # Update lateral position based on steering and sensitivity
        self.lateral_pos += steering * STEERING_SENSITIVITY * dt * 50
        
        # Keep player within road boundaries (at the bottom)
        half_road = ROAD_WIDTH // 2
        self.x = (SCREEN_WIDTH // 2) + self.lateral_pos
        
        # Clamp lateral position to road boundaries
        self.x = max(SCREEN_WIDTH // 2 - half_road, min(self.x, SCREEN_WIDTH // 2 + half_road))

    def draw(self, surface):
        draw_car_rear(surface, self.x - self.width // 2, self.y, self.width, self.height)
