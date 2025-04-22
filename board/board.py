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
        self.en_passant_target = None  # Thuộc tính để theo dõi ô mục tiêu en passant

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
        if 0 <= row < 8 and 0 <= col < 8: 
            return self.board[row][col]
        return None
        
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

        is_castling = False

        # Xử lý nhập thành
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


        # Xử lý bắt qua đường (en passant)
        captured_king_color = None
        if isinstance(piece, Pawn) and end_pos == self.en_passant_target:
            direction = -1 if piece.color == "white" else 1
            captured_row = end_pos[0] + direction  # Ô của tốt bị bắt
            captured_pos = (captured_row, end_pos[1])
            captured_piece = self.get_piece(captured_pos)
            if captured_piece and isinstance(captured_piece, Pawn) and captured_piece.color != piece.color:
                self.remove_piece(captured_pos)
        
        # Di chuyển quân cờ
        target = self.get_piece(end_pos)
        if target and target.color != piece.color:
            if target.__class__.__name__ == "King":
                captured_king_color = target.color
            self.remove_piece(end_pos)
        
        self.remove_piece(start_pos)
        self.set_piece(piece, end_pos)
        piece.has_moved = True

        # Cập nhật en_passant_target
        if isinstance(piece, Pawn) and abs(start_pos[0] - end_pos[0]) == 2:
            self.en_passant_target = ((start_pos[0] + end_pos[0]) // 2, end_pos[1])
        else:
            self.en_passant_target = None

        return True, captured_king_color
    
    def _find_king(self, color):
            for row in range(8):
                for col in range(8):
                    piece = self.get_piece((row, col))
                    if piece and isinstance(piece, King) and piece.color == color:
                        return piece
            return None
    