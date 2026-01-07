import math
from bot.bot import Bot
from state.board import Board, NextState
from state.piece import PieceType, Color

#-- BANG DIEM UU TIEN

PIECE_VALUES = {            #Tot 1, Ma 3, Tuong 3, Xe 5, Hau 9
    PieceType.PAWN: 100, # Quan Tot
    PieceType.KNIGHT: 300, #Quan Ma
    PieceType.BISHOP: 350, #Quan Tuong (uu tien hon Ma)
    PieceType.ROOK: 500,    #Quan Xe
    PieceType.QUEEN: 900,   #Quan Hau
    PieceType.KING: 20000   #Quan Tuong
}

#-- MA TRAN DIEM O TUNG VI TRI

# Quan Tot - tien len, kiem soat trung tam
PAWN_TABLE = [
    [0,  0,  0,  0,  0,  0,  0,  0],
    [50, 50, 50, 50, 50, 50, 50, 50],
    [10, 10, 20, 30, 30, 20, 10, 10],
    [5,  5, 10, 25, 25, 10,  5,  5],
    [0,  0,  0, 20, 20,  0,  0,  0],
    [5, -5,-10,  0,  0,-10, -5,  5],
    [5, 10, 10,-20,-20, 10, 10,  5],
    [0,  0,  0,  0,  0,  0,  0,  0]
]

# Quan Ma - tranh o bien
KNIGHT_TABLE = [
    [-50,-40,-30,-30,-30,-30,-40,-50],
    [-40,-20,  0,  0,  0,  0,-20,-40],
    [-30,  0, 10, 15, 15, 10,  0,-30],
    [-30,  5, 15, 20, 20, 15,  5,-30],
    [-30,  0, 15, 20, 20, 15,  0,-30],
    [-30,  5, 10, 15, 15, 10,  5,-30],
    [-40,-20,  0,  5,  5,  0,-20,-40],
    [-50,-40,-30,-30,-30,-30,-40,-50]
]

# Quan Tuong tranh bien, di o trung tam
BISHOP_TABLE = [
    [-20,-10,-10,-10,-10,-10,-10,-20],
    [-10,  0,  0,  0,  0,  0,  0,-10],
    [-10,  0,  5, 10, 10,  5,  0,-10],
    [-10,  5,  5, 10, 10,  5,  5,-10],
    [-10,  0, 10, 10, 10, 10,  0,-10],
    [-10, 10, 10, 10, 10, 10, 10,-10],
    [-10,  5,  0,  0,  0,  0,  5,-10],
    [-20,-10,-10,-10,-10,-10,-10,-20]
]

# Xe: thich hang ngang, o hàng 7
ROOK_TABLE = [
    [0,  0,  0,  0,  0,  0,  0,  0],
    [5, 10, 10, 10, 10, 10, 10,  5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [0,  0,  0,  5,  5,  0,  0,  0]
]

# Quan Hau - Tranh o bien
QUEEN_TABLE = [
    [-20,-10,-10, -5, -5,-10,-10,-20],
    [-10,  0,  0,  0,  0,  0,  0,-10],
    [-10,  0,  5,  5,  5,  5,  0,-10],
    [-5,   0,  5,  5,  5,  5,  0, -5],
    [0,    0,  5,  5,  5,  5,  0, -5],
    [-10,  5,  5,  5,  5,  5,  0,-10],
    [-10,  0,  5,  0,  0,  0,  0,-10],
    [-20,-10,-10, -5, -5,-10,-10,-20]
]

# Quan Vua - han che di chuyen xa
KING_MID_TABLE = [
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-20,-30,-30,-40,-40,-30,-30,-20],
    [-10,-20,-20,-20,-20,-20,-20,-10],
    [20, 20,  0,  0,  0,  0, 20, 20],
    [20, 30, 10,  0,  0, 10, 30, 20]
]

class Minimaxbot(Bot):
    def __init__(self, depth=3): #Depth = 3, theo lượt mình - đối thủ - mình
        self.depth = depth      
        self.node_count = 0     #Dem so Node da duyet

    def choose_move(self, board: Board) -> NextState:
        self.node_count = 0
        print(f"Thinking with depth {self.depth}...")
        
        Is_White_Turn = (board.turn == Color.WHITE)
        
        best_state = None
    
        next_states = board.generate_next_states()
        
        if not next_states:
            return None             # Het duong di 

        # Cat tia Alpha (Muc diem thap nhat chiu duoc) va Beta (Muc diem cao nhat ma doi thu cho phep minh lay)
        alpha = -math.inf
        beta = math.inf
        
        best_value = -math.inf
        
        for state in next_states:
            value = self.minimax(state.board, self.depth - 1, alpha, beta, False, Is_White_Turn)
            
            if value > best_value:
                best_value = value
                best_state = state
            
            alpha = max(alpha, best_value)
        
        print(f"Selected move score: {best_value}, Nodes visited: {self.node_count}")
        return best_state

    def minimax(self, board, depth, alpha, beta, maximizing_player, bot_is_white):
        self.node_count += 1
        
        # Dung khi het do sau depth = 3 hoac thua game
        if depth == 0:
            return self.evaluate_board(board, bot_is_white) #Danh gia diem
        
        # Kiem tra GameOver
        current_turn = board.turn #Nguoi di luot ke tiep
        if board.is_checkmate(current_turn):          
            # Neu dang la luot cua minh bi chieu bi -> Minh thua -> Diem thap
            # Neu luot doi thu bi chieu bi -> Minh thang -> Diem cuc cao
            return -100000 if maximizing_player else 100000
        if board.is_stalemate(current_turn):
            return 0    # Ket qua Hoa

        next_states = board.generate_next_states()

        if maximizing_player:
            max_eval = -math.inf
            for state in next_states:
                eval = self.minimax(state.board, depth - 1, alpha, beta, False, bot_is_white)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break       # Cat tia Beta
            return max_eval
        else:
            min_eval = math.inf
            for state in next_states:
                eval = self.minimax(state.board, depth - 1, alpha, beta, True, bot_is_white)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break       # Cat tia Alpha
            return min_eval

    def evaluate_board(self, board, bot_is_white):
        
        # Diem so cua Bot: > 0 dang THANG, <0 dang THUA
        
        white_score = 0
        black_score = 0
        
        for y in range(8):
            for x in range(8):
                piece = board.grid[y][x]
                if not piece:
                    continue
                
                # Xet diem uu tien
                material = PIECE_VALUES.get(piece.type, 0)
                
                # Xet diem vi tri
                pos_score = 0               
                table = None
                if piece.type == PieceType.PAWN: table = PAWN_TABLE
                elif piece.type == PieceType.KNIGHT: table = KNIGHT_TABLE
                elif piece.type == PieceType.BISHOP: table = BISHOP_TABLE
                elif piece.type == PieceType.ROOK: table = ROOK_TABLE
                elif piece.type == PieceType.QUEEN: table = QUEEN_TABLE
                elif piece.type == PieceType.KING: table = KING_MID_TABLE
                
                if table:
                    if piece.color == Color.WHITE:
                        pos_score = table[y][x]
                    else:
                        # Lat Bang neu Bot la mau Den
                        pos_score = table[7-y][x] 

                if piece.color == Color.WHITE:
                    white_score += material + pos_score
                else:
                    black_score += material + pos_score
        
        # Tong diem
        eval_score = white_score - black_score

        # Neu Bot la White, tra ve White - Black, con la Black tra ve Black - White
        if bot_is_white:
            return eval_score
        else:
            return -eval_score