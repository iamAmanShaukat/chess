# src/gui/input_handler.py
import pygame
import chess
from src.config.settings import SQUARE_SIZE, BOARD_SIZE, COORD_MARGIN


class InputHandler:
    def __init__(self, view_color=chess.WHITE):
        self.view_color = view_color
        self.board_x_start = COORD_MARGIN
        self.board_x_end = COORD_MARGIN + (BOARD_SIZE * SQUARE_SIZE)
        self.board_y_end = BOARD_SIZE * SQUARE_SIZE

    def set_view_color(self, color):
        self.view_color = color

    def get_square(self, pos):
        x, y = pos

        if not (self.board_x_start <= x < self.board_x_end and 0 <= y < self.board_y_end):
            return None

        col = (x - self.board_x_start) // SQUARE_SIZE
        row_from_top = y // SQUARE_SIZE

        row = (7 - row_from_top) if self.view_color == chess.WHITE else row_from_top

        return chess.square(col, row)