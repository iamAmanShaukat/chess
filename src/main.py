# src/main.py
from src.config.settings import FPS, COORD_MARGIN, BOARD_WIDTH, BOARD_HEIGHT, SQUARE_SIZE

import pygame
import chess
from src.gui.menu import Menu
from src.gui.display import Display
from src.gui.input_handler import InputHandler
from src.core.game_controller import GameController
from src.core.analysis import ChessAnalysis
from src.config.settings import FPS, COORD_MARGIN, BOARD_WIDTH


def run_game(white_human=True, black_human=True, white_difficulty=1, black_difficulty=1):
    controller = GameController(
        white_is_human=white_human,
        black_is_human=black_human,
        white_difficulty=white_difficulty,
        black_difficulty=black_difficulty
    )

    if white_human and not black_human:
        view_color = chess.WHITE
    elif black_human and not white_human:
        view_color = chess.BLACK
    else:
        view_color = chess.WHITE

    analysis = ChessAnalysis()
    display = Display(view_color=view_color)
    input_handler = InputHandler(view_color=view_color)
    clock = pygame.time.Clock()

    if analysis.enabled:
        initial_analysis = analysis.analyze_position(controller.get_fen())
    else:
        initial_analysis = None
    controller._save_analysis(initial_analysis)

    last_fen = controller.get_fen()
    analysis_result = initial_analysis

    show_confirm_exit = False

    running = True
    while running:
        current_fen = controller.get_fen()
        if current_fen != last_fen:
            if analysis.enabled:
                analysis_result = analysis.analyze_position(current_fen)
            else:
                analysis_result = None
            controller._save_analysis(analysis_result)
            last_fen = current_fen

        controller.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    analysis.toggle_analysis()
                elif event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    if not controller.replay_mode:
                        controller.undo_last_move()
                        last_fen = controller.get_fen()
                elif event.key == pygame.K_LEFT:
                    controller.navigate_replay(-1)
                elif event.key == pygame.K_RIGHT:
                    controller.navigate_replay(+1)
                elif event.key == pygame.K_ESCAPE:
                    controller.exit_replay_mode()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if show_confirm_exit:
                    if display.is_confirm_yes_clicked(mouse_pos):
                        return "back_to_menu"
                    elif display.is_confirm_no_clicked(mouse_pos):
                        show_confirm_exit = False
                elif controller.is_awaiting_promotion():
                    x, y = mouse_pos
                    dialog_x = COORD_MARGIN + (BOARD_WIDTH - SQUARE_SIZE * 4) // 2
                    dialog_y = (8 * SQUARE_SIZE - SQUARE_SIZE) // 2
                    if dialog_x <= x < dialog_x + SQUARE_SIZE * 4 and dialog_y <= y < dialog_y + SQUARE_SIZE:
                        piece_index = (x - dialog_x) // SQUARE_SIZE
                        promo_map = [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]
                        if 0 <= piece_index < 4:
                            controller.handle_promotion_choice(promo_map[piece_index])
                else:
                    if display.is_back_button_clicked(mouse_pos):
                        show_confirm_exit = True
                    else:
                        square = input_handler.get_square(mouse_pos)
                        if square is not None:
                            result = controller.handle_click(square, input_handler)
                            if result == "awaiting_promotion":
                                pass

        # Get analysis to show
        if controller.replay_mode:
            display_analysis = controller.get_replay_analysis()
            turn = controller.get_board().turn
        else:
            display_analysis = analysis_result
            turn = controller.get_board().turn

        # Get moves to highlight
        played_move, best_move = controller.get_highlight_moves()
        highlight_moves = []
        if played_move:
            highlight_moves.append(("played", played_move))
        if best_move:
            highlight_moves.append(("best", best_move))

        # Render
        display.draw_board(
            controller.get_board(),
            controller.get_selected_square() if not controller.replay_mode else None,
            controller.get_legal_moves() if not controller.replay_mode else [],
            highlight_moves=highlight_moves
        )

        if controller.is_awaiting_promotion():
            turn_color = controller.get_board().turn
            display.draw_promotion_dialog(color_is_white=turn_color)

        display.draw_analysis(display_analysis, turn, analysis.enabled)
        display.draw_back_button()

        if show_confirm_exit:
            display.draw_confirm_exit()

        if controller.is_game_over():
            display.draw_game_over(controller.get_game_result())

        display.update()
        clock.tick(FPS)

    return "quit"


def main():
    while True:
        menu = Menu()
        menu_result = menu.show_start_screen()

        if menu_result[0] == "human_vs_human":
            mode = "human_vs_human"
            human_color = None
            difficulty = 1
        else:
            mode, human_color, difficulty = menu_result
        if mode == "human_vs_human":
            white_human, black_human = True, True
            white_diff, black_diff = 1, 1
        else:
            white_human = (human_color == chess.WHITE)
            black_human = (human_color == chess.BLACK)
            if white_human:
                white_diff, black_diff = 1, difficulty
            else:
                white_diff, black_diff = difficulty, 1

        result = run_game(
                white_human=white_human,
                black_human=black_human,
                white_difficulty=white_diff,
                black_difficulty=black_diff
            )
        if result == "quit":
            break
        elif result == "back_to_menu":
            continue
    pygame.quit()


if __name__ == "__main__":
    main()