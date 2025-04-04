from pieces.piece import Piece

class Pawn(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)

    def get_valid_moves(self, board):
        moves = []
        row, col = self.position
        direction = -1 if self.color == "white" else 1 #Tốt trắng đi lên, tốt đen đi xuống

        if board[row + direction][col] is None:
            moves.append((row + direction, col))

        if (self.color == "white" and row == 6) or (self.color == "black" and row == 1):
            if board[row + 2 * direction][col] is None:
                moves.append((row + 2 * direction, col))
        
        for d_col in [-1, 1]:
            if 0 <= col + d_col < 8: #kiểm tra cột không nằm ngoài bàn cờ
                if board[row + direction][col + d_col] is not None:
                    moves.append((row, direction, col + d_col))
        
        return moves
        