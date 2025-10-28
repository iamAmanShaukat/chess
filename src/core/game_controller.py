# src/core/game_controller.py
import chess
import time
import random
import copy
from src.core.board import ChessBoard
from src.core.player import Player

class GameController:
    def __init__(self, white_is_human=True, black_is_human=True, white_difficulty=1, black_difficulty=1):
        self.board = ChessBoard()
        self.white_player = Player(chess.WHITE, is_human=white_is_human, difficulty_level=white_difficulty)
        self.black_player = Player(chess.BLACK, is_human=black_is_human, difficulty_level=black_difficulty)
        self.game_over = False
        self.ai_move_pending = False
        self.move_history = []
        self.awaiting_promotion = None

        # Replay & analysis
        self.analysis_history = []
        self.replay_mode = False
        self.replay_index = -1
        self.initial_fen = self.board.get_fen()

    def _save_analysis(self, analysis_result):
        self.analysis_history.append(copy.deepcopy(analysis_result))

    def handle_click(self, square, input_handler):
        if self.replay_mode or self.game_over or self.awaiting_promotion:
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

            if (piece and
                piece.piece_type == chess.PAWN and
                piece.color == self.board.board.turn and
                chess.square_rank(to_sq) in (0, 7)):

                legal_promotions = []
                for promo in [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]:
                    move = chess.Move(from_sq, to_sq, promotion=promo)
                    if move in self.board.board.legal_moves:
                        legal_promotions.append(promo)

                if legal_promotions:
                    self.awaiting_promotion = (from_sq, to_sq)
                    return "awaiting_promotion"

            move = chess.Move(from_sq, to_sq)
            if self.board.make_move(move):
                self.move_history.append(move)
                self.game_over = self.board.is_game_over()
                return move
            else:
                self.board.select_square(square)
                return None

    def handle_promotion_choice(self, piece_type):
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
        if self.replay_mode or self.game_over or self.awaiting_promotion or not self.move_history:
            return False
        self.board.board.pop()
        self.move_history.pop()
        if self.analysis_history:
            self.analysis_history.pop()
        self.game_over = False
        self.board.selected_square = None
        self.board.legal_moves = []
        return True

    def update(self):
        if self.replay_mode or self.game_over or self.awaiting_promotion:
            return

        current_player = self.white_player if self.board.board.turn == chess.WHITE else self.black_player
        if not current_player.is_human:
            if not self.ai_move_pending:
                self.ai_move_pending = True
                time.sleep(0.2)  # Slight delay
                move = current_player.get_move(self.board.board)
                if move:
                    # Handle promotion (auto-queen if needed)
                    if (self.board.board.piece_at(move.from_square) and
                        self.board.board.piece_at(move.from_square).piece_type == chess.PAWN and
                        chess.square_rank(move.to_square) in (0, 7)):
                        move = chess.Move(move.from_square, move.to_square, promotion=chess.QUEEN)
                    self.board.make_move(move)
                    self.move_history.append(move)
                    self.game_over = self.board.is_game_over()
                self.ai_move_pending = False

    def enter_replay_mode(self):
        self.replay_mode = True
        self.replay_index = len(self.move_history)

    def exit_replay_mode(self):
        if not self.game_over:
            self.replay_mode = False
            self.replay_index = -1

    def navigate_replay(self, direction):
        if not self.replay_mode:
            self.enter_replay_mode()
        new_index = self.replay_index + direction
        if 0 <= new_index <= len(self.move_history):
            self.replay_index = new_index

    def get_replay_board(self):
        board = chess.Board(self.initial_fen)
        for i in range(self.replay_index):
            board.push(self.move_history[i])
        return board

    def get_replay_analysis(self):
        if self.replay_index < len(self.analysis_history):
            return self.analysis_history[self.replay_index]
        return None

    def get_highlight_moves(self):
        if self.replay_index <= 0 or self.replay_index > len(self.move_history):
            return None, None
        played_move = self.move_history[self.replay_index - 1]
        best_move = None
        if self.replay_index - 1 < len(self.analysis_history):
            analysis = self.analysis_history[self.replay_index - 1]
            if analysis and analysis.get("best_move"):
                best_move = chess.Move.from_uci(analysis["best_move"])
        return played_move, best_move

    def get_board(self):
        return self.get_replay_board() if self.replay_mode else self.board.board

    def is_game_over(self):
        if self.replay_mode:
            board = self.get_replay_board()
            return board.is_game_over()
        return self.game_over

    def get_game_result(self):
        if self.replay_mode:
            board = self.get_replay_board()
            if board.is_checkmate():
                winner = "White" if board.turn == chess.BLACK else "Black"
                return f"Checkmate! {winner} wins!"
            elif board.is_stalemate():
                return "Stalemate!"
            elif board.is_insufficient_material():
                return "Draw by insufficient material!"
            else:
                return "Game over!"
        return self.board.get_result() if self.game_over else None

    def get_fen(self):
        return self.get_replay_board().fen() if self.replay_mode else self.board.get_fen()

    def get_selected_square(self):
        return self.board.selected_square

    def get_legal_moves(self):
        return self.board.legal_moves

    def is_awaiting_promotion(self):
        return self.awaiting_promotion is not None

    def is_replay_mode(self):
        return self.replay_mode