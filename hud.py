import pygame
from settings import *

class HUD:
    def __init__(self):
        # Initialize fonts
        self.main_font = pygame.font.SysFont("Arial", HUD_FONT_SIZE, bold=True)
        self.speed_font = pygame.font.SysFont("Arial", 20, bold=True)

    def draw(self, surface, elapsed_time, speed, score, lap, total_laps, position):
        # 1. Position (Top-left)
        pos_text = self.main_font.render(f"POS: {position}", True, YELLOW)
        surface.blit(pos_text, (20, 20))

        # 2. Lap (Top-center)
        lap_text = self.main_font.render(f"LAP {lap}/{total_laps}", True, YELLOW)
        rect = lap_text.get_rect(center=(SCREEN_WIDTH // 2, 30))
        surface.blit(lap_text, rect)

        # 3. Time (Top-right)
        time_str = f"{elapsed_time:.1f}s"
        time_text = self.main_font.render(time_str, True, YELLOW)
        surface.blit(time_text, (SCREEN_WIDTH - time_text.get_width() - 20, 20))

        # 4. Speedometer (Bottom-right)
        # Draw outer circle
        pygame.draw.circle(surface, WHITE, (SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100), SPEEDOMETER_RADIUS, 2)
        
        # Calculate needle angle based on speed
        # Assume max speed is around 15.0 units/frame in our current scale
        max_speed = 15.0
        angle = (speed / max_speed) * 180
        
        # Draw needle
        needle_end_x = (SCREEN_WIDTH - 100) + (SPEEDOMETER_RADIUS - 10) * pygame.math.Vector2(1, 0).rotate(angle).x
        needle_end_y = (SCREEN_HEIGHT - 100) + (SPEEDOMETER_RADIUS - 10) * pygame.math.Vector2(1, 0).rotate(angle).y
        pygame.draw.line(surface, RED, (SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100), (needle_end_x, needle_end_y), 3)

        # Numeric Speed inside speedometer
        kmh = speed * KMH_MULTIPLIER
        speed_text = self.speed_font.render(f"{int(kmh)} KM/H", True, WHITE)
        surface.blit(speed_text, (SCREEN_WIDTH - 100 - speed_text.get_width() // 2, SCREEN_HEIGHT - 100 + 5))

    def draw_score(self, surface, score):
        score_text = self.main_font.render(f"SCORE: {int(score)}", True, WHITE)
        surface.blit(score_text, (20, SCREEN_HEIGHT - 40))
