# src/core/game_controller.py
import chess
import time
import random
from src.core.board import ChessBoard
from src.core.player import Player

class GameController:
    def __init__(self, white_is_human=True, black_is_human=True):
        self.board = ChessBoard()
        self.white_player = Player(chess.WHITE, is_human=white_is_human)
        self.black_player = Player(chess.BLACK, is_human=black_is_human)
        self.game_over = False
        self.ai_move_pending = False
        self.move_history = []  # Store FEN or moves for undo
        self.awaiting_promotion = None  # (from_square, to_square) if promotion needed

    def handle_click(self, square, input_handler):
        if self.game_over or self.awaiting_promotion:
            return None

        current_player = self.white_player if self.board.board.turn == chess.WHITE else self.black_player
        if not current_player.is_human:
            return None

        if self.board.selected_square is None:
            self.board.select_square(square)
            return None
        else:
            from_sq = self.board.selected_square
            to_sq = square
            piece = self.board.board.piece_at(from_sq)

            # Only consider promotion if it's a pawn moving to rank 1/8
            if (piece and
                piece.piece_type == chess.PAWN and
                piece.color == self.board.board.turn and
                chess.square_rank(to_sq) in (0, 7)):

                # Check if ANY promotion is legal (Q, R, B, N)
                legal_promotions = []
                for promo in [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]:
                    move = chess.Move(from_sq, to_sq, promotion=promo)
                    if move in self.board.board.legal_moves:
                        legal_promotions.append(promo)

                if legal_promotions:
                    # Valid promotion move exists → show dialog
                    self.awaiting_promotion = (from_sq, to_sq)
                    return "awaiting_promotion"

            # Otherwise, try regular move
            move = chess.Move(from_sq, to_sq)
            if self.board.make_move(move):
                self.move_history.append(move)
                self.game_over = self.board.is_game_over()
                return move
            else:
                # Invalid move — reselect
                self.board.select_square(square)
                return None

    def handle_promotion_choice(self, piece_type):
        """Called when user selects Q/R/B/N for promotion."""
        if not self.awaiting_promotion:
            return
        from_sq, to_sq = self.awaiting_promotion
        move = chess.Move(from_sq, to_sq, promotion=piece_type)
        if move in self.board.board.legal_moves:
            self.board.make_move(move)
            self.move_history.append(move)
            self.game_over = self.board.is_game_over()
        self.awaiting_promotion = None

    def undo_last_move(self):
        """Undo last move if game is not over and no promotion pending."""
        if self.game_over or self.awaiting_promotion or not self.move_history:
            return False
        # Pop last move
        self.board.board.pop()
        self.move_history.pop()
        self.game_over = False
        # Clear selection
        self.board.selected_square = None
        self.board.legal_moves = []
        return True

    def update(self):
        if self.game_over or self.awaiting_promotion:
            return

        current_player = self.white_player if self.board.board.turn == chess.WHITE else self.black_player
        if not current_player.is_human:
            if not self.ai_move_pending:
                self.ai_move_pending = True
                time.sleep(0.3)
                move = current_player.get_random_move(self.board.board)
                if move:
                    # Handle AI promotion (auto-queen for now)
                    if (self.board.board.piece_at(move.from_square) and
                        self.board.board.piece_at(move.from_square).piece_type == chess.PAWN and
                        chess.square_rank(move.to_square) in (0, 7)):
                        move = chess.Move(move.from_square, move.to_square, promotion=chess.QUEEN)
                    self.board.make_move(move)
                    self.move_history.append(move)
                    self.game_over = self.board.is_game_over()
                self.ai_move_pending = False

    def get_game_result(self):
        return self.board.get_result() if self.game_over else None

    def is_game_over(self):
        return self.game_over

    def get_fen(self):
        return self.board.get_fen()

    def get_board(self):
        return self.board.board

    def get_selected_square(self):
        return self.board.selected_square

    def get_legal_moves(self):
        return self.board.legal_moves

    def is_awaiting_promotion(self):
        return self.awaiting_promotion is not None