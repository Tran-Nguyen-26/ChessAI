from pieces.piece import Piece


class Knight(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)

    def get_valid_moves(self, board):
        moves = []
        row, col = self.position
        knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1),
                        (1, 2), (1, -2), (-1, 2), (-1, -2)]

        for move in knight_moves:
            r, c = row + move[0], col + move[1]
            if 0 <= r < 8 and 0 <= c < 8:
                if board.get_piece((r, c)) is None or board.get_piece((r, c)).color != self.color:
                    # Lưu vị trí hiện tại và quân cờ tại vị trí đích (nếu có)
                    original_position = self.position
                    captured_piece = board.get_piece((r, c))

                    # Thực hiện nước đi thử nghiệm
                    self.position = (r, c)
                    board.board[r][c] = self
                    board.board[original_position[0]][original_position[1]] = None

                    # Tìm vua cùng màu
                    king = board._find_king(self.color)

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
                        moves.append((r, c))

        return moves