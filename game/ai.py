import copy
from board import board
from game.move import get_all_valid_moves
from pieces import queen
from pieces.pawn import Pawn

# Bảng ghi nhớ vị trí để tránh tính toán lại các vị trí đã đánh giá
transposition_table = {}

def evaluate_board(board, color):
    #Đánh giá bàn cờ
    piece_values = {
        "Pawn": 100,
        "Knight": 320,
        "Bishop": 330,
        "Rook": 500,
        "Queen": 900, 
        "King": 20000
    }
    #Đánh giá sức mạnh tại mỗi vị trí của các quân cờ
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
    # Từ điển ánh xạ
    position_tables = {
        "Pawn": pawn_position,
        "Knight": knight_position,
        "Bishop": bishop_position,
        "Rook": rook_position,
        "Queen": queen_position,
        "King": king_middlegame
    }

    # Tối ưu: Thay vì đếm quân mỗi lần, ta sẽ đếm một lần trong quá trình đánh giá
    piece_count = 0
    pieces_by_color = {"white": 0, "black": 0}
    
    # Tối ưu: Khởi tạo các điểm số trước vòng lặp để tránh tính toán nhiều lần
    material_score = 0
    position_score = 0
    pawn_structure_score = 0
    development_score = 0
    center_control_score = 0
    king_safety_score = 0
    
    # Tối ưu: Khởi tạo mảng đếm quân tốt
    pawn_columns = {"white": [0] * 8, "black": [0] * 8}
    
    # Đếm số quân tốt theo cột trước
    for y in range(8):
        for x in range(8):
            piece = board.get_piece((y, x))
            if piece:
                piece_count += 1
                pieces_by_color[piece.color] += 1
                if piece.__class__.__name__ == "Pawn":
                    pawn_columns[piece.color][x] += 1

    # Nếu còn dưới 10 quân là giai đoạn cuối game
    is_endgame = piece_count <= 10
    if is_endgame:
        position_tables["King"] = king_endgame
    
    # Tối ưu: Lưu các ô trung tâm để kiểm tra nhanh hơn
    center_squares = {(3, 3), (3, 4), (4, 3), (4, 4)}
    
    # Đánh giá chính
    for y in range(8):
        for x in range(8):
            piece = board.get_piece((y, x))
            if not piece:
                continue
                
            piece_type = piece.__class__.__name__
            value = piece_values.get(piece_type, 0)
            
            # Nếu là quân mình thì cộng điểm, quân địch thì trừ điểm
            multiplier = 1 if piece.color == color else -1
            material_score += value * multiplier
            
            # Tính điểm vị trí các quân
            if piece_type in position_tables:
                pos_y = y if piece.color == "white" else 7 - y
                pos_value = position_tables[piece_type][pos_y][x]
                position_score += pos_value * multiplier
            
            # Đánh giá cấu trúc con Tốt
            if piece_type == "Pawn":
                # Penalize doubled pawns (trừ điểm nếu có các quân tốt chồng lên nhau)
                if pawn_columns[piece.color][x] > 1:
                    pawn_structure_score -= 20 * multiplier
                
                # Penalize isolated pawns (trừ điểm cho quân tốt bị cô lập)
                is_isolated = True
                for adj_x in [x-1, x+1]:
                    if 0 <= adj_x < 8 and pawn_columns[piece.color][adj_x] > 0:
                        is_isolated = False
                        break
                
                if is_isolated:
                    pawn_structure_score -= 15 * multiplier
            
            # Chấm điểm cho giai đoạn khai cuộc
            if piece_count > 24 and piece_type in ["Knight", "Bishop"]:
                if (piece.color == "white" and y != 7) or (piece.color == "black" and y != 0):
                    development_score += 10 * multiplier
            
            # Tính điểm kiểm soát trung tâm
            if (y, x) in center_squares:
                center_control_score += 10 * multiplier
            
            # Đánh giá an toàn của vua
            if piece_type == "King":
                protectors = 0
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < 8 and 0 <= nx < 8 and (dy != 0 or dx != 0):
                            neighbor = board.get_piece((ny, nx))
                            if neighbor and neighbor.color == piece.color:
                                protectors += 1
                
                king_safety_score += protectors * 5 * multiplier
    
    # Tối ưu: Chỉ tính toán một lần tổng điểm cuối cùng
    final_score = (
        material_score * 1.0 +          # Material is most important
        position_score * 0.5 +          # Position is important but secondary
        pawn_structure_score * 0.3 +    # Pawn structure influences long-term strategy
        development_score * 0.2 +       # Development matters in early game
        center_control_score * 0.3 +    # Center control is key strategic factor
        king_safety_score * 0.4         # King safety is critical
    )

    return final_score

# Tối ưu: Thêm hàm để sắp xếp các nước đi theo độ ưu tiên
def order_moves(moves, board, color):
    """Sắp xếp các nước đi để cải thiện hiệu quả cắt tỉa alpha-beta"""
    move_scores = []
    for from_pos, to_pos in moves:
        score = 0
        moving_piece = board.get_piece(from_pos)
        captured_piece = board.get_piece(to_pos)
        
        # Ưu tiên nước ăn quân
        if captured_piece:
            piece_values = {"Pawn": 10, "Knight": 32, "Bishop": 33, "Rook": 50, "Queen": 90, "King": 2000}
            moving_value = piece_values.get(moving_piece.__class__.__name__, 0)
            captured_value = piece_values.get(captured_piece.__class__.__name__, 0)
            score = 10 * captured_value - moving_value
        
        # Ưu tiên phong Hậu
        if isinstance(moving_piece, Pawn):
            if (moving_piece.color == "white" and to_pos[0] == 0) or (moving_piece.color == "black" and to_pos[0] == 7):
                score += 900  # Giá trị của Hậu
        
        # Ưu tiên kiểm soát trung tâm
        if to_pos in [(3, 3), (3, 4), (4, 3), (4, 4)]:
            score += 5
            
        move_scores.append((score, (from_pos, to_pos)))
    
    # Sắp xếp giảm dần theo điểm
    move_scores.sort(reverse=True)
    return [move for _, move in move_scores]

# Tối ưu: Thêm tìm kiếm tĩnh (quiescence search) cho các nước ăn quân
def quiescence_search(board, alpha, beta, color, depth=3):
    """Tìm kiếm tĩnh để tránh hiệu ứng chân trời"""
    stand_pat = evaluate_board(board, color)
    
    if depth == 0:
        return stand_pat
        
    if stand_pat >= beta:
        return beta
    
    if alpha < stand_pat:
        alpha = stand_pat
        
    all_moves = get_all_valid_moves(board, color)
    capture_moves = []
    
    # Chỉ xét các nước ăn quân
    for from_pos, to_pos in all_moves:
        if board.get_piece(to_pos) is not None:
            capture_moves.append((from_pos, to_pos))
    
    capture_moves = order_moves(capture_moves, board, color)
    
    for from_pos, to_pos in capture_moves:
        new_board = copy.deepcopy(board)
        new_board.move_piece(from_pos, to_pos)
        
        piece = new_board.get_piece(to_pos)
        if isinstance(piece, Pawn):
            if (piece.color == "white" and to_pos[0] == 0) or (piece.color == "black" and to_pos[0] == 7):
                new_board.set_piece(queen.Queen(piece.color), to_pos)
                
        score = -quiescence_search(new_board, -beta, -alpha, opponent_color(color), depth - 1)
        
        if score >= beta:
            return beta
            
        if score > alpha:
            alpha = score
    
    return alpha

def minimax_alpha_beta(board, depth, alpha, beta, maximizing_player, color):
    # Tạo khóa hash từ trạng thái bàn cờ để kiểm tra xem đã tính chưa
    board_hash = str(board.board)  # Đơn giản hóa, trong thực tế nên dùng hash function tốt hơn
    
    # Kiểm tra trong bảng ghi nhớ
    if board_hash in transposition_table and transposition_table[board_hash][0] >= depth:
        stored_depth, stored_value, stored_move = transposition_table[board_hash]
        return stored_value, stored_move
    
    # Nếu đã tìm đến độ sâu giới hạn thì dùng tìm kiếm tĩnh để đánh giá
    if depth == 0:
        eval_score = quiescence_search(board, alpha, beta, color)
        return eval_score, None
    
    best_move = None
    all_moves = get_all_valid_moves(board, color if maximizing_player else opponent_color(color))
    
    # Tối ưu: Sắp xếp các nước đi để cắt tỉa hiệu quả hơn
    all_moves = order_moves(all_moves, board, color if maximizing_player else opponent_color(color))
    
    # Không có nước đi hợp lệ, trả về giá trị đánh giá hiện tại
    if not all_moves:
        # Giả định là hòa cờ (không có hàm kiểm tra chiếu tướng trong code gốc)
        return 0, None
    
    if maximizing_player:
        max_eval = float("-inf")
        for from_pos, to_pos in all_moves:
            # Với mỗi nước đi tạo một bàn cờ mới sau khi đi nước đó
            new_board = copy.deepcopy(board)
            new_board.move_piece(from_pos, to_pos)

            piece = new_board.get_piece(to_pos)
            if isinstance(piece, Pawn):
                if (piece.color == "white" and to_pos[0] == 0) or (piece.color == "black" and to_pos[0] == 7):
                    new_board.set_piece(queen.Queen(piece.color), to_pos)

            # Đệ quy để đánh giá nước đi tiếp theo
            eval_score, _ = minimax_alpha_beta(new_board, depth - 1, alpha, beta, False, color)
            
            # Nếu điểm nước đi này cao hơn những nước trước thì cập nhật điểm tốt nhất
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = (from_pos, to_pos)

            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        
        # Lưu kết quả vào bảng ghi nhớ
        transposition_table[board_hash] = (depth, max_eval, best_move)
        return max_eval, best_move
    else:
        min_eval = float("inf")
        for from_pos, to_pos in all_moves:
            new_board = copy.deepcopy(board)
            new_board.move_piece(from_pos, to_pos)

            piece = new_board.get_piece(to_pos)
            if isinstance(piece, Pawn):
                if (piece.color == "white" and to_pos[0] == 0) or (piece.color == "black" and to_pos[0] == 7):
                    new_board.set_piece(queen.Queen(piece.color), to_pos)
                    
            # Đệ quy để đánh giá nước đi tiếp theo
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