import pygame
from settings import *

class MenuSystem:
    def __init__(self):
        # Initialize fonts
        self.title_font = pygame.font.SysFont("Arial", MENU_FONT_SIZE, bold=True)
        self.button_font = pygame.font.SysFont("Arial", SUB_MENU_FONT_SIZE, bold=True)
        self.body_font = pygame.font.SysFont("Arial", 24, bold=False)

    def draw_main_menu(self, surface):
        # Background (Simplified: use the road/scenery or a clear color for now)
        surface.fill(DARK_GRAY)
        
        # Title
        title = self.title_font.render("HIGHWAY RACER", True, MENU_TITLE_COLOR)
        rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        surface.blit(title, rect)

        # Buttons (Vertical stack)
        buttons = ["START GAME", "OPTIONS", "HOW TO PLAY", "QUIT"]
        button_y_start = SCREEN_HEIGHT // 2 - 50
        for i, text in enumerate(buttons):
            color = SELECTED_BUTTON_COLOR if i == 1 else BUTTON_COLOR # Default selection is 'Options'
            btn_text = self.button_font.render(text, True, color)
            rect = btn_text.get_rect(center=(SCREEN_WIDTH // 2, button_y_start + (i * 60)))
            surface.blit(btn_text, rect)

    def draw_pause_screen(self, surface):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        pause_text = self.title_font.render("PAUSED", True, PAUSE_TEXT_COLOR)
        rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        surface.blit(pause_text, rect)

        resume_text = self.button_font.render("Press 'P' to Resume", True, WHITE)
        rect_res = resume_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        surface.blit(resume_text, rect_res)

    def draw_results_screen(self, surface, time_str, score):
        surface.fill(DARK_GRAY)

        title = self.title_font.render("RACE COMPLETE", True, YELLOW)
        rect1 = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        surface.blit(title, rect1)

        time_text = self.body_font.render(f"Time: {time_str}", True, WHITE)
        score_text = self.body_font.render(f"Score: {int(score)}", True, WHITE)
        
        rect2 = time_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        rect3 = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
        
        surface.blit(time_text, rect2)
        surface.blit(score_text, rect3)

        retry_text = self.button_font.render("Press 'R' to Retry", True, RED)
        rect4 = retry_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.8))
        surface.blit(retry_text, rect4)
