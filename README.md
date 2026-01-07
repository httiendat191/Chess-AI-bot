# Chess AI Solver
An educational chess engine and simple GUI used for experimenting with search-based AI.

This repository contains:
- a board & move generator implementing full chess rules (castling, en-passant, promotion),
- simple AI agents (random, minimax) and an optional ML-based agent,
- a small Tkinter GUI (`main.py`) to run matches between bots.

Quick start
----------
Install dependencies and run the GUI:

```bash
python -m pip install -r requirements.txt
python main.py
```

Then use the UI to select bots (Random / Minimax / ML) for White and Black and Start the match.

Board model (important internals)
--------------------------------
- `state/board.py` — `Board` holds `grid[y][x]` (8×8, top-left is a8, bottom-right is h1), `turn` (Color), `en_passant`, `castling` rights, and helpers like `generate_next_states()`.
- `state/piece.py` — `Piece` objects with `type` and `color`.
- Moves are produced as `NextState(board, move)` objects (or plain `Board` in some bot interfaces).

Available bots
--------------
- `bot/random_bot.py`: picks a legal move at random.
- `bot/minimax_bot.py`: minimax search with fixed depth (used by the UI when `Minimax` is selected).
- `bot/ml_bot.py`: loads a PyTorch model (`machine_learning/chess_model.pth`) and evaluates positions. If no model is present the bot will log a warning.

Files of interest
-----------------
- `main.py` — Tkinter GUI and bot-selection controls.
- `gui.py` — alternate GUI implementation (if present).
- `state/` — core engine: `board.py`, `move.py`, `piece.py`.
- `bot/` — bots and AI agents.
- `machine_learning/` — model, training and utilities (requires `torch` and `numpy`).
- `requirements.txt` — runtime dependencies (`torch`, `numpy`).

Notes and tips
-------------
- The ML bot expects `machine_learning/chess_model.pth`. If you are on a CPU-only machine and the model was saved with CUDA tensors, the loader will attempt to map to CPU.
- Running heavy bots (Minimax with larger depths or ML evaluation) may block the GUI; consider increasing the UI delay or running evaluation off the main thread.
- If `torch` installation fails via pip on Windows, follow the instructions at https://pytorch.org/get-started/locally/ to install the correct wheel for your Python and CUDA setup.

License / Usage
---------------
Educational code — modify and experiment freely for learning purposes.
