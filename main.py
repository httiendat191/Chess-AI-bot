import tkinter as tk
from tkinter import ttk, messagebox
from bot.random_bot import RandomBot
from bot.minimax_bot import Minimaxbot
from state.board import Board, PieceType, Color
from bot.ml_bot import MLBot  # <--- Import Bot ML mới


SQUARE_SIZE = 64
BOARD_COLOR_LIGHT = "#F0D9B5"
BOARD_COLOR_DARK = "#B58863"
PIECE_COLOR_WHITE = "#000000"
PIECE_COLOR_BLACK = "#000000"

# Unicode chess glyphs. White pieces: U+2654..2659, Black pieces: U+265A..265F
UNICODE_PIECES = {
   PieceType.KING: '\u265A',
    PieceType.QUEEN: '\u265B',
    PieceType.ROOK: '\u265C',
    PieceType.BISHOP: '\u265D',
    PieceType.KNIGHT: '\u265E',
    PieceType.PAWN: '\u265F',
}

class ChessGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess AI")

        self.canvas = tk.Canvas(root, width=8*SQUARE_SIZE, height=8*SQUARE_SIZE)
        self.canvas.grid(row=0, column=0, rowspan=6)

        # Controls
        self.start_btn = ttk.Button(root, text="Start", command=self.start)
        self.start_btn.grid(row=0, column=1, sticky='ew')

        self.pause_btn = ttk.Button(root, text="Pause", command=self.pause)
        self.pause_btn.grid(row=1, column=1, sticky='ew')

        self.step_btn = ttk.Button(root, text="Step", command=self.step)
        self.step_btn.grid(row=2, column=1, sticky='ew')

        self.reset_btn = ttk.Button(root, text="Reset", command=self.reset)
        self.reset_btn.grid(row=3, column=1, sticky='ew')

        ttk.Label(root, text="Delay ms").grid(row=4, column=1)
        self.delay_var = tk.IntVar(value=500)
        self.delay_scale = ttk.Scale(root, from_=50, to=2000, orient='horizontal', variable=self.delay_var)
        self.delay_scale.grid(row=5, column=1, sticky='ew')

        self.status = tk.StringVar()
        self.status = tk.StringVar()

        # Bot selection controls (white/black) and Minimax depth
        ttk.Label(root, text="White Bot").grid(row=6, column=1)
        initial_white = 'Random'
        self.white_bot_var = tk.StringVar(value=initial_white)
        self.white_bot_cb = ttk.Combobox(root, values=['Random', 'Minimax', 'ML'], textvariable=self.white_bot_var, state='readonly')
        self.white_bot_cb.grid(row=7, column=1, sticky='ew')

        ttk.Label(root, text="Black Bot").grid(row=8, column=1)
        initial_black = 'Random'
        self.black_bot_var = tk.StringVar(value=initial_black)
        self.black_bot_cb = ttk.Combobox(root, values=['Random', 'Minimax', 'ML'], textvariable=self.black_bot_var, state='readonly')
        self.black_bot_cb.grid(row=9, column=1, sticky='ew')

        # Minimax depth selector removed — using fixed depth in _make_bot

        self.status_label = ttk.Label(root, textvariable=self.status)
        self.status_label.grid(row=12, column=0, columnspan=2, sticky='ew')

        # Game stateM
        self.board = Board()
        self.white_bot = RandomBot()
        self.black_bot = RandomBot()
        self.running = False
        self.move_count = 0

        self.draw_board()
        self.update_status()

    def draw_board(self):
        self.canvas.delete('all')
        for y in range(8):
            for x in range(8):
                x1 = x * SQUARE_SIZE
                y1 = y * SQUARE_SIZE
                x2 = x1 + SQUARE_SIZE
                y2 = y1 + SQUARE_SIZE
                color = BOARD_COLOR_LIGHT if (x + y) % 2 == 0 else BOARD_COLOR_DARK
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=color)

                p = self.board.grid[y][x]
                if p is not None:
                    # choose unicode glyph based on color
                    if p.color == Color.WHITE:
                        glyph = UNICODE_PIECES.get(p.type, '?')
                        self.canvas.create_text(x1 + SQUARE_SIZE/2, y1 + SQUARE_SIZE/2,
                                                text=glyph, font=("Segoe UI Symbol", 44), fill='white')
                    else:
                        glyph = UNICODE_PIECES.get(p.type, '?')
                        self.canvas.create_text(x1 + SQUARE_SIZE/2, y1 + SQUARE_SIZE/2,
                                                text=glyph, font=("Segoe UI Symbol", 44), fill='black')

        # Draw coordinates
        for x in range(8):
            self.canvas.create_text(x * SQUARE_SIZE + 10, 8 * SQUARE_SIZE - 10, text=chr(ord('a') + x), anchor='w')
        for y in range(8):
            self.canvas.create_text(5, y * SQUARE_SIZE + 10, text=str(8 - y), anchor='w')

    def start(self):
        if not self.running:
            # instantiate bots according to selection
            self.white_bot = self._make_bot(self.white_bot_var.get())
            self.black_bot = self._make_bot(self.black_bot_var.get())
            self.running = True
            self._loop()

    def pause(self):
        self.running = False

    def step(self):
        # perform a single bot move (if available)
        self._play_one()

    def reset(self):
        self.running = False
        self.board = Board()
        self.move_count = 0
        # re-create bots according to selection
        self.white_bot = self._make_bot(self.white_bot_var.get())
        self.black_bot = self._make_bot(self.black_bot_var.get())
        self.draw_board()
        self.update_status()

    def _make_bot(self, choice):
        # use a fixed default depth for Minimax
        c = (choice or '').strip().lower()
        if c == 'minimax':
            return Minimaxbot(depth=3)
        if c in ('ml', 'mlbot'):
            return MLBot()
        return RandomBot()

    def _loop(self):
        if not self.running:
            return
        self._play_one()
        delay = max(1, self.delay_var.get())
        self.root.after(delay, self._loop)

    def _play_one(self):
        # Determine whose turn and get move from corresponding bot
        try:
            if self.board.turn == Color.WHITE:
                nxt = self.white_bot.choose_move(self.board)
            else:
                nxt = self.black_bot.choose_move(self.board)
        except Exception as e:
            # no moves or error
            self.running = False
            self.status.set(f"Game over or error: {e}")
            return

        if nxt is None:
            self.running = False
            self.status.set("No legal moves: game over")
            return

        # nxt can be either a Board or a NextState(board, move)
        try:
            if hasattr(nxt, 'board'):
                # NextState object
                self.board = nxt.board
                move_obj = getattr(nxt, 'move', None)
            else:
                # direct Board
                self.board = nxt
                move_obj = None
        except Exception as e:
            self.running = False
            self.status.set(f"Error applying move: {e}")
            return

        self.move_count += 1
        self.draw_board()
        # include last move in status if available
        if move_obj is not None:
            self.status.set(f"Move: {self.move_count} | Turn: {self.board.turn.name} | Last: {move_obj}")
        else:
            self.update_status()

        # check for game end: checkmate or stalemate (draw)
        # After applying a move, if the side to move has no legal moves,
        # it's either checkmate (if in check) or stalemate.
        to_move = self.board.turn
        if self.board.is_checkmate(to_move):
            winner = to_move.opposite().name
            self.running = False
            msg = f"Checkmate! Winner: {winner}"
            self.status.set(msg)
            try:
                self.root.lift()
                self.root.attributes('-topmost', True)
                messagebox.showinfo("Game Over", msg, parent=self.root)
                self.root.attributes('-topmost', False)
            except Exception as e:
                print("Failed to show messagebox:", e)
            return
        if self.board.is_stalemate(to_move):
            self.running = False
            msg = "Stalemate (draw)"
            self.status.set(msg)
            try:
                self.root.lift()
                self.root.attributes('-topmost', True)
                messagebox.showinfo("Game Over", msg, parent=self.root)
                self.root.attributes('-topmost', False)
            except Exception as e:
                print("Failed to show messagebox:", e)
            return

    def update_status(self):
        self.status.set(f"Move: {self.move_count} | Turn: {self.board.turn.name}")


# if __name__ == '__main__':
#     root = tk.Tk()
#     white_bot = RandomBot()
#     black_bot = RandomBot()
#     gui = ChessGUI(root, white_bot=white_bot, black_bot=black_bot)
#     root.mainloop()

if __name__ == '__main__':
    root = tk.Tk()
    gui = ChessGUI(root)
    root.mainloop()