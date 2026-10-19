import pygame
import random
from settings import *
from sprites import draw_rival_car

class TrafficVehicle:
    def __init__(self, lane_offset, depth):
        # Randomly choose a color from the predefined list
        self.color = random.choice(TRAFFIC_COLORS)
        # Set initial position based on perspective and lane
        # Depth is 0 at horizon, 1 at bottom of screen
        self.depth = depth # 0 to 1
        
        # Calculate width/height based on depth (projection)
        # Nearer vehicles are larger
        base_width = 40
        base_height = 60
        self.width = base_width * self.depth * 5  # Scale by depth to make them bigger in front
        self.height = base_height * self.depth * 5
        
        # Lane position: -1 (left), 0 (center), 1 (right)
        self.lane_offset = lane_offset # Range roughly -2 to 2
        self.x = (SCREEN_WIDTH // 2) + (self.lane_offset * ROAD_WIDTH * self.depth)
        self.y = self.horizon_y + ((SCREEN_HEIGHT - self.horizon_y) * self.depth)

    def update(self, dt, player_speed):
        # Move towards the player (downwards in screen space)
        # We adjust speed based on depth: farther vehicles move slower
        move_speed = player_speed * (1 + (1 - self.depth)) 
        self.y += move_speed * dt * 50
        
        # Update depth as it moves towards bottom
        new_depth = (self.y - self.horizon_y) / (SCREEN_HEIGHT - self.horizon_y)
        self.depth = max(0, min(1, new_depth))
        
        # Recalculate width/height based on new depth
        self.width = 40 * self.depth * 5
        self.height = 60 * self.depth * 5
        
        # Keep x relative to lane as it moves
        self.x = (SCREEN_WIDTH // 2) + (self.lane_offset * ROAD_WIDTH * self.depth)

    def draw(self, surface):
        draw_rival_car(surface, self.x - self.width // 2, self.y, self.width, self.height, self.color)

class TrafficManager:
    def __init__(self):
        self.vehicles = []
        self.spawn_timer = 0.0

    def update(self, dt, player_speed):
        # Spawn new vehicles periodically
        self.spawn_timer += dt
        if self.spawn_timer >= SPAWN_INTERVAL:
            # Random lane offset and random depth (starting far away)
            lane = random.uniform(-1.5, 1.5)
            depth = random.uniform(0.4, 0.9) # Spawn in the middle-to-front distance
            self.vehicles.append(TrafficVehicle(lane, depth))
            self.spawn_timer = 0

        # Update all vehicles
        for v in self.vehicles[:]:
            v.update(dt, player_speed)
            # Remove vehicles that have passed the bottom of the screen
            if v.y > SCREEN_HEIGHT + 50:
                self.vehicles.remove(v)

    def draw(self, surface):
        # Sort by depth so we draw farther ones first (Painter's Algorithm)
        sorted_vehicles = sorted(self.vehicles, key=lambda v: v.depth)
        for v in sorted_vehicles:
            v.draw(surface)

    def get_collisions(self, player):
        # Check if any vehicle is close to the player
        for v in self.vehicles:
            # Basic bounding box overlap check in screen space
            p_rect = pygame.Rect(player.x - player.width//2, player.y, player.width, player.height)
            v_rect = pygame.Rect(v.x - v.width//2, v.y, v.width, v.height)
            if p_rect.colliderect(v_rect):
                return True
        return False
