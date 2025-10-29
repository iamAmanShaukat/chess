# src/core/analysis.py
from stockfish import Stockfish
from src.config.settings import STOCKFISH_PATH, ANALYSIS_DEPTH
import os

class ChessAnalysis:
    def __init__(self):
        self.enabled = False
        self.stockfish = None
        if os.path.exists(STOCKFISH_PATH):
            try:
                self.stockfish = Stockfish(path=STOCKFISH_PATH)
                self.stockfish.set_depth(ANALYSIS_DEPTH)
                self.enabled = True  # Only enable if loaded successfully
            except Exception as e:
                print(f"[WARNING] Failed to initialize Stockfish: {e}")
                self.enabled = False
        else:
            print(f"[WARNING] Stockfish executable not found at: {STOCKFISH_PATH}")
            self.enabled = False

    def toggle_analysis(self):
        if self.stockfish is not None:
            self.enabled = not self.enabled

    def analyze_position(self, fen):
        if not self.enabled or self.stockfish is None:
            return None
        try:
            self.stockfish.set_fen_position(fen)
            evaluation = self.stockfish.get_evaluation()
            best_move = self.stockfish.get_best_move()
            return {
                "type": evaluation["type"],
                "value": evaluation["value"],
                "best_move": best_move
            }
        except Exception as e:
            print(f"[ERROR] Stockfish analysis failed: {e}")
            return None