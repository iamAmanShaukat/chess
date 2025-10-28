# src/gui/menu.py
import pygame
from src.config.settings import WINDOW_SIZE, FONT_PATH
import chess

class Menu:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Chess App - Main Menu")
        try:
            self.font_large = pygame.font.Font(FONT_PATH, 48)
            self.font_btn = pygame.font.Font(FONT_PATH, 32)
        except:
            self.font_large = pygame.font.SysFont("Arial", 48)
            self.font_btn = pygame.font.SysFont("Arial", 32)
        self.clock = pygame.time.Clock()

    def draw_button(self, text, x, y, width, height, hover=False):
        color = (60, 180, 75) if not hover else (50, 160, 65)
        pygame.draw.rect(self.screen, color, (x, y, width, height), border_radius=8)
        pygame.draw.rect(self.screen, (30, 30, 30), (x, y, width, height), 2, border_radius=8)
        txt = self.font_btn.render(text, True, (255, 255, 255))
        # Center text
        self.screen.blit(txt, (x + width // 2 - txt.get_width() // 2, y + height // 2 - txt.get_height() // 2))

    def show_start_screen(self):
        btn_width, btn_height = 420, 55  # ← wider and taller
        self.font_btn = pygame.font.SysFont("Arial", 28)

        btn1_rect = pygame.Rect(WINDOW_SIZE[0] // 2 - btn_width // 2, 180, btn_width, btn_height)
        btn2_rect = pygame.Rect(WINDOW_SIZE[0] // 2 - btn_width // 2, 250, btn_width, btn_height)
        btn3_rect = pygame.Rect(WINDOW_SIZE[0] // 2 - btn_width // 2, 320, btn_width, btn_height)

        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()
            b1_h = btn1_rect.collidepoint(mouse_pos)
            b2_h = btn2_rect.collidepoint(mouse_pos)
            b3_h = btn3_rect.collidepoint(mouse_pos)

            self.screen.fill((40, 40, 40))
            title = self.font_large.render("Chess App", True, (240, 240, 240))
            self.screen.blit(title, (WINDOW_SIZE[0] // 2 - title.get_width() // 2, 100))

            self.draw_button("Human vs Human", *btn1_rect, hover=b1_h)
            self.draw_button("Human vs AI (Play as White)", *btn2_rect, hover=b2_h)
            self.draw_button("Human vs AI (Play as Black)", *btn3_rect, hover=b3_h)

            pygame.display.flip()
            self.clock.tick(30)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if btn1_rect.collidepoint(event.pos):
                        pygame.quit()
                        return ("human_vs_human", None)
                    if btn2_rect.collidepoint(event.pos):
                        pygame.quit()
                        return ("human_vs_ai", chess.WHITE)
                    if btn3_rect.collidepoint(event.pos):
                        pygame.quit()
                        return ("human_vs_ai", chess.BLACK)
        pygame.quit()
        return ("human_vs_human", None)