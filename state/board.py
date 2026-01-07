from copy import deepcopy
from dataclasses import dataclass

from .piece import Piece, PieceType, Color
from .move import Move

@dataclass
class NextState:
    board: "Board"
    move: Move
    
class Board:
    def __init__(self):
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        self.turn = Color.WHITE
        self.en_passant = None
        self.castling = {
            Color.WHITE: {"K": True, "Q": True},
            Color.BLACK: {"K": True, "Q": True},
        }
        self._init()

    def _init(self):
        for x in range(8):
            self.grid[1][x] = Piece(PieceType.PAWN, Color.BLACK)
            self.grid[6][x] = Piece(PieceType.PAWN, Color.WHITE)

        self.grid[0][0] = self.grid[0][7] = Piece(PieceType.ROOK, Color.BLACK)
        self.grid[7][0] = self.grid[7][7] = Piece(PieceType.ROOK, Color.WHITE)

        self.grid[0][1] = self.grid[0][6] = Piece(PieceType.KNIGHT, Color.BLACK)
        self.grid[7][1] = self.grid[7][6] = Piece(PieceType.KNIGHT, Color.WHITE)

        self.grid[0][2] = self.grid[0][5] = Piece(PieceType.BISHOP, Color.BLACK)
        self.grid[7][2] = self.grid[7][5] = Piece(PieceType.BISHOP, Color.WHITE)

        self.grid[0][3] = Piece(PieceType.QUEEN, Color.BLACK)
        self.grid[7][3] = Piece(PieceType.QUEEN, Color.WHITE)

        self.grid[0][4] = Piece(PieceType.KING, Color.BLACK)
        self.grid[7][4] = Piece(PieceType.KING, Color.WHITE)

    def copy(self):
        return deepcopy(self)

    def inside(self, x, y):
        return 0 <= x < 8 and 0 <= y < 8

    def get(self, pos):
        x, y = pos
        return self.grid[y][x]

    def printBoard(self):
        mapping = {
            PieceType.KING:   "K",
            PieceType.QUEEN:  "Q",
            PieceType.ROOK:   "R",
            PieceType.BISHOP: "B",
            PieceType.KNIGHT: "N",
            PieceType.PAWN:   "P",
        }

        print("\n   +------------------------+")
        for y in range(8):
            print(f" {8-y} |", end=" ")
            for x in range(8):
                p = self.grid[y][x]
                if p is None:
                    print(".", end="  ")
                else:
                    ch = mapping[p.type]
                    if p.color == Color.BLACK:
                        ch = ch.lower()
                    print(ch, end="  ")
            print("|")
        print("   +------------------------+")
        print("     a  b  c  d  e  f  g  h\n")
    
    # ---------- CHECK DETECTION ----------
    def is_in_check(self, color):
        king_pos = None
        for y in range(8):
            for x in range(8):
                p = self.grid[y][x]
                if p and p.type == PieceType.KING and p.color == color:
                    king_pos = (x, y)
                    break

        enemy = color.opposite()
        return self.square_attacked(king_pos, enemy)

    def square_attacked(self, pos, by_color):
        x, y = pos

        # Pawn
        dirp = 1 if by_color == Color.WHITE else -1
        for dx in (-1, 1):
            px, py = x + dx, y + dirp
            if self.inside(px, py):
                p = self.get((px, py))
                if p and p.color == by_color and p.type == PieceType.PAWN:
                    return True

        # Knight
        for dx, dy in [(1,2),(2,1),(-1,2),(-2,1),(1,-2),(2,-1),(-1,-2),(-2,-1)]:
            nx, ny = x + dx, y + dy
            if self.inside(nx, ny):
                p = self.get((nx, ny))
                if p and p.color == by_color and p.type == PieceType.KNIGHT:
                    return True

        # Sliding
        sliders = {
            PieceType.BISHOP: [(1,1),(-1,1),(1,-1),(-1,-1)],
            PieceType.ROOK: [(1,0),(-1,0),(0,1),(0,-1)],
            PieceType.QUEEN: [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)],
        }

        for t, dirs in sliders.items():
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                while self.inside(nx, ny):
                    p = self.get((nx, ny))
                    if p:
                        if p.color == by_color and p.type == t:
                            return True
                        break
                    nx += dx
                    ny += dy

        # King
        for dx, dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)]:
            nx, ny = x + dx, y + dy
            if self.inside(nx, ny):
                p = self.get((nx, ny))
                if p and p.color == by_color and p.type == PieceType.KING:
                    return True

        return False

    def generate_next_states(self):
        out = []
        for y in range(8):
            for x in range(8):
                p = self.grid[y][x]
                if p and p.color == self.turn:
                    out.extend(self.generate_piece_next_states((x, y), p))
        return out

    # ---------- MOVE AVAILABILITY / GAME END ----------
    def _has_legal_moves_for(self, color: Color) -> bool:
        """Return True if `color` has at least one legal move from current position."""
        cur_turn = self.turn
        try:
            self.turn = color
            nexts = self.generate_next_states()
            return len(nexts) > 0
        finally:
            self.turn = cur_turn

    def is_checkmate(self, color: Color) -> bool:
        """True if `color` is checkmated (in check and no legal moves)."""
        if not self.is_in_check(color):
            return False
        return not self._has_legal_moves_for(color)

    def is_stalemate(self, color: Color) -> bool:
        """True if `color` has no legal moves but is not in check (stalemate)."""
        if self.is_in_check(color):
            return False
        return not self._has_legal_moves_for(color)

    def generate_piece_next_states(self, pos, piece):
        if piece.type == PieceType.PAWN:
            return self.generate_pawn(pos, piece)
        if piece.type == PieceType.KNIGHT:
            return self.generate_knight(pos, piece)
        if piece.type == PieceType.BISHOP:
            return self.generate_sliding(pos, piece, [(1,1), (-1,1), (1,-1), (-1,-1)])
        if piece.type == PieceType.ROOK:
            return self.generate_sliding(pos, piece, [(1,0),(-1,0),(0,1),(0,-1)])
        if piece.type == PieceType.QUEEN:
            return self.generate_sliding(pos, piece, [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)])
        if piece.type == PieceType.KING:
            return self.generate_king(pos, piece)
        return []

    # ---------- SLIDING (rook/bishop/queen) ----------
    def generate_sliding(self, pos, piece, dirs):
        out = []
        x, y = pos
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            while self.inside(nx, ny):
                t = self.get((nx, ny))
                if t is None or t.color != piece.color:
                    newb = self.copy()
                    newb.grid[y][x] = None
                    newb.grid[ny][nx] = piece.copy()
                    # Update castling rights
                    if piece.type == PieceType.ROOK:
                        if piece.color == Color.WHITE:
                            if (x, y) == (7, 7):
                                newb.castling[Color.WHITE]['K'] = False
                            if (x, y) == (0, 7):
                                newb.castling[Color.WHITE]['Q'] = False
                        else:
                            if (x, y) == (7, 0):
                                newb.castling[Color.BLACK]['K'] = False
                            if (x, y) == (0, 0):
                                newb.castling[Color.BLACK]['Q'] = False
                    # Update rook capture castling rights
                    if t and t.type == PieceType.ROOK:
                        if t.color == Color.WHITE:
                            if (nx, ny) == (7, 7):
                                newb.castling[Color.WHITE]['K'] = False
                            if (nx, ny) == (0, 7):
                                newb.castling[Color.WHITE]['Q'] = False
                        else:
                            if (nx, ny) == (7, 0):
                                newb.castling[Color.BLACK]['K'] = False
                            if (nx, ny) == (0, 0):
                                newb.castling[Color.BLACK]['Q'] = False
                    newb.turn = self.turn.opposite()
                    newb.en_passant = None
                    if not newb.is_in_check(piece.color):
                        out.append(NextState(board=newb, move=Move(frm=(x, y), to=(nx, ny), piece=piece)))
                    if t:
                        break
                else:
                    break
                nx += dx
                ny += dy
        return out

    # ---------- KNIGHT ----------
    def generate_knight(self, pos, piece):
        out = []
        x, y = pos
        moves = [(1,2),(2,1),(-1,2),(-2,1),(1,-2),(2,-1),(-1,-2),(-2,-1)]
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if self.inside(nx, ny):
                t = self.get((nx, ny))
                if t is None or t.color != piece.color:
                    newb = self.copy()
                    newb.grid[y][x] = None
                    newb.grid[ny][nx] = piece.copy()
                    newb.turn = self.turn.opposite()
                    newb.en_passant = None
                    if not newb.is_in_check(piece.color):
                        out.append(NextState(board=newb, move=Move(frm=(x, y), to=(nx, ny), piece=piece)))
        return out

    # ---------- PAWN ----------
    def generate_pawn(self, pos, piece):
        out = []
        x, y = pos
        dirp = -1 if piece.color == Color.WHITE else 1
        start_row = 6 if piece.color == Color.WHITE else 1

        # forward 1
        if self.inside(x, y+dirp) and self.get((x, y+dirp)) is None:
            out.extend(self._pawn_move(pos, (x, y+dirp), piece))

        # forward 2
        if y == start_row and self.get((x, y+dirp)) is None and self.get((x, y+2*dirp)) is None:
            out.extend(self._pawn_move(pos, (x, y+2*dirp), piece, double=True))
        # capture
        for dx in (-1, 1):
            nx, ny = x + dx, y + dirp
            if self.inside(nx, ny):
                t = self.get((nx, ny))
                if t and t.color != piece.color:
                    out.extend(self._pawn_move(pos, (nx, ny), piece))

        # en passant
        if self.en_passant:
            ex, ey = self.en_passant
            if ey == y + dirp and abs(ex - x) == 1:
                out.extend(self._pawn_move(pos, (ex, ey), piece, enpass=True))

        return out

    def _pawn_move(self, frm, to, piece, double=False, enpass=False):
        fx, fy = frm
        tx, ty = to
        if (piece.color == Color.WHITE and ty == 0) or (piece.color == Color.BLACK and ty == 7):
            out = []
            for t in [PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT]:
                newb = self.copy()
                newb.grid[fy][fx] = None
                newb.grid[ty][tx] = Piece(t, piece.color)
                newb.turn = self.turn.opposite()
                newb.en_passant = None
                if not newb.is_in_check(piece.color):
                    out.append(NextState(board=newb, move=Move(frm=frm, to=to, piece=piece, promotion=t)))
            return out
                       
        newb = self.copy()
        newb.grid[fy][fx] = None

        if enpass:
            direction = -1 if piece.color == Color.WHITE else 1
            newb.grid[ty - direction][tx] = None

        newb.grid[ty][tx] = piece.copy()

        if double:
            mid = (fy + ty)//2
            newb.en_passant = (fx, mid)
        else:
            newb.en_passant = None

        newb.turn = self.turn.opposite()
        if newb.is_in_check(piece.color):
            return []
        return [NextState(board=newb, move=Move(frm=frm, to=to, piece=piece, en_passant=enpass))]

    # ---------- KING ----------
    def generate_king(self, pos, piece):
        out = []
        x, y = pos
        dirs = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)]

        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if self.inside(nx, ny):
                t = self.get((nx, ny))
                if t is None or t.color != piece.color:
                    newb = self.copy()
                    newb.grid[y][x] = None
                    newb.grid[ny][nx] = piece.copy()
                    newb.castling[piece.color]["K"] = False
                    newb.castling[piece.color]["Q"] = False
                    newb.turn = self.turn.opposite()
                    newb.en_passant = None
                    if not newb.is_in_check(piece.color):
                        out.append(NextState(board=newb, move=Move(frm=(x, y), to=(nx, ny), piece=piece)))

        # castling
        out.extend(self._castle(pos, piece))

        return out

    def _castle(self, pos, king):
        x, y = pos
        out = []
        rights = self.castling[king.color]
        enemy = king.color.opposite()

        
        if rights["K"]:
            if self.grid[y][5] is None and self.grid[y][6] is None and self.grid[y][7] is not None:
                if not self.square_attacked((4,y), enemy) and not self.square_attacked((5,y), enemy) and not self.square_attacked((6,y), enemy):
                    newb = self.copy()
                    newb.grid[y][4] = None
                    newb.grid[y][6] = king.copy()
                    
                    rook = newb.grid[y][7]
                    if rook is not None: 
                        newb.grid[y][7] = None
                        newb.grid[y][5] = rook.copy()
                        newb.turn = enemy
                        newb.castling[king.color]["K"] = False
                        newb.castling[king.color]["Q"] = False
                        newb.en_passant = None
                        out.append(NextState(board=newb, move=Move(frm=(x, y), to=(6, y), piece=king, castling=True)))

        if rights["Q"]:
            if self.grid[y][1] is None and self.grid[y][2] is None and self.grid[y][3] is None and self.grid[y][0] is not None:
                if not self.square_attacked((4,y), enemy) and not self.square_attacked((3,y), enemy) and not self.square_attacked((2,y), enemy):
                    newb = self.copy()
                    newb.grid[y][4] = None
                    newb.grid[y][2] = king.copy()
                    
                    rook = newb.grid[y][0]
                    if rook is not None:
                        newb.grid[y][0] = None
                        newb.grid[y][3] = rook.copy()
                        newb.turn = enemy
                        newb.castling[king.color]["K"] = False
                        newb.castling[king.color]["Q"] = False
                        newb.en_passant = None
                        out.append(NextState(board=newb, move=Move(frm=(x, y), to=(2, y), piece=king, castling=True)))

        return out
