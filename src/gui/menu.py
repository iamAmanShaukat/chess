# src/gui/menu.py
import pygame
from src.config.settings import WINDOW_SIZE, FONT_PATH
import chess


class Menu:
    # Color constants
    BG_COLOR = (40, 40, 40)
    TITLE_COLOR = (240, 240, 240)
    SUBTITLE_COLOR = (200, 200, 200)
    BUTTON_COLOR = (60, 180, 75)
    BUTTON_HOVER_COLOR = (50, 160, 65)
    BUTTON_BORDER_COLOR = (30, 30, 30)
    SLIDER_BG_COLOR = (100, 100, 100)
    TEXT_COLOR = (255, 255, 255)

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Chess App - Main Menu")

        try:
            self.font_large = pygame.font.Font(FONT_PATH, 48)
            self.font_btn = pygame.font.Font(FONT_PATH, 32)
            self.font_medium = pygame.font.Font(FONT_PATH, 28)
        except (FileNotFoundError, OSError):
            self.font_large = pygame.font.SysFont("Arial", 48)
            self.font_btn = pygame.font.SysFont("Arial", 32)
            self.font_medium = pygame.font.SysFont("Arial", 28)

        self.clock = pygame.time.Clock()

    def draw_button(self, text, rect, hover=False, font=None):
        """Draw a button with text centered."""
        if font is None:
            font = self.font_btn

        color = self.BUTTON_HOVER_COLOR if hover else self.BUTTON_COLOR
        pygame.draw.rect(self.screen, color, rect, border_radius=8)
        pygame.draw.rect(self.screen, self.BUTTON_BORDER_COLOR, rect, 2, border_radius=8)

        txt = font.render(text, True, self.TEXT_COLOR)
        txt_rect = txt.get_rect(center=rect.center)
        self.screen.blit(txt, txt_rect)

    def draw_centered_text(self, text, y, font, color):
        """Draw text centered horizontally at given y position."""
        surf = font.render(text, True, color)
        x = WINDOW_SIZE[0] // 2 - surf.get_width() // 2
        self.screen.blit(surf, (x, y))

    def show_difficulty_screen(self, human_color):
        """Show slider to select AI difficulty (1-20)."""
        color_name = 'White' if human_color == chess.WHITE else 'Black'
        title = f"Human vs AI ({color_name})"
        subtitle = "Select AI Difficulty (1 = Easy, 20 = Hard)"

        # Slider dimensions
        slider_width = 400
        slider_height = 20
        slider_x = WINDOW_SIZE[0] // 2 - slider_width // 2
        slider_y = 250
        handle_radius = 15

        # Slider interaction area (expanded for easier clicking)
        slider_area = pygame.Rect(
            slider_x - handle_radius,
            slider_y - handle_radius,
            slider_width + handle_radius * 2,
            slider_height + handle_radius * 2
        )

        difficulty = 10  # Default difficulty
        dragging = False
        needs_redraw = True

        # Confirm button
        btn_rect = pygame.Rect(WINDOW_SIZE[0] // 2 - 100, slider_y + 100, 200, 50)

        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()
            btn_hover = btn_rect.collidepoint(mouse_pos)

            # Only redraw if something changed
            if needs_redraw:
                self.screen.fill(self.BG_COLOR)

                # Title and subtitle
                self.draw_centered_text(title, 100, self.font_large, self.TITLE_COLOR)
                self.draw_centered_text(subtitle, 180, self.font_btn, self.SUBTITLE_COLOR)

                # Slider track
                pygame.draw.rect(
                    self.screen,
                    self.SLIDER_BG_COLOR,
                    (slider_x, slider_y, slider_width, slider_height),
                    border_radius=10
                )

                # Slider handle
                # Normalize difficulty (1-20) to slider position (0-1)
                normalized = (difficulty - 1) / 19
                handle_x = slider_x + int(normalized * slider_width)
                pygame.draw.circle(
                    self.screen,
                    self.BUTTON_COLOR,
                    (handle_x, slider_y + slider_height // 2),
                    handle_radius
                )

                # Display current difficulty
                self.draw_centered_text(str(difficulty), slider_y + 40, self.font_large, self.TEXT_COLOR)

                # Confirm button
                self.draw_button("Start Game", btn_rect, hover=btn_hover)

                pygame.display.flip()
                needs_redraw = False

            self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None  # Signal to exit game

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if btn_rect.collidepoint(event.pos):
                        return difficulty

                    if slider_area.collidepoint(event.pos):
                        dragging = True
                        # Calculate difficulty from click position
                        relative_x = max(0, min(slider_width, event.pos[0] - slider_x))
                        new_difficulty = 1 + int(relative_x / slider_width * 19)
                        if new_difficulty != difficulty:
                            difficulty = new_difficulty
                            needs_redraw = True

                elif event.type == pygame.MOUSEBUTTONUP:
                    dragging = False

                elif event.type == pygame.MOUSEMOTION:
                    if dragging:
                        relative_x = max(0, min(slider_width, event.pos[0] - slider_x))
                        new_difficulty = 1 + int(relative_x / slider_width * 19)
                        if new_difficulty != difficulty:
                            difficulty = new_difficulty
                            needs_redraw = True
                    # Check if hover state changed
                    elif btn_rect.collidepoint(event.pos) != btn_hover:
                        needs_redraw = True

        return None

    def show_start_screen(self):
        """Show main menu with game mode options."""
        btn_width, btn_height = 420, 55
        center_x = WINDOW_SIZE[0] // 2

        buttons = [
            ("Human vs Human", pygame.Rect(center_x - btn_width // 2, 180, btn_width, btn_height)),
            ("Human vs AI (Play as White)", pygame.Rect(center_x - btn_width // 2, 250, btn_width, btn_height)),
            ("Human vs AI (Play as Black)", pygame.Rect(center_x - btn_width // 2, 320, btn_width, btn_height))
        ]

        needs_redraw = True
        last_hover = None

        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()

            # Determine which button is hovered
            current_hover = None
            for i, (_, rect) in enumerate(buttons):
                if rect.collidepoint(mouse_pos):
                    current_hover = i
                    break

            # Only redraw if hover state changed
            if needs_redraw or current_hover != last_hover:
                self.screen.fill(self.BG_COLOR)
                self.draw_centered_text("Chess App", 100, self.font_large, self.TITLE_COLOR)

                for i, (text, rect) in enumerate(buttons):
                    self.draw_button(text, rect, hover=(i == current_hover), font=self.font_medium)

                pygame.display.flip()
                needs_redraw = False
                last_hover = current_hover

            self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None  # Signal to exit game

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Human vs Human
                    if buttons[0][1].collidepoint(event.pos):
                        return ("human_vs_human", None)

                    # Human vs AI (White)
                    elif buttons[1][1].collidepoint(event.pos):
                        diff = self.show_difficulty_screen(chess.WHITE)
                        if diff is None:  # User closed window
                            return None
                        return ("human_vs_ai", chess.WHITE, diff)

                    # Human vs AI (Black)
                    elif buttons[2][1].collidepoint(event.pos):
                        diff = self.show_difficulty_screen(chess.BLACK)
                        if diff is None:  # User closed window
                            return None
                        return ("human_vs_ai", chess.BLACK, diff)

        return None