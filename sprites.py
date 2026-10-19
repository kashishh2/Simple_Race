import pygame

def draw_car_rear(surface, x, y, width, height):
    """Draws a retro pixel-art style red sports car from the rear."""
    # Body
    pygame.draw.rect(surface, (200, 0, 0), (x, y, width, height)) # Red body
    # Rear window
    pygame.draw.rect(surface, (50, 50, 100), (x + width*0.2, y + height*0.1, width*0.6, height*0.3))
    # Taillights
    pygame.draw.rect(surface, (255, 0, 0), (x, y + height*0.7, width*0.4, height*0.2)) # Left
    pygame.draw.rect(surface, (255, 0, 0), (x + width*0.6, y + height*0.7, width*0.4, height*0.2)) # Right
    # Tires
    pygame.draw.rect(surface, (30, 30, 30), (x - 5, y + height*0.4, width+10, height*0.3))

def draw_mountain(surface, x, y, width, height, color):
    """Draws a simple triangular mountain."""
    points = [(x, y), (x + width // 2, y - height), (x + width, y)]
    pygame.draw.polygon(surface, color, points)

def draw_tree(surface, x, y, scale):
    """Draws a simple procedural tree."""
    # Trunk
    pygame.draw.rect(surface, (100, 50, 20), (x - 5 * scale, y, 10 * scale, 20 * scale))
    # Leaves
    pygame.draw.circle(surface, (34, 139, 34), (x, y - 10 * scale), 15 * scale)

def draw_barrier(surface, x, y, width, height):
    """Draws a roadside barrier."""
    pygame.draw.rect(surface, (150, 150, 150), (x, y, width, height))
    pygame.draw.rect(surface, (200, 200, 200), (x, y, width, height*0.3)) # Top cap
