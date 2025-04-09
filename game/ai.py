import copy
from board import board
from move import get_all_valid_moves

def evaluate_board(board, color):
    piece_values = {
        "Pawn": 1,
        "Knight": 3,
        "Bishop": 3,
        "Rook": 5,
        "Queen": 9,
        "King": 1000
    }

    score = 0
    for row in board.board:
        for piece in row:
            if piece:
                value = piece_values.get(piece.__class__.__name__, 0)
                score += value if piece.color == color else -value

def minimax(board, depth, maxmizing_player, color):
    if depth == 0:
        return evaluate_board(board, color), None
    
    best_move = None
    all_moves = get_all_valid_moves(board.board, color if maxmizing_player else opponent_color(color))

    if maxmizing_player:
        max_eval = float("-inf")
        for from_pos, to_pos in all_moves:
            new_board = copy.deepcopy(board)
            new_board.move_piece(from_pos, to_pos)
            eval_score, _ = minimax(new_board, depth - 1, False, color)
            
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = (from_pos, to_pos)
            
        return max_eval, best_move
    else:
        min_eval = float("inf")
        for from_pos, to_pos in all_moves:
            new_board = copy.deepcopy(board)
            new_board.move_piece(from_pos, to_pos)
            eval_score, _ = minimax(new_board, depth - 1, True, color)

            if eval_score < min_eval:
                min_eval = eval_score
                best_move = (from_pos, to_pos)
            
        return min_eval, best_move
    
def opponent_color(color):
    return "black" if color == "white" else "white"
