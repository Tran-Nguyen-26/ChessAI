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
        self.promote_piece = None
        self.promote_position = None

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
        
        if not piece or end_pos not in piece.get_valid_moves(self):
            return False, None

        #　Xử lí nhập thành
        is_castling = False
        if piece.__class__.__name__ == "King":
            start_row, start_col = start_pos
            end_row, end_col = end_pos

            if end_col - start_col == 2:
                is_castling = True
                rook = self.get_piece((start_row, 7))
                self.remove_piece((start_row, 7))
                self.set_piece(rook, (start_row, start_col + 1))
                rook.has_moved = True
            
            elif start_col - end_col == 2:
                is_castling = True
                rook = self.get_piece((start_row, 0))
                self.remove_piece((start_row, 0))
                self.set_piece(rook, (start_row, start_col - 1))
                rook.has_moved = True


        captured_king_color = None
        if target and target.__class__.__name__ == "King":
            captured_king_color = target.color

        if target and target.color != piece.color:
            self.remove_piece(end_pos)
        
        self.remove_piece(start_pos)
        self.set_piece(piece, end_pos)

        piece.has_moved = True
    
        # Xử lí điều kiện phong quân
        if piece.__class__.__name__ == "Pawn":
            end_row, end_col = end_pos
            if (piece.color == "white" and end_row == 0) or (piece.color == "black" and end_row == 7):
                self.set_piece(Queen(piece.color, end_pos), end_pos)
            
        return True, captured_king_color

    def promote_pawn(self, piece_type):
        if not self.promote_piece or not self.promote_position:
            return False
        
        position = self.promote_position
        color = self.promote_piece.color

        new_piece = None
        if piece_type == "queen":
            new_piece = Queen(color, position)
        elif piece_type == "rook":
            new_piece = Rook(color, position)
        elif piece_type == "bishop":
            new_piece = Bishop(color, position)
        elif piece_type == "knight":
            new_piece = Knight(color, position)
        else:
            return False
        
        self.remove_piece(position)
        self.set_piece(new_piece, position)

        self.promote_piece = None
        self.promote_position = None

        return True