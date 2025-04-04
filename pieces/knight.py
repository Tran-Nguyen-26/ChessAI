from pieces.piece import Piece

class Knight(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
    
    def get_valid_moves(self, board):
        moves = []
        row, col = self.position
        knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1),
                        (1, 2), (1, -2), (-1, 2), (-1, -2)]

        for move in knight_moves:
            r, c = row + move[0], col + move[1]
            if 0 <= r < 8 and 0 <= c < 8:
                if board[r][c] is None or board[r][c].color != self.color:
                    moves.append((r, c))
        
        return moves