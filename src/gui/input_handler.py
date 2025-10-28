# src/gui/input_handler.py
import pygame
import chess
from src.config.settings import SQUARE_SIZE, BOARD_SIZE, COORD_MARGIN

class InputHandler:
    def __init__(self, view_color=chess.WHITE):
        self.view_color = view_color

    def get_square(self, pos):
        x, y = pos
        board_x_start = COORD_MARGIN
        board_y_start = 0
        board_width = BOARD_SIZE * SQUARE_SIZE
        board_height = BOARD_SIZE * SQUARE_SIZE

        if not (board_x_start <= x < board_x_start + board_width and
                board_y_start <= y < board_y_start + board_height):
            return None

        rel_x = x - board_x_start
        rel_y = y - board_y_start
        col = rel_x // SQUARE_SIZE

        # Flip row interpretation based on view_color
        if self.view_color == chess.WHITE:
            # White at bottom: screen row 0 = rank 8
            row = 7 - (rel_y // SQUARE_SIZE)
        else:
            # Black at bottom: screen row 0 = rank 1 → so row = rel_y // SQUARE_SIZE
            row = rel_y // SQUARE_SIZE

        return chess.square(col, row)