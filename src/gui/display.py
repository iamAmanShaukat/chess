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

    def load_font(self):
        try:
            return pygame.font.Font(FONT_PATH, 20)
        except FileNotFoundError:
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

    def draw_board(self, board, selected_square, legal_moves):
        self.screen.fill((30, 30, 30))
        board_x = COORD_MARGIN
        board_y = 0

        is_flipped = (self.view_color == chess.BLACK)

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
                rect = (board_x + col * SQUARE_SIZE, board_y + row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                pygame.draw.rect(self.screen, color, rect)

                # Determine which square to show based on flip
                if is_flipped:
                    # Black at bottom: file a-h still left-right, but rank 8-1 becomes 1-8 visually
                    square = chess.square(col, row)  # row 0 = rank 1 (bottom for black)
                else:
                    square = chess.square(col, 7 - row)  # row 0 = rank 8 (top)

                piece = board.piece_at(square)
                if piece:
                    symbol = piece.symbol()
                    color_key = 'w' if piece.color == chess.WHITE else 'b'
                    key = color_key + symbol.upper()
                    if key in self.piece_images:
                        self.screen.blit(
                            self.piece_images[key],
                            (board_x + col * SQUARE_SIZE, board_y + row * SQUARE_SIZE)
                        )

        # Highlighting: convert selected square to screen coords based on flip
        if selected_square is not None:
            if is_flipped:
                col = chess.square_file(selected_square)
                row = chess.square_rank(selected_square)  # 0 = rank 1 (bottom)
            else:
                col = chess.square_file(selected_square)
                row = 7 - chess.square_rank(selected_square)

            s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            s.fill(HIGHLIGHT)
            self.screen.blit(s, (board_x + col * SQUARE_SIZE, board_y + row * SQUARE_SIZE))

            for move in legal_moves:
                to_sq = move.to_square
                if is_flipped:
                    to_col = chess.square_file(to_sq)
                    to_row = chess.square_rank(to_sq)
                else:
                    to_col = chess.square_file(to_sq)
                    to_row = 7 - chess.square_rank(to_sq)

                center = (
                    board_x + to_col * SQUARE_SIZE + SQUARE_SIZE // 2,
                    board_y + to_row * SQUARE_SIZE + SQUARE_SIZE // 2
                )
                pygame.draw.circle(self.screen, (0, 200, 0), center, SQUARE_SIZE // 6)

        # >>> COORDINATES: adjust based on flip <<<
        coord_font = pygame.font.SysFont("Arial", 16)
        coord_bg = (220, 190, 150)
        text_color = (0, 0, 0)

        if is_flipped:
            # Files: h to a (right to left)
            for col in range(8):
                label = coord_font.render(chr(ord('h') - col), True, text_color)
                bg_rect = pygame.Rect(COORD_MARGIN + col * SQUARE_SIZE, BOARD_HEIGHT, SQUARE_SIZE, COORD_MARGIN)
                pygame.draw.rect(self.screen, coord_bg, bg_rect)
                text_x = COORD_MARGIN + col * SQUARE_SIZE + (SQUARE_SIZE - label.get_width()) // 2
                text_y = BOARD_HEIGHT + (COORD_MARGIN - label.get_height()) // 2
                self.screen.blit(label, (text_x, text_y))

            # Ranks: 1 to 8 (bottom to top)
            for row in range(8):
                label = coord_font.render(str(row + 1), True, text_color)
                bg_rect = pygame.Rect(0, row * SQUARE_SIZE, COORD_MARGIN, SQUARE_SIZE)
                pygame.draw.rect(self.screen, coord_bg, bg_rect)
                text_x = COORD_MARGIN - label.get_width() - 4
                text_y = row * SQUARE_SIZE + (SQUARE_SIZE - label.get_height()) // 2
                self.screen.blit(label, (text_x, text_y))
        else:
            # Standard: a-h, 8-1
            for col in range(8):
                label = coord_font.render(chr(ord('a') + col), True, text_color)
                bg_rect = pygame.Rect(COORD_MARGIN + col * SQUARE_SIZE, BOARD_HEIGHT, SQUARE_SIZE, COORD_MARGIN)
                pygame.draw.rect(self.screen, coord_bg, bg_rect)
                text_x = COORD_MARGIN + col * SQUARE_SIZE + (SQUARE_SIZE - label.get_width()) // 2
                text_y = BOARD_HEIGHT + (COORD_MARGIN - label.get_height()) // 2
                self.screen.blit(label, (text_x, text_y))

            for row in range(8):
                label = coord_font.render(str(8 - row), True, text_color)
                bg_rect = pygame.Rect(0, row * SQUARE_SIZE, COORD_MARGIN, SQUARE_SIZE)
                pygame.draw.rect(self.screen, coord_bg, bg_rect)
                text_x = COORD_MARGIN - label.get_width() - 4
                text_y = row * SQUARE_SIZE + (SQUARE_SIZE - label.get_height()) // 2
                self.screen.blit(label, (text_x, text_y))

        # Border
        board_rect = pygame.Rect(board_x, board_y, BOARD_WIDTH, BOARD_HEIGHT)
        pygame.draw.rect(self.screen, (0, 0, 0), board_rect, 2)

    def draw_analysis(self, analysis_result, turn, analysis_enabled):
        panel_x = BOARD_WIDTH + COORD_MARGIN  # Right after the board (including left margin)
        panel_width = WINDOW_SIZE[0] - panel_x
        pygame.draw.rect(self.screen, WHITE, (panel_x, 0, panel_width, WINDOW_SIZE[1]))

        y = 10
        if analysis_enabled and analysis_result:
            eval_text = f"Evaluation: {analysis_result['type']} {analysis_result['value']}"
            move_text = f"Best Move: {analysis_result['best_move']}"
            self.screen.blit(self.font.render(eval_text, True, BLACK), (panel_x + 10, y))
            self.screen.blit(self.font.render(move_text, True, BLACK), (panel_x + 10, y + 30))
            y += 70
        elif not analysis_enabled:
            self.screen.blit(self.font.render("Analysis: OFF", True, BLACK), (panel_x + 10, y))
            y += 40

        turn_text = f"Turn: {'White' if turn == chess.WHITE else 'Black'}"
        self.screen.blit(self.font.render(turn_text, True, BLACK), (panel_x + 10, y))
        y += 30
        self.screen.blit(self.font.render("Press 'A' to toggle analysis", True, BLACK), (panel_x + 10, y))

    def draw_game_over(self, result):
        s = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        self.screen.blit(s, (0, 0))
        text = self.font.render(result, True, WHITE)
        text_rect = text.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2))
        self.screen.blit(text, text_rect)

    def draw_promotion_dialog(self, color_is_white):
        """Draw queen, rook, bishop, knight for promotion."""
        dialog_width = SQUARE_SIZE * 4
        dialog_height = SQUARE_SIZE
        board_x = COORD_MARGIN
        board_y = 0

        # Center dialog at top of board
        x = board_x + (BOARD_WIDTH - dialog_width) // 2
        y = board_y + (BOARD_HEIGHT - dialog_height) // 2

        # Background
        s = pygame.Surface((dialog_width, dialog_height))
        s.fill((50, 50, 50))
        self.screen.blit(s, (x, y))
        pygame.draw.rect(self.screen, (200, 200, 200), (x, y, dialog_width, dialog_height), 2)

        pieces = ['Q', 'R', 'B', 'N']
        color_prefix = 'w' if color_is_white else 'b'

        for i, p in enumerate(pieces):
            piece_key = color_prefix + p
            if piece_key in self.piece_images:
                self.screen.blit(self.piece_images[piece_key], (x + i * SQUARE_SIZE, y))

    def draw_back_button(self):
        """Draw 'Back' button in analysis panel."""
        panel_x = BOARD_WIDTH + COORD_MARGIN
        btn_rect = pygame.Rect(panel_x + 10, WINDOW_SIZE[1] - 40, 100, 30)
        pygame.draw.rect(self.screen, (200, 60, 60), btn_rect, border_radius=5)
        pygame.draw.rect(self.screen, (0, 0, 0), btn_rect, 2, border_radius=5)
        text = self.font.render("Back", True, WHITE)
        self.screen.blit(text, (btn_rect.centerx - text.get_width() // 2, btn_rect.centery - text.get_height() // 2))
        self.back_button_rect = btn_rect  # Save for click detection

    def is_back_button_clicked(self, pos):
        """Check if back button was clicked."""
        return hasattr(self, 'back_button_rect') and self.back_button_rect.collidepoint(pos)

    def draw_confirm_exit(self):
        """Draw confirmation dialog for exiting to menu."""
        overlay = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        dialog_w, dialog_h = 300, 140
        x = WINDOW_SIZE[0] // 2 - dialog_w // 2
        y = WINDOW_SIZE[1] // 2 - dialog_h // 2

        pygame.draw.rect(self.screen, (240, 240, 240), (x, y, dialog_w, dialog_h), border_radius=8)
        pygame.draw.rect(self.screen, (0, 0, 0), (x, y, dialog_w, dialog_h), 2, border_radius=8)

        msg = self.font.render("Go back to menu?", True, (0, 0, 0))
        self.screen.blit(msg, (x + dialog_w // 2 - msg.get_width() // 2, y + 20))

        # Yes button
        self.confirm_yes_rect = pygame.Rect(x + 30, y + 70, 80, 30)
        pygame.draw.rect(self.screen, (60, 180, 75), self.confirm_yes_rect, border_radius=5)
        yes_text = self.font.render("Yes", True, WHITE)
        self.screen.blit(yes_text, (self.confirm_yes_rect.centerx - yes_text.get_width() // 2,
                                    self.confirm_yes_rect.centery - yes_text.get_height() // 2))

        # No button
        self.confirm_no_rect = pygame.Rect(x + 190, y + 70, 80, 30)
        pygame.draw.rect(self.screen, (200, 60, 60), self.confirm_no_rect, border_radius=5)
        no_text = self.font.render("No", True, WHITE)
        self.screen.blit(no_text, (self.confirm_no_rect.centerx - no_text.get_width() // 2,
                                   self.confirm_no_rect.centery - no_text.get_height() // 2))

    def is_confirm_yes_clicked(self, pos):
        return hasattr(self, 'confirm_yes_rect') and self.confirm_yes_rect.collidepoint(pos)

    def is_confirm_no_clicked(self, pos):
        return hasattr(self, 'confirm_no_rect') and self.confirm_no_rect.collidepoint(pos)

    def update(self):
        pygame.display.flip()