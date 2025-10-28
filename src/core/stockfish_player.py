# src/core/stockfish_player.py
import chess
from stockfish import Stockfish
from src.config.settings import STOCKFISH_PATH, PROJECT_ROOT
import os
import random


class StockfishPlayer:
    def __init__(self, difficulty_level=1):
        """
        difficulty_level: int from 1 to 20
        - Level 1-5: Very weak (random + blunders)
        - Level 6-10: Moderate (low depth, skill cap)
        - Level 11-15: Strong (medium depth)
        - Level 16-20: Full strength
        """
        self.difficulty = max(1, min(20, difficulty_level))
        self.stockfish = None
        self._init_stockfish()

    def _init_stockfish(self):
        if not os.path.exists(STOCKFISH_PATH):
            print(f"[ERROR] Stockfish not found at: {STOCKFISH_PATH}")
            return

        try:
            self.stockfish = Stockfish(path=STOCKFISH_PATH, depth=18, parameters={"Threads": 1})

            # Map difficulty to Stockfish UCI parameters
            if self.difficulty <= 5:
                # Very weak: random moves + occasional Stockfish move
                self.mode = "random_with_blunders"
            elif self.difficulty <= 10:
                # Weak: limit skill and depth
                skill = self.difficulty - 1  # 0 to 9
                self.stockfish.update_engine_parameters({
                    "Skill Level": skill,
                    "UCI_LimitStrength": True,
                    "UCI_Elo": 800 + (skill * 100)  # 800 to 1700 Elo
                })
                self.mode = "limited"
            elif self.difficulty <= 15:
                # Strong: higher skill, no Elo cap
                skill = 10 + (self.difficulty - 10)  # 10 to 15
                self.stockfish.update_engine_parameters({
                    "Skill Level": skill,
                    "UCI_LimitStrength": False
                })
                self.mode = "strong"
            else:
                # Full strength
                self.stockfish.update_engine_parameters({
                    "Skill Level": 20,
                    "UCI_LimitStrength": False
                })
                self.mode = "full"
        except Exception as e:
            print(f"[ERROR] Failed to initialize Stockfish: {e}")
            self.stockfish = None

    def get_move(self, board: chess.Board):
        """Return a move based on difficulty level."""
        if self.stockfish is None:
            # Fallback to random
            return random.choice(list(board.legal_moves)) if board.legal_moves else None

        if self.mode == "random_with_blunders":
            # 70% random, 30% Stockfish (but even Stockfish may blunder at low depth)
            if random.random() < 0.7:
                return random.choice(list(board.legal_moves))
            else:
                self.stockfish.set_fen_position(board.fen())
                best = self.stockfish.get_best_move()
                if best:
                    return chess.Move.from_uci(best)
                else:
                    return random.choice(list(board.legal_moves))

        else:
            # Use Stockfish with configured strength
            self.stockfish.set_fen_position(board.fen())
            best = self.stockfish.get_best_move()
            if best:
                return chess.Move.from_uci(best)
            else:
                return random.choice(list(board.legal_moves))