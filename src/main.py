# src/main.py
from src.config.settings import FPS, COORD_MARGIN, BOARD_WIDTH, BOARD_HEIGHT, SQUARE_SIZE

# src/main.py
import pygame
import chess
from src.gui.menu import Menu
from src.gui.display import Display
from src.gui.input_handler import InputHandler
from src.core.game_controller import GameController
from src.core.analysis import ChessAnalysis
from src.config.settings import FPS, COORD_MARGIN, BOARD_WIDTH

def run_game(white_human=True, black_human=True):
    """Run a single game instance."""
    controller = GameController(white_is_human=white_human, black_is_human=black_human)
    analysis = ChessAnalysis()
    display = Display()
    input_handler = InputHandler()
    clock = pygame.time.Clock()

    last_fen = controller.get_fen()
    analysis_result = None
    show_confirm_exit = False  # For back-to-menu confirmation

    running = True
    while running:
        controller.update()

        current_fen = controller.get_fen()
        if analysis.enabled and current_fen != last_fen:
            analysis_result = analysis.analyze_position(current_fen)
            last_fen = current_fen

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    analysis.toggle_analysis()
                elif event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    controller.undo_last_move()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos

                # Handle confirmation dialog
                if show_confirm_exit:
                    if display.is_confirm_yes_clicked(mouse_pos):
                        return "back_to_menu"
                    elif display.is_confirm_no_clicked(mouse_pos):
                        show_confirm_exit = False
                elif controller.is_awaiting_promotion():
                    # Handle promotion
                    x, y = mouse_pos
                    dialog_x = COORD_MARGIN + (BOARD_WIDTH - SQUARE_SIZE * 4) // 2
                    dialog_y = (8 * SQUARE_SIZE - SQUARE_SIZE) // 2
                    if dialog_x <= x < dialog_x + SQUARE_SIZE * 4 and dialog_y <= y < dialog_y + SQUARE_SIZE:
                        piece_index = (x - dialog_x) // SQUARE_SIZE
                        promo_map = [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]
                        if 0 <= piece_index < 4:
                            controller.handle_promotion_choice(promo_map[piece_index])
                else:
                    # Check if "Back" button clicked
                    if display.is_back_button_clicked(mouse_pos):
                        show_confirm_exit = True
                    else:
                        square = input_handler.get_square(mouse_pos)
                        if square is not None:
                            result = controller.handle_click(square, input_handler)
                            if result == "awaiting_promotion":
                                pass

        # --- RENDER ---
        display.draw_board(
            controller.get_board(),
            controller.get_selected_square(),
            controller.get_legal_moves()
        )

        if controller.is_awaiting_promotion():
            turn = controller.get_board().turn
            display.draw_promotion_dialog(color_is_white=turn)

        display.draw_analysis(analysis_result, controller.get_board().turn, analysis.enabled)
        display.draw_back_button()  # Always draw back button

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
        mode, human_color = menu.show_start_screen()

        if mode == "human_vs_human":
            white_human = True
            black_human = True
        else:  # human_vs_ai
            white_human = (human_color == chess.WHITE)
            black_human = (human_color == chess.BLACK)

        result = run_game(white_human=white_human, black_human=black_human)
        if result == "quit":
            break
        elif result == "back_to_menu":
            continue

    pygame.quit()

if __name__ == "__main__":
    main()