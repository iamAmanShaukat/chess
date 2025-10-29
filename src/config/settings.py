# src/config/settings.py
import os
# Board settings

COORD_MARGIN = 24
BOARD_SIZE = 8
SQUARE_SIZE = 80

BOARD_WIDTH = BOARD_SIZE * SQUARE_SIZE
BOARD_HEIGHT = BOARD_SIZE * SQUARE_SIZE
# Window: board + right panel (300px) + margins
WINDOW_SIZE = (
    BOARD_WIDTH + 300 + COORD_MARGIN,
    BOARD_HEIGHT + COORD_MARGIN
)
FPS = 60

BOARD_OFFSET_X = COORD_MARGIN
BOARD_OFFSET_Y = 0

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)
HIGHLIGHT = (0, 255, 0, 100)

# Paths
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ASSET_PATH = os.path.join(PROJECT_ROOT, "assets")
PIECE_IMAGES = {
    'wP': '/images/wP.png', 'wN': '/images/wN.png', 'wB': '/images/wB.png',
    'wR': '/images/wR.png', 'wQ': '/images/wQ.png', 'wK': '/images/wK.png',
    'bP': '/images/bP.png', 'bN': '/images/bN.png', 'bB': '/images/bB.png',
    'bR': '/images/bR.png', 'bQ': '/images/bQ.png', 'bK': '/images/bK.png'
}
FONT_PATH = os.path.join(ASSET_PATH, "fonts", "arial.ttf")

# Stockfish settings
STOCKFISH_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "stockfish", "stockfish")
ANALYSIS_DEPTH = 17