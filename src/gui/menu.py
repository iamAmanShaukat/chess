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

    def show_difficulty_screen(self, human_color):
        title = f"Human vs AI ({'White' if human_color == chess.WHITE else 'Black'})"
        subtitle = "Select AI Difficulty (1 = Easy, 20 = Hard)"

        slider_width = 400
        slider_height = 20
        slider_x = WINDOW_SIZE[0] // 2 - slider_width // 2
        slider_y = 250

        difficulty = 10  # default

        running = True
        dragging = False
        while running:
            mouse_pos = pygame.mouse.get_pos()
            self.screen.fill((40, 40, 40))

            # Title
            title_surf = self.font_large.render(title, True, (240, 240, 240))
            self.screen.blit(title_surf, (WINDOW_SIZE[0] // 2 - title_surf.get_width() // 2, 100))
            sub_surf = self.font_btn.render(subtitle, True, (200, 200, 200))
            self.screen.blit(sub_surf, (WINDOW_SIZE[0] // 2 - sub_surf.get_width() // 2, 180))

            # Slider background
            pygame.draw.rect(self.screen, (100, 100, 100), (slider_x, slider_y, slider_width, slider_height),
                             border_radius=10)
            # Slider handle
            handle_x = slider_x + int((difficulty - 1) / 19 * slider_width)
            pygame.draw.circle(self.screen, (60, 180, 75), (handle_x, slider_y + slider_height // 2), 15)

            # Difficulty number
            diff_text = self.font_large.render(str(difficulty), True, (255, 255, 255))
            self.screen.blit(diff_text, (WINDOW_SIZE[0] // 2 - diff_text.get_width() // 2, slider_y + 40))

            # Confirm button
            btn_rect = pygame.Rect(WINDOW_SIZE[0] // 2 - 100, slider_y + 100, 200, 50)
            hover = btn_rect.collidepoint(mouse_pos)
            pygame.draw.rect(self.screen, (60, 180, 75) if not hover else (50, 160, 65), btn_rect, border_radius=8)
            btn_text = self.font_btn.render("Start Game", True, (255, 255, 255))
            self.screen.blit(btn_text, (
            btn_rect.centerx - btn_text.get_width() // 2, btn_rect.centery - btn_text.get_height() // 2))

            pygame.display.flip()
            self.clock.tick(30)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if btn_rect.collidepoint(event.pos):
                        return difficulty
                    # Check if clicked on slider
                    if slider_x <= event.pos[0] <= slider_x + slider_width and \
                            slider_y - 10 <= event.pos[1] <= slider_y + slider_height + 10:
                        dragging = True
                        difficulty = max(1, min(20, 1 + int((event.pos[0] - slider_x) / slider_width * 19)))
                elif event.type == pygame.MOUSEBUTTONUP:
                    dragging = False
                elif event.type == pygame.MOUSEMOTION and dragging:
                    difficulty = max(1, min(20, 1 + int((event.pos[0] - slider_x) / slider_width * 19)))

        pygame.quit()
        return 10

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
                        return ("human_vs_human", None)
                    if btn2_rect.collidepoint(event.pos):
                        diff = self.show_difficulty_screen(chess.WHITE)
                        return ("human_vs_ai", chess.WHITE, diff)
                    if btn3_rect.collidepoint(event.pos):
                        diff = self.show_difficulty_screen(chess.BLACK)
                        return ("human_vs_ai", chess.BLACK, diff)
