import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from state.board import Board, Color
from machine_learning.model import ChessNet
from machine_learning.utils import board_to_tensor, get_material_score

# --- CẤU HÌNH ---
EPISODES = 250       # Số ván tự chơi (Self-play)
MAX_MOVES = 500      # Giới hạn số nước đi để tránh loop vô tận
EPSILON_START = 0.9  # Tỉ lệ đi ngẫu nhiên ban đầu (khám phá)
EPSILON_END = 0.1    # Tỉ lệ đi ngẫu nhiên lúc sau (tối ưu)
EPSILON_DECAY = 0.995
LEARNING_RATE = 0.001
BATCH_SIZE = 128

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def select_move_epsilon(model, board, epsilon):
    """Chọn nước đi: Epsilon% ngẫu nhiên, (1-Epsilon)% theo Model"""
    next_states = board.generate_next_states()
    if not next_states: return None

    # Khám phá (Exploration): Đi bừa để học cái mới
    if random.random() < epsilon:
        return random.choice(next_states)

    # Khai thác (Exploitation): Đi nước tốt nhất theo Model hiện tại
    best_state = None
    best_score = -float('inf') if board.turn == Color.WHITE else float('inf')
    
    # Batch processing để nhanh hơn
    tensor_list = []
    for st in next_states:
        tensor_list.append(board_to_tensor(st.board).numpy())
    
    batch_tensors = torch.tensor(np.array(tensor_list)).to(device)
    
    with torch.no_grad():
        scores = model(batch_tensors).cpu().numpy().flatten()
        
    if board.turn == Color.WHITE:
        idx = np.argmax(scores)
    else:
        idx = np.argmin(scores)
        
    return next_states[idx]

def train_self_play():
    print(f"--- Bắt đầu Training Self-Play trên {device} ---")
    
    model = ChessNet().to(device)
    
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    criterion = nn.MSELoss()
    
    epsilon = EPSILON_START
    memory = [] # Lưu trữ dữ liệu: (board_tensor, target_value)

    for episode in range(1, EPISODES + 1):
        board = Board()
        game_history = [] # Lưu các trạng thái trong ván này
        
        # --- GIAI ĐOẠN 1: TỰ CHƠI (SELF-PLAY) ---
        winner = 0 # 0: Hòa, 1: Trắng, -1: Đen
        moves_count = 0
        
        while moves_count < MAX_MOVES:
            # Kiểm tra kết thúc game
            if not board._has_legal_moves_for(board.turn):
                if board.is_in_check(board.turn):
                    winner = -1 if board.turn == Color.WHITE else 1
                else:
                    winner = 0 # Hòa stalemate
                break
                
            # Bot chọn nước đi
            next_state = select_move_epsilon(model, board, epsilon)
            if next_state is None: break # Hòa/Lỗi
            
            # Lưu trạng thái vào lịch sử ván đấu
            # Note: Lưu tensor của bàn cờ TRƯỚC khi đi hay SAU khi đi?
            # Với Value Network, ta đánh giá thế cờ HIỆN TẠI.
            game_history.append(board_to_tensor(next_state.board))
            
            board = next_state.board
            moves_count += 1
            
        # Giảm epsilon dần dần
        epsilon = max(EPSILON_END, epsilon * EPSILON_DECAY)

        # --- GIAI ĐOẠN 2: TẠO DỮ LIỆU TRAINING (REWARD ASSIGNMENT) ---
        # Gán nhãn cho toàn bộ nước đi trong ván
        # Nếu Trắng thắng (1): Mọi thế cờ dẫn đến kết quả này đều có xu hướng = 1
        # Nhưng để thông minh hơn, ta cộng thêm điểm Material (heuristic) để dẫn hướng ban đầu
        
        for state_tensor in game_history:
            # Reward shaping: Kết hợp Kết quả ván cờ + Lợi thế vật chất
            # target = (Kết quả thực tế * 0.7) + (Điểm vật chất quy đổi * 0.3)
            # Điều này giúp bot không bị "mù" khi chưa thắng ván nào
            
            # Tính điểm vật chất đơn giản (-1 đến 1)
            # Giả sử max material diff là 20
            # material_val = get_material_score(...) / 20.0 
            # Tuy nhiên để đơn giản, ta dùng Pure Monte Carlo trước:
            
            target = float(winner) 
            
            # Lưu vào bộ nhớ chung
            memory.append((state_tensor, target))

        # --- GIAI ĐOẠN 3: HUẤN LUYỆN (TRAINING) ---
        # Chỉ train khi đủ dữ liệu hoặc hết ván
        if len(memory) > BATCH_SIZE:
            # Lấy ngẫu nhiên batch để học (Experience Replay)
            batch = random.sample(memory, BATCH_SIZE)
            states_b, targets_b = zip(*batch)
            
            states_tensor = torch.stack(states_b).to(device)
            targets_tensor = torch.tensor(targets_b, dtype=torch.float32).unsqueeze(1).to(device)
            
            optimizer.zero_grad()
            outputs = model(states_tensor)
            loss = criterion(outputs, targets_tensor)
            loss.backward()
            optimizer.step()
            
            # Giữ bộ nhớ không quá lớn (quên bớt cái cũ)
            if len(memory) > 5000:
                memory = memory[-5000:]
                
        # Log kết quả
        if episode % 10 == 0:
            result_str = "Hòa"
            if winner == 1: result_str = "Trắng Thắng"
            if winner == -1: result_str = "Đen Thắng"
            print(f"Ep {episode}: {result_str} (Moves: {moves_count}, Eps: {epsilon:.2f}, Loss: {loss.item():.4f})")
            
        # Lưu model định kỳ
        if episode % 50 == 0:
            torch.save(model.state_dict(), "chess_model.pth")

    print("--- Hoàn tất Training RL ---")
    torch.save(model.state_dict(), "chess_model.pth") # Ghi đè model chính

if __name__ == "__main__":
    train_self_play()