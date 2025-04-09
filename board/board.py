from pieces.pawn import Pawn
from pieces.rook import Rook
from pieces.knight import Knight
from pieces.bishop import Bishop
from pieces.queen import Queen
from pieces.king import King

class Board:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self._initialize_pieces()
        self.king_pieces = {
            "white": None,
            "black": None
        }

    def _initialize_pieces(self):
        #black
        self.board[0][0] = Rook("black", (0, 0))
        self.board[0][1] = Knight("black", (0, 1))
        self.board[0][2] = Bishop("black", (0, 2))
        self.board[0][3] = Queen("black", (0, 3))
        self.board[0][4] = King("black", (0, 4))
        self.board[0][5] = Bishop("black", (0, 5))
        self.board[0][6] = Knight("black", (0, 6))
        self.board[0][7] = Rook("black", (0, 7))
        for i in range(8):
            self.board[1][i] = Pawn("black", (1, i))

        #white
        self.board[7][0] = Rook("white", (7, 0))
        self.board[7][1] = Knight("white", (7, 1))
        self.board[7][2] = Bishop("white", (7, 2))
        self.board[7][3] = Queen("white", (7, 3))
        self.board[7][4] = King("white", (7, 4))
        self.board[7][5] = Bishop("white", (7, 5))
        self.board[7][6] = Knight("white", (7, 6))
        self.board[7][7] = Rook("white", (7, 7))
        for i in range(8):
            self.board[6][i] = Pawn("white", (6, i))

    def get_piece(self, position):
        row, col = position
        return self.board[row][col]
        
    def set_piece(self, piece, position):
        row, col = position
        self.board[row][col] = piece
        piece.position = position
    
    def remove_piece(self,position):
        row, col = position
        self.board[row][col] = None
    
    def move_piece(self, start_pos, end_pos):
        piece = self.get_piece(start_pos)
        target = self.get_piece(end_pos)
        if piece and end_pos in piece.get_valid_moves(self):
            if target and target.color != piece.color:
                self.remove_piece(end_pos)

            self.remove_piece(start_pos)
            self.set_piece(piece, end_pos)
            return True
        
        return False