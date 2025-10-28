# src/gui/display.py
import pygame
import chess
import os

from src.config.settings import (
    BOARD_SIZE, SQUARE_SIZE, WINDOW_SIZE,
    WHITE, BLACK, LIGHT_SQUARE, DARK_SQUARE, HIGHLIGHT,
    ASSET_PATH, PIECE_IMAGES, FONT_PATH,
    COORD_MARGIN, BOARD_WIDTH, BOARD_HEIGHT
)


class Display:
    # Color constants
    SELECTED_HIGHLIGHT = HIGHLIGHT
    LEGAL_MOVE_COLOR = (0, 200, 0)
    PLAYED_MOVE_COLOR = (255, 255, 0, 180)
    BEST_MOVE_COLOR = (0, 255, 255, 180)
    COORD_BG = (220, 190, 150)
    COORD_TEXT = (0, 0, 0)
    PANEL_BG = WHITE
    PANEL_TEXT = BLACK
    BACK_BUTTON_COLOR = (200, 60, 60)
    CONFIRM_YES_COLOR = (60, 180, 75)
    CONFIRM_NO_COLOR = (200, 60, 60)
    DIALOG_BG = (240, 240, 240)

    def __init__(self, view_color=chess.WHITE):
        pygame.init()
        try:
            self.screen = pygame.display.set_mode(WINDOW_SIZE)
        except pygame.error as e:
            print(f"[FATAL] Failed to create display: {e}")
            pygame.quit()
            exit(1)

        pygame.display.set_caption("Chess App")
        self.view_color = view_color
        self.piece_images = self.load_piece_images()
        self.font = self.load_font()
        self.coord_font = pygame.font.SysFont("Arial", 16)

        # Pre-create surfaces for highlights (reusable)
        self.selected_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        self.selected_surface.fill(self.SELECTED_HIGHLIGHT)

        self.played_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        self.played_surface.fill(self.PLAYED_MOVE_COLOR)

        self.best_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        self.best_surface.fill(self.BEST_MOVE_COLOR)

        # Cache coordinate labels
        self._cache_coordinate_labels()

        # Button rects (will be set when drawn)
        self.back_button_rect = None
        self.confirm_yes_rect = None
        self.confirm_no_rect = None

    def load_font(self):
        try:
            return pygame.font.Font(FONT_PATH, 20)
        except (FileNotFoundError, OSError):
            return pygame.font.SysFont("Arial", 20)

    def load_piece_images(self):
        images = {}
        for piece, path in PIECE_IMAGES.items():
            full_path = os.path.join(ASSET_PATH, path.lstrip('/'))
            try:
                img = pygame.image.load(full_path).convert_alpha()
                images[piece] = pygame.transform.scale(img, (SQUARE_SIZE, SQUARE_SIZE))
            except Exception as e:
                print(f"[ERROR] Failed to load {full_path}: {e}")
        return images

    def _cache_coordinate_labels(self):
        """Pre-render coordinate labels for better performance."""
        self.coord_labels = {}
        # Files (a-h)
        for i in range(8):
            label = chr(ord('a') + i)
            self.coord_labels[f'file_{i}'] = self.coord_font.render(label, True, self.COORD_TEXT)
            label_flipped = chr(ord('h') - i)
            self.coord_labels[f'file_flipped_{i}'] = self.coord_font.render(label_flipped, True, self.COORD_TEXT)
        # Ranks (1-8)
        for i in range(8):
            label = str(i + 1)
            self.coord_labels[f'rank_{i}'] = self.coord_font.render(label, True, self.COORD_TEXT)
            label_flipped = str(8 - i)
            self.coord_labels[f'rank_flipped_{i}'] = self.coord_font.render(label_flipped, True, self.COORD_TEXT)

    def _square_to_screen(self, square, is_flipped):
        """Convert chess square to screen coordinates (col, row)."""
        col = chess.square_file(square)
        rank = chess.square_rank(square)

        if is_flipped:
            row = rank
        else:
            row = 7 - rank

        return col, row

    def _get_square_rect(self, col, row):
        """Get screen rectangle for a board square."""
        return pygame.Rect(
            COORD_MARGIN + col * SQUARE_SIZE,
            row * SQUARE_SIZE,
            SQUARE_SIZE,
            SQUARE_SIZE
        )

    def _get_square_center(self, col, row):
        """Get center coordinates of a board square."""
        return (
            COORD_MARGIN + col * SQUARE_SIZE + SQUARE_SIZE // 2,
            row * SQUARE_SIZE + SQUARE_SIZE // 2
        )

    def draw_board(self, board, selected_square, legal_moves, highlight_moves=None):
        if highlight_moves is None:
            highlight_moves = []

        self.screen.fill((30, 30, 30))
        is_flipped = (self.view_color == chess.BLACK)

        # Draw squares and pieces
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                # Checkerboard pattern
                color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
                rect = self._get_square_rect(col, row)
                pygame.draw.rect(self.screen, color, rect)

                # Determine which square this is
                square = chess.square(col, row if is_flipped else 7 - row)

                # Draw piece if present
                piece = board.piece_at(square)
                if piece:
                    symbol = piece.symbol()
                    color_key = 'w' if piece.color == chess.WHITE else 'b'
                    key = color_key + symbol.upper()
                    if key in self.piece_images:
                        self.screen.blit(self.piece_images[key], rect.topleft)

        # Highlight selected square
        if selected_square is not None:
            col, row = self._square_to_screen(selected_square, is_flipped)
            self.screen.blit(self.selected_surface, self._get_square_rect(col, row).topleft)

        # Highlight legal moves
        for move in legal_moves:
            col, row = self._square_to_screen(move.to_square, is_flipped)
            center = self._get_square_center(col, row)
            pygame.draw.circle(self.screen, self.LEGAL_MOVE_COLOR, center, SQUARE_SIZE // 6)

        # Highlight played/best moves (for replay)
        for move_type, move in highlight_moves:
            from_col, from_row = self._square_to_screen(move.from_square, is_flipped)
            to_col, to_row = self._square_to_screen(move.to_square, is_flipped)

            # Highlight FROM square
            surface = self.played_surface if move_type == "played" else self.best_surface
            self.screen.blit(surface, self._get_square_rect(from_col, from_row).topleft)

            # Draw circle on TO square
            center = self._get_square_center(to_col, to_row)
            color = (255, 255, 0) if move_type == "played" else (0, 255, 255)
            pygame.draw.circle(self.screen, color, center, SQUARE_SIZE // 3, 4)

        # Draw coordinates
        self._draw_coordinates(is_flipped)

        # Board border
        pygame.draw.rect(self.screen, (0, 0, 0), (COORD_MARGIN, 0, BOARD_WIDTH, BOARD_HEIGHT), 2)

    def _draw_coordinates(self, is_flipped):
        """Draw file and rank labels around the board."""
        # Files (bottom)
        for col in range(8):
            label_key = f'file_flipped_{col}' if is_flipped else f'file_{col}'
            label = self.coord_labels[label_key]

            bg_rect = pygame.Rect(
                COORD_MARGIN + col * SQUARE_SIZE,
                BOARD_HEIGHT,
                SQUARE_SIZE,
                COORD_MARGIN
            )
            pygame.draw.rect(self.screen, self.COORD_BG, bg_rect)

            text_x = bg_rect.centerx - label.get_width() // 2
            text_y = bg_rect.centery - label.get_height() // 2
            self.screen.blit(label, (text_x, text_y))

        # Ranks (left side)
        for row in range(8):
            label_key = f'rank_{row}' if is_flipped else f'rank_flipped_{row}'
            label = self.coord_labels[label_key]

            bg_rect = pygame.Rect(0, row * SQUARE_SIZE, COORD_MARGIN, SQUARE_SIZE)
            pygame.draw.rect(self.screen, self.COORD_BG, bg_rect)

            text_x = COORD_MARGIN - label.get_width() - 4
            text_y = bg_rect.centery - label.get_height() // 2
            self.screen.blit(label, (text_x, text_y))

    def draw_promotion_dialog(self, color_is_white):
        """Draw piece selection dialog for pawn promotion."""
        dialog_width = SQUARE_SIZE * 4
        dialog_height = SQUARE_SIZE
        x = COORD_MARGIN + (BOARD_WIDTH - dialog_width) // 2
        y = (BOARD_HEIGHT - dialog_height) // 2

        # Background
        pygame.draw.rect(self.screen, (50, 50, 50), (x, y, dialog_width, dialog_height))
        pygame.draw.rect(self.screen, (200, 200, 200), (x, y, dialog_width, dialog_height), 2)

        # Draw pieces
        pieces = ['Q', 'R', 'B', 'N']
        color_prefix = 'w' if color_is_white else 'b'
        for i, p in enumerate(pieces):
            piece_key = color_prefix + p
            if piece_key in self.piece_images:
                self.screen.blit(self.piece_images[piece_key], (x + i * SQUARE_SIZE, y))

    def draw_back_button(self):
        """Draw back button in the right panel."""
        panel_x = BOARD_WIDTH + COORD_MARGIN
        self.back_button_rect = pygame.Rect(panel_x + 10, WINDOW_SIZE[1] - 40, 100, 30)

        pygame.draw.rect(self.screen, self.BACK_BUTTON_COLOR, self.back_button_rect, border_radius=5)
        pygame.draw.rect(self.screen, (0, 0, 0), self.back_button_rect, 2, border_radius=5)

        text = self.font.render("Back", True, WHITE)
        text_rect = text.get_rect(center=self.back_button_rect.center)
        self.screen.blit(text, text_rect)

    def is_back_button_clicked(self, pos):
        """Check if back button was clicked."""
        return self.back_button_rect is not None and self.back_button_rect.collidepoint(pos)

    def draw_confirm_exit(self):
        """Draw confirmation dialog for exiting to menu."""
        # Semi-transparent overlay
        overlay = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        # Dialog box
        dialog_w, dialog_h = 300, 140
        x = WINDOW_SIZE[0] // 2 - dialog_w // 2
        y = WINDOW_SIZE[1] // 2 - dialog_h // 2

        pygame.draw.rect(self.screen, self.DIALOG_BG, (x, y, dialog_w, dialog_h), border_radius=8)
        pygame.draw.rect(self.screen, (0, 0, 0), (x, y, dialog_w, dialog_h), 2, border_radius=8)

        # Message
        msg = self.font.render("Go back to menu?", True, (0, 0, 0))
        msg_rect = msg.get_rect(center=(x + dialog_w // 2, y + 40))
        self.screen.blit(msg, msg_rect)

        # Yes button
        self.confirm_yes_rect = pygame.Rect(x + 30, y + 70, 80, 30)
        pygame.draw.rect(self.screen, self.CONFIRM_YES_COLOR, self.confirm_yes_rect, border_radius=5)
        yes_text = self.font.render("Yes", True, WHITE)
        yes_rect = yes_text.get_rect(center=self.confirm_yes_rect.center)
        self.screen.blit(yes_text, yes_rect)

        # No button
        self.confirm_no_rect = pygame.Rect(x + 190, y + 70, 80, 30)
        pygame.draw.rect(self.screen, self.CONFIRM_NO_COLOR, self.confirm_no_rect, border_radius=5)
        no_text = self.font.render("No", True, WHITE)
        no_rect = no_text.get_rect(center=self.confirm_no_rect.center)
        self.screen.blit(no_text, no_rect)

    def is_confirm_yes_clicked(self, pos):
        """Check if 'Yes' was clicked in confirmation dialog."""
        return self.confirm_yes_rect is not None and self.confirm_yes_rect.collidepoint(pos)

    def is_confirm_no_clicked(self, pos):
        """Check if 'No' was clicked in confirmation dialog."""
        return self.confirm_no_rect is not None and self.confirm_no_rect.collidepoint(pos)

    def draw_analysis(self, analysis_result, turn, analysis_enabled):
        """Draw analysis panel on the right side."""
        panel_x = BOARD_WIDTH + COORD_MARGIN
        panel_width = WINDOW_SIZE[0] - panel_x

        # Panel background
        pygame.draw.rect(self.screen, self.PANEL_BG, (panel_x, 0, panel_width, WINDOW_SIZE[1]))

        y = 10

        # Analysis info
        if analysis_enabled and analysis_result:
            eval_text = f"Evaluation: {analysis_result['type']} {analysis_result['value']}"
            move_text = f"Best Move: {analysis_result['best_move']}"
            self.screen.blit(self.font.render(eval_text, True, self.PANEL_TEXT), (panel_x + 10, y))
            self.screen.blit(self.font.render(move_text, True, self.PANEL_TEXT), (panel_x + 10, y + 30))
            y += 70
        elif not analysis_enabled:
            self.screen.blit(self.font.render("Analysis: OFF", True, self.PANEL_TEXT), (panel_x + 10, y))
            y += 40

        # Turn indicator
        turn_text = f"Turn: {'White' if turn == chess.WHITE else 'Black'}"
        self.screen.blit(self.font.render(turn_text, True, self.PANEL_TEXT), (panel_x + 10, y))
        y += 30

        # Instructions
        self.screen.blit(self.font.render("Press 'A' to toggle analysis", True, self.PANEL_TEXT), (panel_x + 10, y))
        self.screen.blit(self.font.render("← → to navigate moves", True, self.PANEL_TEXT), (panel_x + 10, y + 30))

    def draw_game_over(self, result):
        """Draw game over overlay."""
        overlay = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        text = self.font.render(result, True, WHITE)
        text_rect = text.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2))
        self.screen.blit(text, text_rect)

    def update(self):
        """Update the display."""
        pygame.display.flip()