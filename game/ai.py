import copy
from board import board
from game.move import get_all_valid_moves

def evaluate_board(board, color):
    piece_values = {
        "Pawn": 100,
        "Knight": 320,
        "Bishop": 330,
        "Rook": 500,
        "Queen": 900, 
        "King": 20000
    }

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

    position_tables = {
        "Pawn": pawn_position,
        "Knight": knight_position,
        "Bishop": bishop_position,
        "Rook": rook_position,
        "Queen": queen_position,
        "King": king_middlegame
    }

    piece_count = 0
    pieces_by_color = {"white": 0, "black": 0}
    for row in board.board:
        for piece in row:
            if piece:
                piece_count += 1
                pieces_by_color[piece.color] += 1
    
    is_endgame = piece_count <= 10

    if is_endgame:
        position_tables["King"] = king_endgame
    
    material_score = 0
    position_score = 0
    pawn_structure_score = 0

    pawn_columns = {color: [0] * 8 for color in ["white", "black"]}
    for y in range(8):
        for x in range(8):
            piece = board.get_piece((y, x))
            if piece and piece.__class__.__name__ == "Pawn":
                pawn_columns[piece.color][x] += 1
    
    for y in range(8):
        for x in range(8):
            piece = board.get_piece((y, x))
            if piece:
                piece_type = piece.__class__.__name__
                value = piece_values.get(piece_type, 0)

                if piece.color == color:
                    material_score += value
                else:
                    material_score -= value

                if piece_type in position_tables:
                    if piece.color == "white":
                        pos_y = y
                    else:
                        pos_y = 7 - y
                    
                    pos_value = position_tables[piece_type][pos_y][x]
                    
                    if piece.color == color:
                        position_score += pos_value
                    else:
                        position_score -= pos_value
                    
                    if piece.color == color:
                        position_score += pos_value
                    else:
                        position_score -= pos_value
                
                if piece_type == "Pawn":
                    # Penalize doubled pawns
                    if pawn_columns[piece.color][x] > 1:
                        if piece.color == color:
                            pawn_structure_score -= 20
                        else:
                            pawn_structure_score += 20
                    
                    is_isolated = True
                    for adj_x in [x-1, x+1]:
                        if 0 <= adj_x < 8 and pawn_columns[piece.color][adj_x] > 0:
                            is_isolated = False
                            break
                    
                    if is_isolated:
                        if piece.color == color:
                            pawn_structure_score -= 15
                        else:
                            pawn_structure_score += 15
                        
    development_score = 0
    if piece_count > 24:  # Early game
        # Check if knights and bishops have moved from starting positions
        for piece_type in ["Knight", "Bishop"]:
            for y in range(8):
                for x in range(8):
                    piece = board.board[y][x]
                    if piece and piece.__class__.__name__ == piece_type:
                        # Check if piece moved from starting position
                        if piece.color == "white" and y != 7:
                            if piece.color == color:
                                development_score += 10
                            else:
                                development_score -= 10
                        elif piece.color == "black" and y != 0:
                            if piece.color == color:
                                development_score += 10
                            else:
                                development_score -= 10
                    
    center_control_score = 0
    center_squares = [(3, 3), (3, 4), (4, 3), (4, 4)]
    for cy, cx in center_squares:
        piece = board.board[cy][cx]
        if piece:
            if piece.color == color:
                center_control_score += 10
            else:
                center_control_score -= 10
    
    king_safety_score = 0
    for y in range(8):
        for x in range(8):
            piece = board.board[y][x]
            if piece and piece.__class__.__name__ == "King":
                # Count pieces protecting the king
                protectors = 0
                king_y, king_x = y, x
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        ny, nx = king_y + dy, king_x + dx
                        if 0 <= ny < 8 and 0 <= nx < 8 and (dy != 0 or dx != 0):
                            neighbor = board.board[ny][nx]
                            if neighbor and neighbor.color == piece.color:
                                protectors += 1
                
                if piece.color == color:
                    king_safety_score += protectors * 5
                else:
                    king_safety_score -= protectors * 5
    
    final_score = (
        material_score * 1.0 +          # Material is most important
        position_score * 0.5 +          # Position is important but secondary
        pawn_structure_score * 0.3 +    # Pawn structure influences long-term strategy
        development_score * 0.2 +       # Development matters in early game
        center_control_score * 0.3 +    # Center control is key strategic factor
        king_safety_score * 0.4         # King safety is critical
    )

    return final_score

def minimax_alpha_beta(board, depth, alpha, beta, maxmizing_player, color):
    if depth == 0:
        return evaluate_board(board, color), None
    
    best_move = None
    all_moves = get_all_valid_moves(board, color if maxmizing_player else opponent_color(color))

    if maxmizing_player:
        max_eval = float("-inf")
        for from_pos, to_pos in all_moves:
            new_board = copy.deepcopy(board)
            new_board.move_piece(from_pos, to_pos)
            eval_score, _ = minimax_alpha_beta(new_board, depth - 1, alpha, beta, False, color)
            
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = (from_pos, to_pos)

            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
            
        return max_eval, best_move
    else:
        min_eval = float("inf")
        for from_pos, to_pos in all_moves:
            new_board = copy.deepcopy(board)
            new_board.move_piece(from_pos, to_pos)
            eval_score, _ = minimax_alpha_beta(new_board, depth - 1, alpha, beta, True, color)

            if eval_score < min_eval:
                min_eval = eval_score
                best_move = (from_pos, to_pos)
            
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
            
        return min_eval, best_move
    
def opponent_color(color):
    return "black" if color == "white" else "white"
