# 🏁 Chess App – A Modern Chess GUI with AI Analysis

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![Pygame](https://img.shields.io/badge/Pygame-2.6%2B-green?logo=pygame)
![Stockfish](https://img.shields.io/badge/Stockfish-Engines-FF6F00)

A feature-rich, modular chess application built with Python, Pygame, and Stockfish. Play against a human or AI with **20 difficulty levels**, review your games with **move-by-move analysis**, and visualize engine suggestions in real time.

---

## ✨ Features

- **Multiple Game Modes**:
  - Human vs Human
  - Human vs AI (play as White or Black)
- **Gradual AI Difficulty** (Levels 1–20):
  - Level 1: Random moves (beginner-friendly)
  - Level 10: ~1700 Elo (club player)
  - Level 20: Full Stockfish strength
- **Interactive Analysis**:
  - Toggle Stockfish evaluation on/off
  - View **what you played** vs. **what the engine recommended** at each move
- **Game Review Tools**:
  - Navigate history with **← / → arrow keys**
  - Highlight played (🟡 yellow) and best (🔵 cyan) moves
  - Works even after game ends
- **User Experience**:
  - Clean board with algebraic notation (`a–h`, `1–8`)
  - Flipped board when playing as Black
  - Promotion dialog (choose Q/R/B/N)
  - Undo moves (`Ctrl+Z`)
  - Back to menu with confirmation
- **Modular & Extensible**:
  - Clean separation of concerns (GUI, core logic, AI, config)
  - Easy to add new engines or features

---

## 🗂️ System Architecture

```
src/
├── config/
│   └── settings.py          # Constants, paths, colors
├── core/
│   ├── board.py             # Wraps python-chess.Board
│   ├── game_controller.py   # Orchestrates game flow, replay, history
│   ├── player.py            # Human/AI player abstraction
│   ├── stockfish_player.py  # Stockfish AI with difficulty levels
│   └── analysis.py          # Stockfish evaluation wrapper
├── gui/
│   ├── display.py           # Renders board, pieces, UI
│   ├── input_handler.py     # Mouse/click logic (flipped-aware)
│   └── menu.py              # Start screen & difficulty selector
└── main.py                  # Entry point & game loop
```

### Key Design Principles

- **Single Responsibility**: Each module has one clear purpose.
- **State Encapsulation**: `GameController` owns all game state.
- **Replay System**: Move history + analysis snapshots enable full post-game review.
- **Flipped View**: Board orientation adapts to player color (White/Black at bottom).
- **Non-blocking AI**: Stockfish runs without freezing the UI.

---

## 🚀 Installation

### Prerequisites
- Python 3.8+
- [Stockfish](https://stockfishchess.org/download/) (v14+ recommended)

### Steps

1. **Clone the repo**
   ```bash
   git clone https://github.com/your-username/chess-app.git
   cd chess-app
   ```

2. **Install dependencies**
   ```bash
   pip install pygame python-chess stockfish
   ```

3. **Download Stockfish**
   - **Windows**: Get `stockfish.exe` from [stockfishchess.org](https://stockfishchess.org/download/)
   - **macOS/Linux**: Use Homebrew or download binary
   - Place the executable in:
     ```
     chess-app/
     └── stockfish/
         └── stockfish        # (or stockfish.exe on Windows)
     ```

4. **Add chess piece images**
   - Create folder: `assets/images/`
   - Add PNGs named: `wP.png`, `wN.png`, ..., `bK.png`
   - (Optional) Add `assets/fonts/arial.ttf` for custom font

---

## ▶️ Running the App

```bash
python -m src.main
```

> 💡 **Note**: Run from the **project root** (parent of `src/`).

---

## 🎮 Controls

| Action | Key / Click |
|-------|-------------|
| Select square | Mouse click |
| Promote pawn | Click piece in dialog |
| Toggle analysis | `A` |
| Undo move | `Ctrl + Z` |
| Navigate moves | `←` / `→` |
| Exit replay | `Esc` |
| Back to menu | Click "Back" → Confirm |

---

## 🧠 AI Difficulty Levels

| Level | Behavior |
|-------|--------|
| 1–5 | Mostly random moves; occasional blunders |
| 6–10 | Limited strength (800–1700 Elo); makes tactical errors |
| 11–15 | Strong play; rarely blunders |
| 16–20 | Full engine strength; near-perfect play |

> The progression is **smooth** — each level is slightly stronger than the last.

---

## 📦 Project Structure Details

### Core Logic
- **`GameController`**: The brain. Handles turns, AI, replay, history, and state.
- **`StockfishPlayer`**: Wraps Stockfish with UCI parameters (`Skill Level`, `UCI_Elo`) for smooth difficulty scaling.
- **Analysis History**: Stores engine evaluation **before each move**, enabling accurate post-game comparison.

### GUI
- **Coordinate System**: Board flips visually when playing as Black; input logic adapts accordingly.
- **Highlighting**: 
  - 🟡 **Yellow**: Move you played
  - 🔵 **Cyan**: Best move recommended by engine (at that time)
- **Responsive UI**: Buttons, dialogs, and panels scale with window.

---

## 🛠️ Extending the App

### Add a New AI Engine
1. Create `src/core/my_engine.py`
2. Implement `get_move(board: chess.Board) -> chess.Move`
3. Update `Player` to use it

### Add Sound Effects
- Use `pygame.mixer.Sound` in `Display` on move/capture/check.

### Export PGN
- Use `chess.pgn.Game.from_board()` in `GameController`.

---

## 📜 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🙌 Acknowledgements

- [Stockfish](https://stockfishchess.org) – World-class chess engine
- [Pygame](https://www.pygame.org) – Graphics and input handling

---

> 🎯 **Perfect for learning chess, reviewing games, or building your own AI!**  
> ✨ **Contributions welcome!**

--- 

**Enjoy your game!** ♟️