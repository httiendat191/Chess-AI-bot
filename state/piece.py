from enum import Enum

class Color(Enum):
    WHITE = "WHITE"
    BLACK = "BLACK"
    
    def opposite(self):
        return Color.BLACK if self == Color.WHITE else Color.WHITE

class PieceType(Enum):
    PAWN   = "PAWN"
    ROOK   = "ROOK"
    KNIGHT = "KNIGHT"
    BISHOP = "BISHOP"
    QUEEN  = "QUEEN"
    KING   = "KING"

class Piece:
    def __init__(self, piece_type: PieceType, color: Color):
        self.type = piece_type
        self.color = color

    def __repr__(self):
        return f"{self.color.name}_{self.type.name}"

    def copy(self):
        """Return a shallow copy of this Piece (same type and color)."""
        return Piece(self.type, self.color)
      