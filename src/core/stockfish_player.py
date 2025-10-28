# src/core/stockfish_player.py
import chess
from stockfish import Stockfish
from src.config.settings import STOCKFISH_PATH
import os
import random


class StockfishPlayer:
    def __init__(self, difficulty_level=1):
        self.difficulty = max(1, min(20, difficulty_level))
        self.stockfish = None
        self.mode = "normal"
        self._init_stockfish()

    def _init_stockfish(self):
        if not os.path.exists(STOCKFISH_PATH):
            raise RuntimeError(f"Stockfish not found at: {STOCKFISH_PATH}")

        try:
            # Smooth depth scaling: 1→5 (very low), 5→10 (low-mid), 10→20 (high)
            if self.difficulty <= 5:
                depth = 1 + self.difficulty  # 2→6
            elif self.difficulty <= 10:
                depth = 6 + (self.difficulty - 5)  # 7→11
            else:
                depth = 11 + (self.difficulty - 10)  # 12→21

            self.stockfish = Stockfish(path=STOCKFISH_PATH, depth=depth, parameters={"Threads": 1})

            # Smoother Elo curve: smaller jumps at lower levels
            if self.difficulty <= 5:
                elo = 800 + (self.difficulty - 1) * 50  # 800→1000 (50 per level)
            elif self.difficulty <= 10:
                elo = 1000 + (self.difficulty - 5) * 100  # 1000→1500 (100 per level)
            elif self.difficulty <= 15:
                elo = 1500 + (self.difficulty - 10) * 150  # 1500→2250 (150 per level)
            else:
                elo = 2250 + (self.difficulty - 15) * 50  # 2250→2500 (50 per level)

            # Skill level with diminishing returns
            skill = min(20, int((self.difficulty - 1) * 1.2))  # 0→20, but slower at top

            # Configure based on difficulty tiers
            if self.difficulty <= 8:
                self.mode = "beginner"
                self.stockfish.update_engine_parameters({
                    "Skill Level": skill,
                    "UCI_LimitStrength": True,
                    "UCI_Elo": elo
                })
            elif self.difficulty <= 16:
                self.mode = "intermediate"
                self.stockfish.update_engine_parameters({
                    "Skill Level": skill,
                    "UCI_LimitStrength": True,
                    "UCI_Elo": elo
                })
            else:
                self.mode = "advanced"
                self.stockfish.update_engine_parameters({
                    "Skill Level": 20,
                    "UCI_LimitStrength": False
                })

        except Exception as e:
            raise RuntimeError(f"Failed to initialize Stockfish: {e}")

    def get_move(self, board: chess.Board):
        """Return a move according to current difficulty level."""
        if not board.legal_moves:
            return None

        # Gradual reduction in random moves for beginners
        if self.difficulty <= 8:
            # Level 1: 50%, Level 2: 44%, Level 3: 38%... Level 8: 6%
            random_chance = max(0, 0.56 - (self.difficulty * 0.06))
            if random.random() < random_chance:
                return random.choice(list(board.legal_moves))

        self.stockfish.set_fen_position(board.fen())
        best_move_uci = self.stockfish.get_best_move()

        if best_move_uci:
            try:
                move = chess.Move.from_uci(best_move_uci)
                if move in board.legal_moves:
                    return move
            except ValueError:
                pass

        return random.choice(list(board.legal_moves))