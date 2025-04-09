from pieces.piece import Piece

class King(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)

    def get_valid_moves(self, board):
        moves = []
        row, col = self.position
        king_moves = [(1, 0), (-1, 0), (0, 1), (0, -1),  
                    (1, 1), (-1, -1), (1, -1), (-1, 1)]

        for move in king_moves:
            r, c = row + move[0], col + move[1]
            if 0 <= r < 8 and 0 <= c < 8:
                if board.get_piece((r, c)) is None or board.get_piece((r, c)).color != self.color:
                    moves.append((r, c))
            
        return moves