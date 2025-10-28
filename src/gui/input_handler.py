# src/gui/input_handler.py
import pygame
import chess
from config.settings import SQUARE_SIZE, BOARD_SIZE
# src/gui/input_handler.py
import pygame
import chess
from src.config.settings import SQUARE_SIZE, BOARD_SIZE, COORD_MARGIN

class InputHandler:
    def get_square(self, pos):
        x, y = pos
        board_x_start = COORD_MARGIN
        board_y_start = 0
        board_width = BOARD_SIZE * SQUARE_SIZE
        board_height = BOARD_SIZE * SQUARE_SIZE

        # Check if click is inside the board area (excluding margins)
        if (board_x_start <= x < board_x_start + board_width and
            board_y_start <= y < board_y_start + board_height):
            rel_x = x - board_x_start
            rel_y = y - board_y_start
            col = rel_x // SQUARE_SIZE
            row = 7 - (rel_y // SQUARE_SIZE)  # flip row
            return chess.square(col, row)
        return None