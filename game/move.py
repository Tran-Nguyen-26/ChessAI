def is_in_bounds(pos):
    row, col = pos
    return 0 <= row < 8 and 0 <= col < 8

def is_empty(board, pos):
    row, col = pos
    return board[row][col] is None

def is_enemy(board, pos, color):
    row, col = pos
    target = board[row][col]
    return target is not None and target.color != color
def get_all_valid_moves(board, color):
    moves = []
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece and piece.color == color:
                for move in piece.get_valid_moves(board):
                    moves.append((row, col), move)
                
    return moves

