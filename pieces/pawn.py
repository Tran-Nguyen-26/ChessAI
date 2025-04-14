from pieces.piece import Piece

class Pawn(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)

    def get_valid_moves(self, board):
        moves = []
        row, col = self.position
        direction = -1 if self.color == "white" else 1 #Tốt trắng đi lên, tốt đen đi xuống

        if board.get_piece((row + direction,col)) is None:
            moves.append((row + direction, col))

        if (self.color == "white" and row == 6) or (self.color == "black" and row == 1):
            if board.get_piece((row + 2 * direction,col)) is None:
                moves.append((row + 2 * direction, col))
        
        for d_col in [-1, 1]:
            new_row = row + direction
            new_col = col + d_col
            if 0 <= col + d_col < 8: #kiểm tra cột không nằm ngoài bàn cờ
                target = board.get_piece((row + direction,col + d_col))
                if target is not None and target.color != self.color:
                    moves.append((new_row, new_col))
        
        return moves
    
        