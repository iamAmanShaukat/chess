# src/core/player.py
import random
import chess

class Player:
    def __init__(self, color, is_human=True):
        self.color = color
        self.is_human = is_human

    def get_random_move(self, board):
        """Return a random legal move. Only for AI."""
        if self.is_human:
            return None
        legal_moves = list(board.legal_moves)
        return random.choice(legal_moves) if legal_moves else None