import random
from bot.bot import Bot
from state.board import Board, NextState

class RandomBot(Bot):
    def choose_move(self, board: Board) -> NextState:
        next_states = board.generate_next_states()
        return random.choice(next_states)