import torch
import os
from bot.bot import Bot
from state.board import Board, NextState
from state.piece import Color
from machine_learning.model import ChessNet
from machine_learning.utils import board_to_tensor

class MLBot(Bot):
    def __init__(self, model_path=None):
        self.model = ChessNet()
        
    
        if model_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_path = os.path.join(base_dir, "machine_learning", "chess_model.pth")
            
        try:
            # If CUDA is available, load normally; otherwise map tensors to CPU
            if torch.cuda.is_available():
                self.model.load_state_dict(torch.load(model_path))
            else:
                self.model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
            print("MLBot: Loaded model successfully.")
        except FileNotFoundError:
            print(f"MLBot Error: Could not find model at {model_path}. Please run machine_learning/train.py first.")
        except RuntimeError as e:
            # Common case: model was saved with CUDA tensors but running on CPU-only machine
            try:
                self.model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
                print("MLBot: Loaded model with map_location=cpu after RuntimeError.")
            except Exception:
                print(f"MLBot Error loading model: {e}")
        
        self.model.eval() # Chế độ inference

    def choose_move(self, board: Board) -> NextState:
        next_states = board.generate_next_states()
        
        if not next_states:
            return None
        
        for state in next_states:
            # Nếu đi nước này mà đối phương bị chiếu hết -> Chọn luôn!
            if state.board.is_checkmate(state.board.turn):
                return state
        best_state = None
        
        # Nếu Bot cầm quân Trắng, tìm điểm cao nhất (Max)
        # Nếu Bot cầm quân Đen, tìm điểm thấp nhất (Min) - vì score dương có lợi cho Trắng
        is_white = (board.turn == Color.WHITE)
        best_score = -float('inf') if is_white else float('inf')
        
        # Duyệt qua tất cả các nước đi có thể (Batch processing would be faster, but loop is simpler)
        for state in next_states:
            # state là object NextState, ta cần đánh giá bàn cờ sau khi đi (state.board)
            tensor_input = board_to_tensor(state.board).unsqueeze(0) # Thêm batch dimension (1, 12, 8, 8)
            
            with torch.no_grad():
                score = self.model(tensor_input).item()
            
            if is_white:
                if score > best_score:
                    best_score = score
                    best_state = state
            else:
                if score < best_score:
                    best_score = score
                    best_state = state
                    
        # Fallback nếu lỗi (hiếm gặp)
        if best_state is None:
            import random
            return random.choice(next_states)
            
        return best_state