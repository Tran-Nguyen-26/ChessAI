import copy
from board import board
from game.move import get_all_valid_moves
from pieces import queen
from pieces.pawn import Pawn

# Bảng ghi nhớ vị trí để tránh tính toán lại các vị trí đã đánh giá
transposition_table = {}

# Cache cho các nước đi hợp lệ để tránh tính đi tính lại
valid_moves_cache = {}

# Các giá trị phạt/thưởng cố định để tránh tính toán lặp đi lặp lại
DOUBLED_PAWN_PENALTY = 20
ISOLATED_PAWN_PENALTY = 15
DEVELOPED_PIECE_BONUS = 10
CENTER_CONTROL_BONUS = 10
KING_PROTECTOR_BONUS = 5
PASSED_PAWN_BONUS = 25
MOBILITY_VALUE = 3
BISHOP_PAIR_BONUS = 30
CONNECTED_ROOKS_BONUS = 20
KNIGHT_OUTPOST_BONUS = 20

# Các ô trung tâm để kiểm tra nhanh
CENTER_SQUARES = {(3, 3), (3, 4), (4, 3), (4, 4)}
EXTENDED_CENTER = {(2, 2), (2, 3), (2, 4), (2, 5), 
                  (3, 2), (3, 3), (3, 4), (3, 5),
                  (4, 2), (4, 3), (4, 4), (4, 5),
                  (5, 2), (5, 3), (5, 4), (5, 5)}

# Giá trị các quân cờ
PIECE_VALUES = {
    "Pawn": 100,
    "Knight": 320,
    "Bishop": 330,
    "Rook": 500,
    "Queen": 900, 
    "King": 20000
}

# MVV-LVA Values (Most Valuable Victim - Least Valuable Attacker)
MVV_LVA_TABLE = {
    "Pawn": {"Pawn": 105, "Knight": 104, "Bishop": 103, "Rook": 102, "Queen": 101, "King": 100},
    "Knight": {"Pawn": 205, "Knight": 204, "Bishop": 203, "Rook": 202, "Queen": 201, "King": 200},
    "Bishop": {"Pawn": 305, "Knight": 304, "Bishop": 303, "Rook": 302, "Queen": 301, "King": 300},
    "Rook": {"Pawn": 405, "Knight": 404, "Bishop": 403, "Rook": 402, "Queen": 401, "King": 400},
    "Queen": {"Pawn": 505, "Knight": 504, "Bishop": 503, "Rook": 502, "Queen": 501, "King": 500},
    "King": {"Pawn": 605, "Knight": 604, "Bishop": 603, "Rook": 602, "Queen": 601, "King": 600}
}

# Bảng vị trí các quân cờ
def get_piece_position_tables():
    # Vị trí quân Tốt
    pawn_position = [
        [0,  0,  0,  0,  0,  0,  0,  0],
        [50, 50, 50, 50, 50, 50, 50, 50],
        [10, 10, 20, 30, 30, 20, 10, 10],
        [5,  5, 10, 25, 25, 10,  5,  5],
        [0,  0,  0, 20, 20,  0,  0,  0],
        [5, -5,-10,  0,  0,-10, -5,  5],
        [5, 10, 10,-20,-20, 10, 10,  5],
        [0,  0,  0,  0,  0,  0,  0,  0]
    ]
    # Vị trí quân Mã
    knight_position = [
        [-50,-40,-30,-30,-30,-30,-40,-50],
        [-40,-20,  0,  0,  0,  0,-20,-40],
        [-30,  0, 10, 15, 15, 10,  0,-30],
        [-30,  5, 15, 20, 20, 15,  5,-30],
        [-30,  0, 15, 20, 20, 15,  0,-30],
        [-30,  5, 10, 15, 15, 10,  5,-30],
        [-40,-20,  0,  5,  5,  0,-20,-40],
        [-50,-40,-30,-30,-30,-30,-40,-50]
    ]
    # Vị trí quân Tịnh
    bishop_position = [
        [-20,-10,-10,-10,-10,-10,-10,-20],
        [-10,  0,  0,  0,  0,  0,  0,-10],
        [-10,  0, 10, 10, 10, 10,  0,-10],
        [-10,  5,  5, 10, 10,  5,  5,-10],
        [-10,  0,  5, 10, 10,  5,  0,-10],
        [-10,  5,  5,  5,  5,  5,  5,-10],
        [-10,  0,  5,  0,  0,  5,  0,-10],
        [-20,-10,-10,-10,-10,-10,-10,-20]
    ]
    # Vị trí quân Xe
    rook_position = [
        [0,  0,  0,  0,  0,  0,  0,  0],
        [5, 10, 10, 10, 10, 10, 10,  5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [0,  0,  0,  5,  5,  0,  0,  0]
    ]
    # Vị trí quân Hậu
    queen_position = [
        [-20,-10,-10, -5, -5,-10,-10,-20],
        [-10,  0,  0,  0,  0,  0,  0,-10],
        [-10,  0,  5,  5,  5,  5,  0,-10],
        [-5,  0,  5,  5,  5,  5,  0, -5],
        [0,  0,  5,  5,  5,  5,  0, -5],
        [-10,  5,  5,  5,  5,  5,  0,-10],
        [-10,  0,  5,  0,  0,  0,  0,-10],
        [-20,-10,-10, -5, -5,-10,-10,-20]
    ]
    # Vị trí quân Vua giai đoạn giữa game
    king_middlegame = [
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-20,-30,-30,-40,-40,-30,-30,-20],
        [-10,-20,-20,-20,-20,-20,-20,-10],
        [20, 20,  0,  0,  0,  0, 20, 20],
        [20, 30, 10,  0,  0, 10, 30, 20]
    ]
    # Vị trí quân Vua giai đoạn cuối game
    king_endgame = [
        [-50,-40,-30,-20,-20,-30,-40,-50],
        [-30,-20,-10,  0,  0,-10,-20,-30],
        [-30,-10, 20, 30, 30, 20,-10,-30],
        [-30,-10, 30, 40, 40, 30,-10,-30],
        [-30,-10, 30, 40, 40, 30,-10,-30],
        [-30,-10, 20, 30, 30, 20,-10,-30],
        [-30,-30,  0,  0,  0,  0,-30,-30],
        [-50,-30,-30,-30,-30,-30,-30,-50]
    ]
    
    return {
        "Pawn": pawn_position,
        "Knight": knight_position,
        "Bishop": bishop_position,
        "Rook": rook_position,
        "Queen": queen_position,
        "King_middlegame": king_middlegame,
        "King_endgame": king_endgame
    }

# Cache bảng vị trí để tránh khởi tạo lại
POSITION_TABLES = get_piece_position_tables()

def hash_board(board):
    """Tạo hash duy nhất cho bàn cờ sử dụng Zobrist Hashing nếu được cài đặt, 
    hoặc trở lại cách đơn giản hơn"""
    # Có thể thay thế bằng Zobrist Hashing nếu cần tối ưu hơn
    return str(board.board)

def count_pieces(board):
    """Đếm số quân trên bàn cờ và phân loại theo màu"""
    piece_count = 0
    pieces_by_color = {"white": 0, "black": 0}
    piece_types = {"white": {}, "black": {}}
    pawn_columns = {"white": [0] * 8, "black": [0] * 8}
    
    for y in range(8):
        for x in range(8):
            piece = board.get_piece((y, x))
            if piece:
                piece_count += 1
                piece_type = piece.__class__.__name__
                pieces_by_color[piece.color] += 1
                
                # Đếm số lượng từng loại quân
                if piece_type not in piece_types[piece.color]:
                    piece_types[piece.color][piece_type] = 0
                piece_types[piece.color][piece_type] += 1
                
                # Đếm tốt theo cột
                if piece_type == "Pawn":
                    pawn_columns[piece.color][x] += 1
    
    return piece_count, pieces_by_color, piece_types, pawn_columns

def is_passed_pawn(board, pos, color):
    """Kiểm tra xem quân tốt có phải là passed pawn không"""
    y, x = pos
    direction = -1 if color == "white" else 1
    opponent = "black" if color == "white" else "white"
    
    # Kiểm tra các cột kề và cột hiện tại phía trước quân tốt
    for col in range(max(0, x-1), min(8, x+2)):
        for row in range(y + direction, 0 if direction < 0 else 8, direction):
            piece = board.get_piece((row, col))
            if piece and piece.__class__.__name__ == "Pawn" and piece.color == opponent:
                return False
    return True

def evaluate_board(board, color):
    """Đánh giá bàn cờ với nhiều yếu tố hơn"""
    # Đếm quân một lần duy nhất để tối ưu
    piece_count, pieces_by_color, piece_types, pawn_columns = count_pieces(board)
    
    # Xác định giai đoạn game (giữa game hay cuối game)
    is_endgame = piece_count <= 12 or (
        pieces_by_color["white"] + pieces_by_color["black"] <= 16 and 
        ("Queen" not in piece_types["white"] or "Queen" not in piece_types["black"])
    )
    
    # Khởi tạo các điểm số
    material_score = 0
    position_score = 0
    pawn_structure_score = 0
    mobility_score = 0
    development_score = 0
    center_control_score = 0
    king_safety_score = 0
    special_score = 0
    
    # Phân tích bàn cờ và đánh giá
    for y in range(8):
        for x in range(8):
            piece = board.get_piece((y, x))
            if not piece:
                continue
                
            piece_type = piece.__class__.__name__
            value = PIECE_VALUES.get(piece_type, 0)
            
            # Xác định hệ số nhân (quân của ai)
            multiplier = 1 if piece.color == color else -1
            
            # Tính điểm quân
            material_score += value * multiplier
            
            # Tính điểm vị trí
            pos_y = y if piece.color == "white" else 7 - y
            if piece_type == "King":
                table_key = "King_endgame" if is_endgame else "King_middlegame"
                pos_value = POSITION_TABLES[table_key][pos_y][x]
            else:
                pos_value = POSITION_TABLES[piece_type][pos_y][x]
            position_score += pos_value * multiplier
            
            # Đánh giá cấu trúc quân Tốt
            if piece_type == "Pawn":
                # Phạt tốt chồng
                if pawn_columns[piece.color][x] > 1:
                    pawn_structure_score -= DOUBLED_PAWN_PENALTY * multiplier
                
                # Phạt tốt cô lập
                is_isolated = True
                for adj_x in [x-1, x+1]:
                    if 0 <= adj_x < 8 and pawn_columns[piece.color][adj_x] > 0:
                        is_isolated = False
                        break
                
                if is_isolated:
                    pawn_structure_score -= ISOLATED_PAWN_PENALTY * multiplier
                
                # Thưởng cho passed pawn
                if is_passed_pawn(board, (y, x), piece.color):
                    # Càng gần vị trí phong hậu càng được nhiều điểm
                    rank_bonus = (7 - pos_y) if piece.color == "white" else pos_y
                    pawn_structure_score += (PASSED_PAWN_BONUS + rank_bonus * 5) * multiplier
            
            # Đánh giá sự phát triển quân cờ
            if piece_count > 20:  # Giai đoạn đầu và giữa game
                if piece_type in ["Knight", "Bishop"]:
                    if ((piece.color == "white" and y < 7) or 
                        (piece.color == "black" and y > 0)):
                        development_score += DEVELOPED_PIECE_BONUS * multiplier
            
            # Kiểm soát trung tâm
            if (y, x) in CENTER_SQUARES:
                center_control_score += CENTER_CONTROL_BONUS * multiplier
            elif (y, x) in EXTENDED_CENTER:
                center_control_score += (CENTER_CONTROL_BONUS // 2) * multiplier
            
            # An toàn của Vua
            if piece_type == "King":
                protectors = 0
                # Đếm quân bảo vệ xung quanh Vua
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < 8 and 0 <= nx < 8 and (dy != 0 or dx != 0):
                            neighbor = board.get_piece((ny, nx))
                            if neighbor and neighbor.color == piece.color:
                                protectors += 1
                
                # Đánh giá cấu trúc nhập thành
                if not is_endgame:
                    if piece.color == "white" and (y == 7 and (x == 1 or x == 2)):
                        king_safety_score += 30 * multiplier  # Thưởng cho việc nhập thành
                    elif piece.color == "black" and (y == 0 and (x == 1 or x == 2)):
                        king_safety_score += 30 * multiplier
                
                king_safety_score += protectors * KING_PROTECTOR_BONUS * multiplier
    
    # Đánh giá cặp tượng (bishop pair)
    if piece_types.get(color, {}).get("Bishop", 0) >= 2:
        special_score += BISHOP_PAIR_BONUS
    if piece_types.get(opponent_color(color), {}).get("Bishop", 0) >= 2:
        special_score -= BISHOP_PAIR_BONUS
    
    # Tính tính cơ động (mobility)
    white_moves = len(get_cached_valid_moves(board, "white"))
    black_moves = len(get_cached_valid_moves(board, "black"))
    mobility_score = (white_moves - black_moves) * MOBILITY_VALUE if color == "white" else (black_moves - white_moves) * MOBILITY_VALUE
    
    # Tính điểm cuối cùng với trọng số
    weights = {
        "material": 1.0,
        "position": 0.5,
        "pawn_structure": 0.4,
        "mobility": 0.3,
        "development": 0.2 if piece_count > 20 else 0.1,
        "center_control": 0.3,
        "king_safety": 0.5 if not is_endgame else 0.2,
        "special": 0.3
    }
    
    final_score = (
        material_score * weights["material"] +
        position_score * weights["position"] +
        pawn_structure_score * weights["pawn_structure"] +
        mobility_score * weights["mobility"] +
        development_score * weights["development"] +
        center_control_score * weights["center_control"] +
        king_safety_score * weights["king_safety"] +
        special_score * weights["special"]
    )

    return final_score

def get_cached_valid_moves(board, color):
    """Lấy các nước đi hợp lệ từ cache hoặc tính toán mới"""
    board_hash = hash_board(board)
    cache_key = f"{board_hash}_{color}"
    
    if cache_key in valid_moves_cache:
        return valid_moves_cache[cache_key]
    
    moves = get_all_valid_moves(board, color)
    valid_moves_cache[cache_key] = moves
    return moves

def order_moves(moves, board, color):
    """Sắp xếp các nước đi để tối ưu alpha-beta pruning"""
    move_scores = []
    
    # Cache lại các nước đi đã được thử trước đó
    board_hash = hash_board(board)
    if board_hash in transposition_table and transposition_table[board_hash][2] is not None:
        best_previous_move = transposition_table[board_hash][2]
        if best_previous_move in moves:
            # Đưa nước đi tốt nhất trước đó lên đầu danh sách
            moves.remove(best_previous_move)
            ordered_moves = [best_previous_move]
            ordered_moves.extend(moves)
            moves = ordered_moves
    
    for from_pos, to_pos in moves:
        score = 0
        moving_piece = board.get_piece(from_pos)
        captured_piece = board.get_piece(to_pos)
        
        if not moving_piece:
            continue
            
        moving_type = moving_piece.__class__.__name__
        
        # 1. Đánh giá theo MVV-LVA cho các nước ăn quân
        if captured_piece:
            captured_type = captured_piece.__class__.__name__
            score = MVV_LVA_TABLE.get(captured_type, {}).get(moving_type, 0)
            
        # 2. Ưu tiên phong Hậu cao nhất
        if isinstance(moving_piece, Pawn):
            if ((moving_piece.color == "white" and to_pos[0] == 0) or 
                (moving_piece.color == "black" and to_pos[0] == 7)):
                score += 1000  # Điểm rất cao cho việc phong hậu
        
        # 3. Thưởng điểm cho việc kiểm soát trung tâm
        if to_pos in CENTER_SQUARES:
            score += 10
        elif to_pos in EXTENDED_CENTER:
            score += 5
            
        # 4. Killer moves (các nước hay cắt tỉa alpha-beta)
        # Có thể bổ sung killer move heuristic nếu cần
        
        move_scores.append((score, (from_pos, to_pos)))
    
    # Sắp xếp giảm dần theo điểm
    move_scores.sort(reverse=True)
    return [move for _, move in move_scores]

def is_check(board, color):
    """Kiểm tra xem vua có đang bị chiếu không"""
    # Tìm vua
    king_pos = None
    for y in range(8):
        for x in range(8):
            piece = board.get_piece((y, x))
            if piece and piece.__class__.__name__ == "King" and piece.color == color:
                king_pos = (y, x)
                break
        if king_pos:
            break
    
    if not king_pos:
        return False  # Không tìm thấy vua (hiếm khi xảy ra)
    
    # Kiểm tra xem có quân đối phương nào có thể ăn vua không
    opponent = opponent_color(color)
    opponent_moves = get_cached_valid_moves(board, opponent)
    
    for _, to_pos in opponent_moves:
        if to_pos == king_pos:
            return True
    
    return False

def quiescence_search(board, alpha, beta, color, depth=2):
    """Tìm kiếm tĩnh nâng cao để tránh hiệu ứng chân trời"""
    stand_pat = evaluate_board(board, color)
    
    if depth == 0:
        return stand_pat
        
    if stand_pat >= beta:
        return beta
    
    if stand_pat > alpha:
        alpha = stand_pat
        
    # Kiểm tra xem có đang bị chiếu không, nếu có thì xem xét tất cả các nước đi
    if is_check(board, color):
        all_moves = get_cached_valid_moves(board, color)
    else:
        # Chỉ xét các nước ăn quân có lợi và các nước phong hậu
        all_moves = get_cached_valid_moves(board, color)
        tactical_moves = []
        
        for from_pos, to_pos in all_moves:
            moving_piece = board.get_piece(from_pos)
            captured_piece = board.get_piece(to_pos)
            
            # Nước ăn quân
            if captured_piece:
                moving_value = PIECE_VALUES.get(moving_piece.__class__.__name__, 0)
                captured_value = PIECE_VALUES.get(captured_piece.__class__.__name__, 0)
                
                # Chỉ xét các nước ăn có lợi hoặc ăn ngang giá
                if captured_value >= moving_value - 50:  # Cho phép một chút chênh lệch
                    tactical_moves.append((from_pos, to_pos))
            
            # Nước phong hậu
            elif isinstance(moving_piece, Pawn):
                if ((moving_piece.color == "white" and to_pos[0] == 0) or 
                    (moving_piece.color == "black" and to_pos[0] == 7)):
                    tactical_moves.append((from_pos, to_pos))
        
        all_moves = tactical_moves if tactical_moves else []
    
    all_moves = order_moves(all_moves, board, color)
    
    for from_pos, to_pos in all_moves:
        new_board = copy.deepcopy(board)
        new_board.move_piece(from_pos, to_pos)
        
        piece = new_board.get_piece(to_pos)
        if isinstance(piece, Pawn):
            if ((piece.color == "white" and to_pos[0] == 0) or 
                (piece.color == "black" and to_pos[0] == 7)):
                new_board.set_piece(queen.Queen(piece.color), to_pos)
                
        score = -quiescence_search(new_board, -beta, -alpha, opponent_color(color), depth - 1)
        
        if score >= beta:
            return beta
            
        if score > alpha:
            alpha = score
    
    return alpha

def minimax_alpha_beta(board, depth, alpha, beta, maximizing_player, color):
    """Thuật toán minimax với alpha-beta pruning và các cải tiến khác"""
    # Hash bàn cờ để tra cứu trong bảng transposition
    board_hash = hash_board(board)
    
    # Kiểm tra trong bảng ghi nhớ
    if board_hash in transposition_table:
        stored_depth, stored_value, stored_move = transposition_table[board_hash]
        if stored_depth >= depth:
            return stored_value, stored_move
    
    # Nếu đã tìm đến độ sâu giới hạn thì dùng tìm kiếm tĩnh để đánh giá
    if depth == 0:
        eval_score = quiescence_search(board, alpha, beta, color)
        return eval_score, None
    
    current_player = color if maximizing_player else opponent_color(color)
    all_moves = get_cached_valid_moves(board, current_player)
    
    # Không có nước đi hợp lệ, kiểm tra chiếu tướng hoặc hòa cờ
    if not all_moves:
        if is_check(board, current_player):
            # Chiếu bí: giá trị rất thấp nếu mình thua, rất cao nếu đối phương thua
            return (-20000 if maximizing_player else 20000), None
        else:
            # Hòa cờ
            return 0, None
    
    # Tối ưu: Sắp xếp các nước đi để cắt tỉa hiệu quả hơn
    all_moves = order_moves(all_moves, board, current_player)
    
    best_move = None
    if maximizing_player:
        max_eval = float("-inf")
        for from_pos, to_pos in all_moves:
            # Tạo bàn cờ mới sau khi đi nước đó
            new_board = copy.deepcopy(board)
            new_board.move_piece(from_pos, to_pos)

            # Xử lý phong cấp cho tốt
            piece = new_board.get_piece(to_pos)
            if isinstance(piece, Pawn):
                if ((piece.color == "white" and to_pos[0] == 0) or 
                    (piece.color == "black" and to_pos[0] == 7)):
                    new_board.set_piece(queen.Queen(piece.color), to_pos)

            # Đệ quy để đánh giá các nước đi tiếp theo
            eval_score, _ = minimax_alpha_beta(new_board, depth - 1, alpha, beta, False, color)
            
            # Nếu tìm thấy nước đi tốt hơn thì cập nhật
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = (from_pos, to_pos)

            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break  # Beta cutoff
        
        # Lưu kết quả vào bảng ghi nhớ
        transposition_table[board_hash] = (depth, max_eval, best_move)
        return max_eval, best_move
    else:
        min_eval = float("inf")
        for from_pos, to_pos in all_moves:
            new_board = copy.deepcopy(board)
            new_board.move_piece(from_pos, to_pos)

            # Xử lý phong cấp cho tốt
            piece = new_board.get_piece(to_pos)
            if isinstance(piece, Pawn):
                if ((piece.color == "white" and to_pos[0] == 0) or 
                    (piece.color == "black" and to_pos[0] == 7)):
                    new_board.set_piece(queen.Queen(piece.color), to_pos)
                    
            # Đệ quy để đánh giá các nước đi tiếp theo
            eval_score, _ = minimax_alpha_beta(new_board, depth - 1, alpha, beta, True, color)

            if eval_score < min_eval:
                min_eval = eval_score
                best_move = (from_pos, to_pos)
            
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        
         # Lưu kết quả vào bảng ghi nhớ
        transposition_table[board_hash] = (depth, min_eval, best_move)
        return min_eval, best_move

def opponent_color(color):
    return "black" if color == "white" else "white"