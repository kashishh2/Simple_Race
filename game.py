import pygame
from settings import *
from road import Road
from player import Player
from scenery import Scenery

class Game:
    def __init__(self):
        # Initialize game objects
        self.road = Road(HORIZON_Y, SCREEN_WIDTH)
        self.player = Player()
        self.scenery = Scenery()
        self.clock = pygame.time.Clock()

    def update(self, dt):
        keys = pygame.key.get_pressed()
        
        # Update player (handles its own acceleration and lateral movement)
        self.player.update(keys, dt)
        
        # Update road using the player's current speed for dynamic scrolling
        self.road.update(dt, self.player.speed)
        
        # Update scenery - pass speed to allow for parallax effect if needed later
        self.scenery.update(dt, self.player.speed)

    def draw(self, surface):
        # Clear background (Sky)
        surface.fill(SKY_BLUE)
        
        # Render objects in order of depth: Scenery -> Road -> Player
        self.scenery.draw(surface)
        self.road.draw(surface)
        self.player.draw(surface)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Simple Race - Phase 2")
    
    game = Game()
    running = True
    while running:
        # Calculate delta time in seconds
        dt = game.clock.tick(FPS) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        game.update(dt)
        game.draw(screen)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
