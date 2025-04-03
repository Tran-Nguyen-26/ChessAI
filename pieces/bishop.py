from pieces.piece import Piece

class Bishop(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
    
    def get_valid_moves(self, board):
        moves = []
        row, col = self.position
        directions = [(1, 1), (-1, -1), (1, -1), (-1, 1)]
