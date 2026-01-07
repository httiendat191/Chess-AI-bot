import time
from bot.ml_bot import MLBot
from bot.random_bot import RandomBot
from state.board import Board, Color

def play_match(white_bot, black_bot, max_moves=1000):
    """
    Chạy 1 ván cờ.
    Trả về: 1 (Trắng thắng), -1 (Đen thắng), 0 (Hòa)
    """
    board = Board()
    moves = 0
    
    while moves < max_moves:
        # 1. Kiểm tra kết thúc game trước khi đi
        if not board._has_legal_moves_for(board.turn):
            if board.is_in_check(board.turn):
                # Bị chiếu mà không đi được -> Thua
                return -1 if board.turn == Color.WHITE else 1
            else:
                # Không đi được nhưng không bị chiếu -> Hòa (Stalemate)
                return 0

        # 2. Chọn nước đi
        try:
            if board.turn == Color.WHITE:
                next_state = white_bot.choose_move(board)
            else:
                next_state = black_bot.choose_move(board)
        except Exception as e:
            print(f"Lỗi bot: {e}")
            return 0 # Coi như hòa nếu lỗi

        # 3. Xử lý kết quả trả về
        if next_state is None:
            # Bot đầu hàng hoặc không tìm thấy nước đi (dù check bên trên đã pass)
            if board.is_in_check(board.turn):
                return -1 if board.turn == Color.WHITE else 1
            return 0

        # 4. Cập nhật bàn cờ
        board = next_state.board
        moves += 1

    # Hết lượt đi mà chưa ai thắng -> Hòa (Draw by Move Limit)
    return 0

def run_tournament(num_games=10):
    print(f"{'='*40}")
    print(f"BẮT ĐẦU ĐẤU GIẢI: {num_games} TRẬN")
    print(f"TRẮNG: MLBot | ĐEN: RandomBot")
    print(f"{'='*40}")

    # Load bot (Chỉ load 1 lần để tiết kiệm thời gian)
    white_bot = MLBot()
    black_bot = RandomBot()

    stats = {"ML_Win": 0, "Random_Win": 0, "Draw": 0}

    for i in range(1, num_games + 1):
        print(f"Đang chạy ván {i}/{num_games}...", end=" ", flush=True)
        
        start_time = time.time()
        result = play_match(white_bot, black_bot)
        end_time = time.time()
        
        duration = end_time - start_time
        
        if result == 1:
            print(f"[ML Thắng] ({duration:.2f}s)")
            stats["ML_Win"] += 1
        elif result == -1:
            print(f"[Random Thắng] ({duration:.2f}s)")
            stats["Random_Win"] += 1
        else:
            print(f"[Hòa] ({duration:.2f}s)")
            stats["Draw"] += 1

    print(f"\n{'='*40}")
    print(f"KẾT QUẢ TỔNG HỢP SAU {num_games} VÁN")
    print(f"{'='*40}")
    print(f"--- ML Bot thắng    : {stats['ML_Win']} ({stats['ML_Win']/num_games*100:.1f}%)")
    print(f"--- Random Bot thắng: {stats['Random_Win']} ({stats['Random_Win']/num_games*100:.1f}%)")
    print(f"--- Hòa             : {stats['Draw']} ({stats['Draw']/num_games*100:.1f}%)")
    print(f"{'='*40}")

if __name__ == "__main__":
    run_tournament(num_games=100)