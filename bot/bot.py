from abc import ABC, abstractmethod
from state.board import Board, NextState

class Bot(ABC):
    @abstractmethod
    def choose_move(self, board: "Board") -> NextState:
        pass