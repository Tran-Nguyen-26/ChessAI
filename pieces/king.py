from pieces.piece import Piece

class King(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
        self._checking_castling = False

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
        
        if not self._checking_castling:
            castling_moves = self.get_castling_moves(board)
            moves.extend(castling_moves)
                
        return moves

    def get_castling_moves(self, board):
        castling_moves = []
        row, col = self.position

        if self.has_moved or self.is_in_check(board):
            return []
        
        self._checking_castling = True
    
        if self.can_castle_kingside(board):
            castling_moves.append((row, col + 2))
        
        if self.can_castle_queenside(board):
            castling_moves.append((row, col - 2))
        
        self._checking_castling = False
        return castling_moves

    def can_castle_kingside(self, board):
        row, col = self.position

        rook_position = (row, 7)
        rook = board.get_piece(rook_position)
        if not rook or rook.__class__.__name__ != "Rook" or rook.color != self.color:
            return False
        
        if hasattr(rook, 'has_moved') and rook.has_moved:
            return False
        
        for c in range(col + 1, 7):
            if board.get_piece((row, c)) is not None:
                return False
        
        for c in range(col, col + 3):
            if self.is_square_attacked(board, row, c):
                return False
        
        return True
    
    def can_castle_queenside(self, board):
        row, col = self.position

        rook_position = (row, 0)
        rook = board.get_piece(rook_position)
        if not rook or rook.__class__.__name__ != "Rook" or rook.color != self.color:
            return False
        
        if hasattr(rook, 'has_moved') and rook.has_moved:
            return False
        
        for c in range(1, col):
            if board.get_piece((row, c)) is not None:
                return False
        
        for c in range(col, col - 3, -1):
            if self.is_square_attacked(board, row, c):
                return False
        
        return True
            
    def is_in_check(self, board):
        return self.is_square_attacked(board, *self.position)
        
    def is_square_attacked(self, board, row, col):
        opponent_color = "black" if self.color == "white" else "black"
        for r in range(8):
            for c in range(8):
                piece = board.get_piece((r, c))
                if piece and piece.color == opponent_color:
                    piece_type = piece.__class__.__name__
                    if piece_type == "Pawn":
                        # Tốt chỉ tấn công theo đường chéo
                        pawn_attacks = []
                        if piece.color == "white":
                            pawn_attacks = [(r - 1, c - 1), (r - 1, c + 1)]
                        else:  # black
                            pawn_attacks = [(r + 1, c - 1), (r + 1, c + 1)]

                        if (row, col) in pawn_attacks:
                            return True
                    
                    elif piece_type == "Knight":
                        # Mã tấn công theo kiểu chữ L
                        knight_moves = [
                            (r + 2, c + 1), (r + 2, c - 1),
                            (r - 2, c + 1), (r - 2, c - 1),
                            (r + 1, c + 2), (r + 1, c - 2),
                            (r - 1, c + 2), (r - 1, c - 2)
                        ]
                        if (row, col) in knight_moves:
                            return True
                    
                    elif piece_type == "King":
                        # Vua tấn công các ô xung quanh
                        if abs(r - row) <= 1 and abs(c - col) <= 1:
                            return True
                    
                    elif piece_type == "Rook" or piece_type == "Queen":
                        # Kiểm tra theo hàng và cột (xe và hậu)
                        if r == row or c == col:
                            # Kiểm tra xem có quân cờ nào đứng giữa không
                            blocking = False
                            if r == row:
                                start, end = min(c, col), max(c, col)
                                for check_c in range(start + 1, end):
                                    if board.get_piece((r, check_c)):
                                        blocking = True
                                        break
                            else:  # c == col
                                start, end = min(r, row), max(r, row)
                                for check_r in range(start + 1, end):
                                    if board.get_piece((check_r, c)):
                                        blocking = True
                                        break
                            
                            if not blocking:
                                return True
                    
                    if piece_type == "Bishop" or piece_type == "Queen":
                        # Kiểm tra theo đường chéo (tượng và hậu)
                        if abs(r - row) == abs(c - col):
                            # Xác định hướng đường chéo
                            dr = 1 if r < row else -1
                            dc = 1 if c < col else -1
                            
                            # Kiểm tra xem có quân cờ nào đứng giữa không
                            blocking = False
                            check_r, check_c = r + dr, c + dc
                            while (check_r, check_c) != (row, col):
                                if board.get_piece((check_r, check_c)):
                                    blocking = True
                                    break
                                check_r += dr
                                check_c += dc
                            
                            if not blocking:
                                return True
    
        return False