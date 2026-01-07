from typing import Optional
from .piece import Piece, PieceType

class Move:
    def __init__(
        self,
        frm: tuple[int, int],
        to: tuple[int, int],
        piece: Piece,
        promotion: Optional[PieceType] = None,
        en_passant: bool = False,
        castling: bool = False,
    ) -> None:
        self.frm: tuple[int, int] = frm
        self.to: tuple[int, int] = to
        self.piece: Piece = piece
        self.promotion: Optional[PieceType] = promotion
        self.en_passant: bool = en_passant
        self.castling: bool = castling

    def __repr__(self) -> str:
        s = f"{self.piece}{self.frm}->{self.to}"
        if self.promotion:
            s += f"={self.promotion.name}"
        if self.castling:
            s += " (castle)"
        if self.en_passant:
            s += " (ep)"
        return s
