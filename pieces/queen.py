from pieces.piece import Piece

class Queen(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)

    def get_valid_moves(self, board):
        moves = []
        row, col = self.position
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1),
                        (1, 1), (-1, -1), (1, -1), (-1, 1)]

        for direction in directions:
            r, c = row, col
            while 0 <= r + direction[0] < 8 and 0 <= c + direction[1] < 8:
                r += direction[0]
                c += direction[1]
                if board[r][c] is None:
                    moves.append((r, c))
                elif board[r][c].color != self.color:
                    moves.append((r, c))
                    break
                else:
                    break
        
        return moves