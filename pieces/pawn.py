from pieces.piece import Piece


class Pawn(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)

    def get_valid_moves(self, board):
        potential_moves = []
        row, col = self.position
        direction = -1 if self.color == "white" else 1  # Tốt trắng đi lên, tốt đen đi xuống

        # Di chuyển tiến 1 ô
        if 0 <= row + direction < 8 and board.get_piece((row + direction, col)) is None:
            potential_moves.append((row + direction, col))

        # Di chuyển tiến 2 ô (nếu là nước đi đầu tiên)
        if ((self.color == "white" and row == 6) or (self.color == "black" and row == 1)) and \
                board.get_piece((row + direction, col)) is None and \
                board.get_piece((row + 2 * direction, col)) is None:
            potential_moves.append((row + 2 * direction, col))

        # Ăn quân chéo
        for d_col in [-1, 1]:
            new_row = row + direction
            new_col = col + d_col
            if 0 <= new_row < 8 and 0 <= new_col < 8:  # Kiểm tra vị trí nằm trong bàn cờ
                target = board.get_piece((new_row, new_col))
                if target is not None and target.color != self.color:
                    potential_moves.append((new_row, new_col))

        # Lọc các nước đi không làm vua bị chiếu
        valid_moves = []
        for move in potential_moves:
            r, c = move

            # Lưu vị trí hiện tại và quân cờ tại vị trí đích (nếu có)
            original_position = self.position
            captured_piece = board.get_piece((r, c))

            # Thực hiện nước đi thử nghiệm
            self.position = (r, c)
            board.board[r][c] = self
            board.board[original_position[0]][original_position[1]] = None

            # Tìm vua cùng màu
            king = None
            for row_idx in range(8):
                for col_idx in range(8):
                    piece = board.get_piece((row_idx, col_idx))
                    if piece and piece.__class__.__name__ == "King" and piece.color == self.color:
                        king = piece
                        break
                if king:
                    break

            # Kiểm tra xem vua có bị chiếu sau khi thực hiện nước đi không
            is_valid = True
            if king and king.is_in_check(board):
                is_valid = False

            # Hoàn tác nước đi thử nghiệm
            self.position = original_position
            board.board[original_position[0]][original_position[1]] = self
            board.board[r][c] = captured_piece

            # Nếu nước đi không làm vua bị chiếu, thêm vào danh sách
            if is_valid:
                valid_moves.append((r, c))

        return valid_moves