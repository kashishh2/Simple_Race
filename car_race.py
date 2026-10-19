import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
GREEN = (34, 139, 34)     # Grass
GRAY = (50, 50, 50)       # Road
WHITE = (255, 255, 255)   # Lines
YELLOW = (255, 255, 0)    # Finish Line
RED = (200, 0, 0)         # Player Car
BLUE = (0, 0, 200)        # Bot Cars

class Car:
    def __init__(self, x, y, color, is_player=True):
        self.x = x
        self.y = y
        self.color = color
        self.is_player = is_player
        self.angle = 0
        self.speed = 0
        self.max_speed = 5
        self.acceleration = 0.1
        self.friction = 0.05
        self.turn_speed = 3
        self.width = 30
        self.height = 50

    def update(self, keys):
        if self.is_player:
            # Input Handling
            if keys[pygame.K_w]:
                self.speed += self.acceleration
            elif keys[pygame.K_s]:
                self.speed -= self.acceleration
            else:
                # Auto-accelerate slightly if not braking/pressing W
                if self.speed < self.max_speed / 2:
                    self.speed += self.acceleration * 0.5
                elif self.speed > -self.max_speed / 2:
                    self.speed -= self.friction

            if keys[pygame.K_a]:
                self.angle += self.turn_speed
            if keys[pygame.K_d]:
                self.angle -= self.turn_speed
        else:
            # Simple AI for bots
            self.speed += 0.1
            self.angle += (random.uniform(-2, 2)) * 0.05 # Slight wobble

        # Limit speed
        if self.speed > self.max_speed: self.speed = self.max_speed
        if self.speed < -self.max_speed / 2: self.speed = -self.max_speed / 2
        
        # Apply physics
        self.x += math.cos(math.radians(self.angle)) * self.speed
        self.y -= math.sin(math.radians(self.angle)) * self.speed

    def draw(self, screen):
        # Create a surface for the car to rotate easily
        car_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(car_surface, self.color, (0, 0, self.width, self.height))
        # Add "front" indicator
        pygame.draw.rect(car_surface, WHITE, (self.width//4, 5, self.width//2, 5))
        
        rotated_surface = pygame.transform.rotate(car_surface, self.angle)
        rect = rotated_surface.get_rect(center=(self.x, self.y))
        screen.blit(rotated_surface, rect)

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Simple Race Game")
    clock = pygame.time.Clock()

    # Setup Track (simple large rectangle for now, but we'll treat the middle as road)
    # To keep it simple and "open", let's use a long horizontal road path
    player = Car(400, 500, RED, True)
    bots = [
        Car(380, 510, BLUE, False),
        Car(420, 510, BLUE, False),
        Car(400, 520, BLUE, False)
    ]

    finish_line_x = 750
    game_over = False
    winner = None

    running = True
    while running:
        screen.fill(GREEN) # Draw Grass

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not game_over:
            keys = pygame.key.get_pressed()
            player.update(keys)

            # Update Bots
            for bot in bots:
                bot.update(None)
                # Simple "track" logic for bots: steer towards the right
                if bot.x < 400: bot.angle += 2
                elif bot.x > 500: bot.angle -= 2
                else: bot.angle += random.uniform(-1, 1)

            # Collision / Boundary Check (Simple example)
            if player.y < -100 or player.y > SCREEN_HEIGHT + 100 or \
               player.x < -100 or player.x > SCREEN_WIDTH + 100:
                game_over = True
                winner = "Crashed Out of Bounds!"

            # Finish line check
            if player.x >= finish_line_x:
                game_over = True
                winner = "Player Wins!"

        # Draw Road (Simple wide horizontal strip)
        pygame.draw.rect(screen, GRAY, (0, 450, SCREEN_WIDTH, 150))
        # Finish Line
        pygame.draw.rect(screen, YELLOW, (finish_line_x, 450, 20, 150))

        # Draw Cars
        player.draw(screen)
        for bot in bots:
            bot.draw(screen)

        if game_over:
            font = pygame.font.SysFont(None, 74)
            text = font.render(winner, True, WHITE)
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2))

        pygame.display.update()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
