# src/main.py
import pygame
import chess
from src.gui.menu import Menu
from src.gui.display import Display
from src.gui.input_handler import InputHandler
from src.core.game_controller import GameController
from src.core.analysis import ChessAnalysis
from src.config.settings import FPS, COORD_MARGIN, BOARD_WIDTH, SQUARE_SIZE


def run_game(white_human=True, black_human=True, white_difficulty=1, black_difficulty=1):
    controller = GameController(
        white_is_human=white_human,
        black_is_human=black_human,
        white_difficulty=white_difficulty,
        black_difficulty=black_difficulty
    )

    # Determine view orientation
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

    # Initial analysis
    initial_analysis = analysis.analyze_position(controller.get_fen()) if analysis.enabled else None
    controller._save_analysis(initial_analysis)

    # State tracking
    last_fen = controller.get_fen()
    analysis_result = initial_analysis
    show_confirm_exit = False
    needs_rerender = True  # Flag to track when display needs updating

    running = True
    while running:
        # Only analyze if position changed
        current_fen = controller.get_fen()
        if current_fen != last_fen:
            if analysis.enabled and not controller.replay_mode:
                analysis_result = analysis.analyze_position(current_fen)
                controller._save_analysis(analysis_result)
            last_fen = current_fen
            needs_rerender = True

        # Update game state (AI moves, etc.)
        state_changed = controller.update()
        if state_changed:
            needs_rerender = True

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            elif event.type == pygame.KEYDOWN:
                needs_rerender = True
                if event.key == pygame.K_a:
                    new_state = analysis.toggle_analysis()
                    # Re-analyze current position if just enabled
                    if new_state and not controller.replay_mode:
                        analysis_result = analysis.analyze_position(controller.get_fen())
                        controller._save_analysis(analysis_result)

                elif event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    if not controller.replay_mode:
                        controller.undo_last_move()
                        last_fen = controller.get_fen()
                        if analysis.enabled:
                            analysis_result = analysis.analyze_position(last_fen)
                            controller._save_analysis(analysis_result)

                elif event.key == pygame.K_LEFT:
                    controller.navigate_replay(-1)

                elif event.key == pygame.K_RIGHT:
                    controller.navigate_replay(+1)

                elif event.key == pygame.K_ESCAPE:
                    controller.exit_replay_mode()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                needs_rerender = True
                mouse_pos = event.pos

                # Handle confirmation dialog
                if show_confirm_exit:
                    if display.is_confirm_yes_clicked(mouse_pos):
                        return "back_to_menu"
                    elif display.is_confirm_no_clicked(mouse_pos):
                        show_confirm_exit = False
                    continue

                # Handle promotion dialog
                if controller.is_awaiting_promotion():
                    x, y = mouse_pos
                    dialog_x = COORD_MARGIN + (BOARD_WIDTH - SQUARE_SIZE * 4) // 2
                    dialog_y = (8 * SQUARE_SIZE - SQUARE_SIZE) // 2

                    if dialog_x <= x < dialog_x + SQUARE_SIZE * 4 and dialog_y <= y < dialog_y + SQUARE_SIZE:
                        piece_index = (x - dialog_x) // SQUARE_SIZE
                        promo_map = [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]
                        if 0 <= piece_index < 4:
                            controller.handle_promotion_choice(promo_map[piece_index])
                    continue

                # Handle back button
                if display.is_back_button_clicked(mouse_pos):
                    show_confirm_exit = True
                    continue

                # Handle board clicks
                square = input_handler.get_square(mouse_pos)
                if square is not None:
                    controller.handle_click(square, input_handler)

        # Only render if something changed
        if not needs_rerender:
            clock.tick(FPS)
            continue

        # Determine what to display
        if controller.replay_mode:
            display_analysis = controller.get_replay_analysis()
        else:
            display_analysis = analysis_result

        turn = controller.get_board().turn

        # Get highlight moves
        played_move, best_move = controller.get_highlight_moves()
        highlight_moves = []
        if played_move:
            highlight_moves.append(("played", played_move))
        if best_move:
            highlight_moves.append(("best", best_move))

        # Render everything
        display.draw_board(
            controller.get_board(),
            controller.get_selected_square() if not controller.replay_mode else None,
            controller.get_legal_moves() if not controller.replay_mode else [],
            highlight_moves=highlight_moves
        )

        if controller.is_awaiting_promotion():
            display.draw_promotion_dialog(color_is_white=turn)

        display.draw_analysis(display_analysis, turn, analysis.enabled)
        display.draw_back_button()

        if show_confirm_exit:
            display.draw_confirm_exit()

        if controller.is_game_over():
            display.draw_game_over(controller.get_game_result())

        display.update()
        needs_rerender = False
        clock.tick(FPS)

    return "quit"


def main():
    while True:
        menu = Menu()
        menu_result = menu.show_start_screen()
        if menu_result is None:  # User closed window
            break

        if menu_result[0] == "human_vs_human":
            white_human, black_human = True, True
            white_diff, black_diff = 1, 1
        else:
            mode, human_color, difficulty = menu_result
            white_human = (human_color == chess.WHITE)
            black_human = (human_color == chess.BLACK)
            white_diff = 1 if white_human else difficulty
            black_diff = 1 if black_human else difficulty

        result = run_game(
            white_human=white_human,
            black_human=black_human,
            white_difficulty=white_diff,
            black_difficulty=black_diff
        )

        if result == "quit":
            break

    pygame.quit()


if __name__ == "__main__":
    main()