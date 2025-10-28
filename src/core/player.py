# src/core/player.py
import random
import chess

# src/core/player.py
import random
import chess
from src.core.stockfish_player import StockfishPlayer

class Player:
    def __init__(self, color, is_human=True, difficulty_level=1):
        self.color = color
        self.is_human = is_human
        self.difficulty_level = difficulty_level
        self.ai_engine = None
        if not is_human:
            self.ai_engine = StockfishPlayer(difficulty_level=difficulty_level)

    def get_move(self, board: chess.Board):
        """Get move from AI engine."""
        if self.is_human:
            return None
        if self.ai_engine:
            return self.ai_engine.get_move(board)
        else:
            return random.choice(list(board.legal_moves)) if board.legal_moves else None