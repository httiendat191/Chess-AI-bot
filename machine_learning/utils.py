import torch
import numpy as np
from state.board import Board
from state.piece import PieceType, Color

# Mapping loại quân sang index (0-5)
PIECE_TYPE_MAP = {
    PieceType.PAWN: 0,
    PieceType.KNIGHT: 1,
    PieceType.BISHOP: 2,
    PieceType.ROOK: 3,
    PieceType.QUEEN: 4,
    PieceType.KING: 5
}

# Điểm số cơ bản 
PIECE_VALUES = {
    PieceType.PAWN: 1,
    PieceType.KNIGHT: 3,
    PieceType.BISHOP: 3,
    PieceType.ROOK: 5,
    PieceType.QUEEN: 9,
    PieceType.KING: 0
}

def board_to_tensor(board: Board):
    """
    Chuyển object Board custom thành Tensor 12x8x8.
    Channel 0-5: Quân Trắng (P, N, B, R, Q, K)
    Channel 6-11: Quân Đen (P, N, B, R, Q, K)
    """
    # 12 channels, 8 rows, 8 cols
    matrix = np.zeros((12, 8, 8), dtype=np.float32)
    
    for y in range(8):
        for x in range(8):
            p = board.grid[y][x]
            if p is not None:
                piece_idx = PIECE_TYPE_MAP[p.type]
                
                # Nếu là màu Đen thì cộng thêm 6 vào index channel
                if p.color == Color.BLACK:
                    piece_idx += 6
                
                matrix[piece_idx, y, x] = 1.0
                
    return torch.tensor(matrix)

def get_material_score(board: Board):
    """
    Tính tổng điểm bàn cờ dựa trên quân số.
    Score > 0: Trắng ưu thế. Score < 0: Đen ưu thế.
    """
    score = 0
    for y in range(8):
        for x in range(8):
            p = board.grid[y][x]
            if p is not None:
                val = PIECE_VALUES[p.type]
                if p.color == Color.WHITE:
                    score += val
                else:
                    score -= val
    return float(score)