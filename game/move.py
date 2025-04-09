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
    all_moves = []
    for row in range(8):
        for col in range(8):
            piece = board.get_piece((row, col))
            if piece and piece.color == color:
                valid_moves = piece.get_valid_moves(board)
                for move in valid_moves:
                    all_moves.append(((row, col), move))
                
    return all_moves

