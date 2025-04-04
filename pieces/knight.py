from pieces.piece import Piece

class Knight(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
    
    def get_valid_moves(self, board):
        moves = []
        row, col = self.position
        knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1),
                        (1, 2), (1, -2), (-1, 2), (-1, -2)]