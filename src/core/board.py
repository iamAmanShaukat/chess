# src/core/board.py
import chess

class ChessBoard:
    def __init__(self):
        self.board = chess.Board()
        self.selected_square = None
        self.legal_moves = []

    def select_square(self, square):
        """Select a square and get legal moves for the piece."""
        self.selected_square = square
        self.legal_moves = [
            move for move in self.board.legal_moves
            if move.from_square == square
        ]
        return self.legal_moves

    def make_move(self, move):
        """Make a move on the board."""
        if move in self.board.legal_moves:
            self.board.push(move)
            self.selected_square = None
            self.legal_moves = []
            return True
        return False

    def get_fen(self):
        """Get the current board position in FEN."""
        return self.board.fen()

    def is_game_over(self):
        """Check if the game is over."""
        return self.board.is_game_over()

    def get_result(self):
        """Get the game result."""
        if self.board.is_checkmate():
            return "Checkmate! " + ("White wins!" if self.board.turn == chess.BLACK else "Black wins!")
        elif self.board.is_stalemate():
            return "Stalemate!"
        elif self.board.is_insufficient_material():
            return "Draw by insufficient material!"
        else:
            return "Game over!"