from pieces.piece import Piece

class Pawn(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)

    def get_valid_moves(self, board):
        moves = []
        row, col = self.position
        direction = -1 if self.color == "white" else 1

        