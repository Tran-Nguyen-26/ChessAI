import chess
import time
import random
import os
import platform
import subprocess
import shutil

# Piece values
PAWN_VALUE = 100
KNIGHT_VALUE = 320
BISHOP_VALUE = 330
ROOK_VALUE = 500
QUEEN_VALUE = 900
KING_VALUE = 20000  # High value to prioritize king safety

# Position tables for each piece
# Pawns are stronger as they advance and control the center
PAWN_TABLE = [
    0, 0, 0, 0, 0, 0, 0, 0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
    5, 5, 10, 25, 25, 10, 5, 5,
    0, 0, 0, 20, 20, 0, 0, 0,
    5, -5, -10, 0, 0, -10, -5, 5,
    5, 10, 10, -20, -20, 10, 10, 5,
    0, 0, 0, 0, 0, 0, 0, 0
]

# Knights are most effective in the center
KNIGHT_TABLE = [
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20, 0, 0, 0, 0, -20, -40,
    -30, 0, 10, 15, 15, 10, 0, -30,
    -30, 5, 15, 20, 20, 15, 5, -30,
    -30, 0, 15, 20, 20, 15, 0, -30,
    -30, 5, 10, 15, 15, 10, 5, -30,
    -40, -20, 0, 5, 5, 0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50
]

# Bishops prefer long diagonals
BISHOP_TABLE = [
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -10, 0, 10, 10, 10, 10, 0, -10,
    -10, 5, 5, 10, 10, 5, 5, -10,
    -10, 0, 5, 10, 10, 5, 0, -10,
    -10, 0, 10, 10, 10, 10, 0, -10,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -20, -10, -10, -10, -10, -10, -10, -20
]

# Rooks are stronger on open files
ROOK_TABLE = [
    0, 0, 0, 0, 0, 0, 0, 0,
    5, 10, 10, 10, 10, 10, 10, 5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    0, 0, 0, 5, 5, 0, 0, 0
]

# Queen combines value of rook and bishop
QUEEN_TABLE = [
    -20, -10, -10, -5, -5, -10, -10, -20,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -10, 0, 5, 5, 5, 5, 0, -10,
    -5, 0, 5, 5, 5, 5, 0, -5,
    0, 0, 5, 5, 5, 5, 0, -5,
    -10, 5, 5, 5, 5, 5, 0, -10,
    -10, 0, 5, 0, 0, 0, 0, -10,
    -20, -10, -10, -5, -5, -10, -10, -20
]

# King prefers safety (different tables for middlegame and endgame)
KING_MIDDLE_TABLE = [
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -20, -30, -30, -40, -40, -30, -30, -20,
    -10, -20, -20, -20, -20, -20, -20, -10,
    20, 20, 0, 0, 0, 0, 20, 20,
    20, 30, 10, 0, 0, 10, 30, 20
]

KING_END_TABLE = [
    -50, -40, -30, -20, -20, -30, -40, -50,
    -30, -20, -10, 0, 0, -10, -20, -30,
    -30, -10, 20, 30, 30, 20, -10, -30,
    -30, -10, 30, 40, 40, 30, -10, -30,
    -30, -10, 30, 40, 40, 30, -10, -30,
    -30, -10, 20, 30, 30, 20, -10, -30,
    -30, -30, 0, 0, 0, 0, -30, -30,
    -50, -30, -30, -30, -30, -30, -30, -50
]


class ChessAI:
    def __init__(self, depth=4, time_limit=5):
        self.depth = depth
        self.time_limit = time_limit  # Maximum time in seconds
        self.board = chess.Board()
        self.transposition_table = {}
        self.nodes_searched = 0
        self.best_move_found = None

        self.use_stockfish = True  # Mặc định sử dụng Stockfish nếu có thể
        self.stockfish_path = self._find_stockfish()  # Tìm đường dẫn đến Stockfish
        self.stockfish_process = None
        self.stockfish_strength = 20  # Cường độ mặc định (1-20)
        self.use_stockfish_as_opponent = False  # Chế độ đấu với Stockfish

        self.piece_values = {
            chess.PAWN: PAWN_VALUE,
            chess.KNIGHT: KNIGHT_VALUE,
            chess.BISHOP: BISHOP_VALUE,
            chess.ROOK: ROOK_VALUE,
            chess.QUEEN: QUEEN_VALUE,
            chess.KING: KING_VALUE
        }

        # Khởi tạo Stockfish nếu có
        if self.stockfish_path and self.use_stockfish:
            self._init_stockfish()

        self._init_zobrist_keys()

    def _init_zobrist_keys(self):
        """Khởi tạo Zobrist keys để hash vị trí bàn cờ"""
        self.zobrist_piece_keys = [[[random.randint(1, 2 ** 64 - 1) for _ in range(12)] for _ in range(64)] for _ in
                                   range(2)]
        self.zobrist_castling_keys = [random.randint(1, 2 ** 64 - 1) for _ in range(16)]
        self.zobrist_en_passant_keys = [random.randint(1, 2 ** 64 - 1) for _ in range(8)]
        self.zobrist_side_key = random.randint(1, 2 ** 64 - 1)

    def _compute_zobrist_hash(self):
        """Tính toán Zobrist hash cho vị trí hiện tại"""
        h = 0

        # Hash các quân cờ
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                piece_idx = (piece.piece_type - 1) + (6 if piece.color == chess.BLACK else 0)
                h ^= self.zobrist_piece_keys[piece.color][square][piece_idx]

        # Hash lượt đi
        if self.board.turn == chess.WHITE:
            h ^= self.zobrist_side_key

        # Hash quyền nhập thành
        castling = 0
        if self.board.has_kingside_castling_rights(chess.WHITE):
            castling |= 1
        if self.board.has_queenside_castling_rights(chess.WHITE):
            castling |= 2
        if self.board.has_kingside_castling_rights(chess.BLACK):
            castling |= 4
        if self.board.has_queenside_castling_rights(chess.BLACK):
            castling |= 8
        h ^= self.zobrist_castling_keys[castling]

        # Hash en passant
        if self.board.ep_square:
            file = chess.square_file(self.board.ep_square)
            h ^= self.zobrist_en_passant_keys[file]

        return h

    def reset_board(self):
        """Reset the board to starting position"""
        self.board = chess.Board()
        self.transposition_table = {}

    def set_board_from_fen(self, fen):
        """Set board from FEN notation"""
        try:
            self.board = chess.Board(fen)
            self.transposition_table = {}
            return True
        except ValueError:
            return False

    def make_move(self, move):
        """Make a move on the board"""
        try:
            if isinstance(move, str):
                move = chess.Move.from_uci(move)
            if move in self.board.legal_moves:
                self.board.push(move)
                return True
            return False
        except Exception as e:
            print(f"Error making move: {e}")
            return False

    def get_ai_move(self):
        """Lấy nước đi từ AI hoặc Stockfish tùy chế độ"""
        if self.use_stockfish_as_opponent and self.board.turn == chess.BLACK:
            # Cho Stockfish đi quân đen
            return self._get_stockfish_move(1000)  # 1 giây suy nghĩ
        else:
            # Sử dụng AI thuật toán riêng cho quân trắng
            return self._get_internal_ai_move()

    def _get_internal_ai_move(self):
        """Find the best move using iterative deepening with alpha-beta pruning"""

        # If there's only one legal move, play it immediately
        legal_moves = list(self.board.legal_moves)
        if len(legal_moves) == 1:
            return legal_moves[0]

        # Sử dụng Stockfish nếu được kích hoạt và sẵn có
        if self.use_stockfish and self.stockfish_process:
            # Chuyển đổi độ khó thành thời gian suy nghĩ cho Stockfish
            thinking_time = 100  # ms
            if self.depth <= 2:  # Dễ
                thinking_time = 100
            elif self.depth == 3:  # Trung bình
                thinking_time = 500
            elif self.depth == 4:  # Khó
                thinking_time = 1000
            else:  # Rất khó
                thinking_time = 2000

            move = self._get_stockfish_move(thinking_time)
            if move:
                print("Đang sử dụng nước đi từ Stockfish:", move)
                return move
            else:
                print("Không nhận được nước đi từ Stockfish, chuyển sang thuật toán riêng")
        else:
            print("Đang sử dụng thuật toán riêng (không sử dụng Stockfish)")

        self.nodes_searched = 0
        start_time = time.time()
        self.best_move_found = None

        # Iterative deepening
        for current_depth in range(1, self.depth + 1):
            alpha = float('-inf')
            beta = float('inf')
            best_score = float('-inf')

            # Sort moves for better pruning efficiency
            moves = self._order_moves(legal_moves)

            for move in moves:
                self.board.push(move)
                score = -self._alpha_beta(current_depth - 1, -beta, -alpha)
                self.board.pop()

                if score > best_score:
                    best_score = score
                    self.best_move_found = move

                alpha = max(alpha, score)

            print(f"Depth {current_depth}: Best move = {self.best_move_found}, Score = {best_score}")

            # Check if time limit is exceeded
            if time.time() - start_time > self.time_limit:
                print(f"Time limit reached after depth {current_depth}")
                break

        elapsed_time = time.time() - start_time
        print(f"Searched {self.nodes_searched} nodes in {elapsed_time:.2f} seconds")

        # Fallback to a random move if no best move was found (shouldn't happen)
        if self.best_move_found is None and legal_moves:
            print("Warning: No best move found, selecting random move")
            self.best_move_found = random.choice(legal_moves)

        return self.best_move_found

    def __del__(self):
        """Dọn dẹp khi đối tượng bị hủy"""
        if self.stockfish_process:
            self._send_to_stockfish("quit")
            self.stockfish_process.terminate()
            self.stockfish_process = None

    def _order_moves(self, moves):
        """Sắp xếp nước đi nâng cao với killer moves và history heuristic"""
        scored_moves = []

        # Thêm trường dữ liệu cho killer moves và history
        if not hasattr(self, 'killer_moves'):
            self.killer_moves = [[None, None] for _ in range(100)]  # Lưu 2 killer moves cho mỗi độ sâu

        if not hasattr(self, 'history_table'):
            self.history_table = {}  # Bảng history heuristic

        current_depth = len(self.board.move_stack)

        for move in moves:
            score = 0
            move_key = (move.from_square, move.to_square)

            # MVV-LVA (Most Valuable Victim - Least Valuable Aggressor)
            if self.board.is_capture(move):
                victim_square = move.to_square
                victim_piece = self.board.piece_at(victim_square)

                if self.board.is_en_passant(move):
                    score = 10 * PAWN_VALUE
                elif victim_piece:
                    aggressor_piece = self.board.piece_at(move.from_square)
                    score = 10 * self.piece_values[victim_piece.piece_type] - self.piece_values[
                        aggressor_piece.piece_type]

            # Thưởng cho phong hậu
            if move.promotion:
                score += 900 if move.promotion == chess.QUEEN else 500

            # Thưởng cho nước chiếu
            self.board.push(move)
            gives_check = self.board.is_check()
            self.board.pop()

            if gives_check:
                score += 50

            # Thưởng cho nhập thành
            if self.board.is_castling(move):
                score += 60

            # Thưởng cho killer moves
            if current_depth < len(self.killer_moves) and move in self.killer_moves[current_depth]:
                score += 30

            # Thưởng cho history heuristic
            if move_key in self.history_table:
                score += min(self.history_table[move_key] // 10, 200)  # Giới hạn ảnh hưởng

            scored_moves.append((move, score))

        # Sắp xếp nước đi theo điểm giảm dần
        scored_moves.sort(key=lambda x: x[1], reverse=True)

        return [move for move, _ in scored_moves]

    def _alpha_beta(self, depth, alpha, beta, allow_null_move=True):
        """Alpha-beta pruning với null move pruning"""
        self.nodes_searched += 1

        # Kiểm tra bảng transposition
        board_hash = hash(self.board._transposition_key())
        if board_hash in self.transposition_table and self.transposition_table[board_hash][0] >= depth:
            return self.transposition_table[board_hash][1]

        # Kiểm tra trạng thái kết thúc
        if self.board.is_checkmate():
            return -10000 if self.board.turn else 10000

        if self.board.is_stalemate() or self.board.is_insufficient_material():
            return 0

        # Null Move Pruning
        if allow_null_move and depth >= 3 and not self._is_endgame() and not self.board.is_check():
            self.board.push(chess.Move.null())
            null_value = -self._alpha_beta(depth - 3, -beta, -beta + 1, False)
            self.board.pop()

            if null_value >= beta:
                return beta

        # Quiescence search tại các nút lá
        if depth <= 0:
            return self._quiescence_search(alpha, beta)

        # Sinh và sắp xếp các nước đi
        moves = self._order_moves(list(self.board.legal_moves))

        best_score = float('-inf')
        legal_moves_searched = 0

        for i, move in enumerate(moves):
            # Kiểm tra xem nước đi có là capture hoặc promote không
            is_capture_or_promotion = self.board.is_capture(move) or move.promotion

            self.board.push(move)

            # Áp dụng LMR cho các nước không phải capture/promotion và không phải 2 nước đầu tiên
            if depth >= 3 and i >= 2 and not is_capture_or_promotion and not self.board.is_check():
                # Reduced depth search
                score = -self._alpha_beta(depth - 2, -alpha - 1, -alpha, allow_null_move)
                # Nếu search giảm độ sâu cho kết quả tốt, thực hiện lại search đầy đủ
                if score > alpha:
                    score = -self._alpha_beta(depth - 1, -beta, -alpha, allow_null_move)
            else:
                # Full depth search cho các nước quan trọng
                score = -self._alpha_beta(depth - 1, -beta, -alpha, allow_null_move)

            self.board.pop()
            legal_moves_searched += 1

            best_score = max(best_score, score)
            alpha = max(alpha, score)

            if alpha >= beta:
                break  # Beta cutoff

        # Lưu kết quả vào bảng transposition
        self.transposition_table[board_hash] = (depth, best_score)

        return best_score

    def _quiescence_search(self, alpha, beta, depth=0, max_depth=4):
        """Quiescence search nâng cao"""
        self.nodes_searched += 1

        # Ngăn độ sâu quá lớn trong quiescence search
        if depth >= max_depth:
            return self._evaluate_position()

        stand_pat = self._evaluate_position()

        # Delta pruning
        if stand_pat >= beta:
            return beta

        # Nếu đang bị chiếu, cần xem xét tất cả các nước đi hợp lệ
        if self.board.is_check():
            moves = list(self.board.legal_moves)
        else:
            # Chỉ xem xét captures và promotions
            moves = [m for m in self.board.legal_moves if self.board.is_capture(m) or m.promotion]

            # Thêm các nước chiếu vào danh sách
            for m in list(self.board.legal_moves):
                if m not in moves:  # Nếu chưa xem xét
                    self.board.push(m)
                    gives_check = self.board.is_check()
                    self.board.pop()

                    if gives_check:
                        moves.append(m)

        # Cập nhật alpha nếu stand_pat tốt hơn
        if stand_pat > alpha:
            alpha = stand_pat

        # Sắp xếp nước đi để cải thiện pruning
        moves = self._order_moves(moves)

        for move in moves:
            self.board.push(move)
            score = -self._quiescence_search(-beta, -alpha, depth + 1, max_depth)
            self.board.pop()

            if score >= beta:
                return beta

            if score > alpha:
                alpha = score

        return alpha

    def _evaluate_position(self):
        """Đánh giá vị trí bàn cờ toàn diện"""
        if self.board.is_checkmate():
            return -10000 if self.board.turn else 10000

        if self.board.is_stalemate() or self.board.is_insufficient_material():
            return 0  # Hòa

        # Xác định giai đoạn ván đấu
        is_endgame = self._is_endgame()
        game_phase = self._calculate_game_phase()

        # Đánh giá cơ bản về vật chất và vị trí
        material_score = self._evaluate_material()
        position_score = self._evaluate_piece_position(game_phase)

        # Đánh giá nâng cao về các khía cạnh chiến thuật
        pawn_structure_score = self._evaluate_pawn_structure()
        king_safety_score = self._evaluate_king_safety(is_endgame)
        mobility_score = self._evaluate_mobility()
        center_control_score = self._evaluate_center_control()

        # Đánh giá về sự phối hợp giữa các quân
        piece_coordination_score = self._evaluate_piece_coordination()
        development_score = self._evaluate_development()

        # Tổng hợp điểm với trọng số khác nhau tùy theo giai đoạn
        total_score = material_score

        # Các yếu tố vị trí và chiến thuật có trọng số khác nhau tùy theo giai đoạn
        total_score += position_score
        total_score += pawn_structure_score

        # Trong giai đoạn đầu và giữa, an toàn vua và phát triển quan trọng hơn
        if game_phase < 1.0:  # Không phải tàn cuộc
            total_score += king_safety_score
            total_score += 0.8 * development_score
            total_score += 0.7 * center_control_score
            total_score += 0.6 * piece_coordination_score
            total_score += 0.5 * mobility_score
        else:  # Tàn cuộc
            total_score += 0.3 * king_safety_score
            total_score += 0.5 * development_score
            total_score += 0.5 * center_control_score
            total_score += 0.8 * piece_coordination_score
            total_score += 1.0 * mobility_score  # Tính linh động quan trọng hơn trong tàn cuộc

        # Trả về điểm từ góc nhìn của người chơi hiện tại
        return total_score if self.board.turn == chess.WHITE else -total_score

    def _evaluate_development(self):
        """Đánh giá mức độ phát triển quân trong khai cuộc"""
        score = 0

        # Chỉ đánh giá nếu đang ở giai đoạn khai cuộc (ít hơn 10 nước đi)
        if len(self.board.move_stack) > 20:
            return 0

        # Thưởng cho việc phát triển mã, tượng ra khỏi vị trí ban đầu
        for piece_type in [chess.KNIGHT, chess.BISHOP]:
            # Vị trí ban đầu của mã và tượng trắng
            white_initial = [chess.B1, chess.G1, chess.C1, chess.F1] if piece_type == chess.KNIGHT else [chess.C1,
                                                                                                         chess.F1]
            # Kiểm tra xem các quân đã di chuyển khỏi vị trí ban đầu chưa
            for square in white_initial:
                piece = self.board.piece_at(square)
                if not piece or piece.piece_type != piece_type or piece.color != chess.WHITE:
                    score += 10  # Đã di chuyển

            # Tương tự cho quân đen
            black_initial = [chess.B8, chess.G8, chess.C8, chess.F8] if piece_type == chess.KNIGHT else [chess.C8,
                                                                                                         chess.F8]
            for square in black_initial:
                piece = self.board.piece_at(square)
                if not piece or piece.piece_type != piece_type or piece.color != chess.BLACK:
                    score -= 10  # Đã di chuyển

        # Phạt cho việc di chuyển hậu quá sớm
        white_queen_square = chess.D1
        if not (self.board.piece_at(white_queen_square) and
                self.board.piece_at(white_queen_square).piece_type == chess.QUEEN and
                self.board.piece_at(white_queen_square).color == chess.WHITE):
            # Hậu đã di chuyển
            moves_count = len(self.board.move_stack) // 2  # Số lượt của mỗi bên
            if moves_count < 7:  # Nếu di chuyển hậu quá sớm
                score -= 20

        black_queen_square = chess.D8
        if not (self.board.piece_at(black_queen_square) and
                self.board.piece_at(black_queen_square).piece_type == chess.QUEEN and
                self.board.piece_at(black_queen_square).color == chess.BLACK):
            # Hậu đã di chuyển
            moves_count = (len(self.board.move_stack) + 1) // 2  # Số lượt của đen
            if moves_count < 7:  # Nếu di chuyển hậu quá sớm
                score += 20

        return score

    def _calculate_game_phase(self):
        """Tính toán giai đoạn ván đấu (0.0 là khai cuộc, 1.0 là tàn cuộc)"""
        # Đếm quân chủ chốt (hậu, xe, mã, tượng)
        total_phase = 24  # Tổng giá trị ban đầu: 2 hậu (8) + 4 xe (8) + 4 mã (4) + 4 tượng (4)

        current_phase = total_phase

        # Trừ đi giá trị cho từng quân đã mất
        current_phase -= len(self.board.pieces(chess.QUEEN, chess.WHITE)) * 4
        current_phase -= len(self.board.pieces(chess.QUEEN, chess.BLACK)) * 4
        current_phase -= len(self.board.pieces(chess.ROOK, chess.WHITE)) * 2
        current_phase -= len(self.board.pieces(chess.ROOK, chess.BLACK)) * 2
        current_phase -= len(self.board.pieces(chess.BISHOP, chess.WHITE)) * 1
        current_phase -= len(self.board.pieces(chess.BISHOP, chess.BLACK)) * 1
        current_phase -= len(self.board.pieces(chess.KNIGHT, chess.WHITE)) * 1
        current_phase -= len(self.board.pieces(chess.KNIGHT, chess.BLACK)) * 1

        # Chuyển đổi thành tỷ lệ (0.0 - 1.0)
        phase = current_phase / total_phase

        # Đảo ngược để 0.0 là khai cuộc và 1.0 là tàn cuộc
        return 1.0 - min(1.0, max(0.0, phase))

    def _evaluate_center_control(self):
        """Evaluate control of the center"""
        score = 0
        central_squares = [chess.D4, chess.E4, chess.D5, chess.E5]
        extended_center = [chess.C3, chess.D3, chess.E3, chess.F3,
                           chess.C4, chess.F4,
                           chess.C5, chess.F5,
                           chess.C6, chess.D6, chess.E6, chess.F6]

        # Score for pieces in center
        for square in central_squares:
            piece = self.board.piece_at(square)
            if piece:
                bonus = 10 if piece.piece_type in [chess.PAWN, chess.KNIGHT] else 5
                score += bonus if piece.color == chess.WHITE else -bonus

        # Score for control of center and extended center
        for square in central_squares:
            score += 8 * len(self.board.attackers(chess.WHITE, square))
            score -= 8 * len(self.board.attackers(chess.BLACK, square))

        for square in extended_center:
            score += 4 * len(self.board.attackers(chess.WHITE, square))
            score -= 4 * len(self.board.attackers(chess.BLACK, square))

        return score

    def _evaluate_pawn_structure(self):
        """Đánh giá cấu trúc tốt nâng cao"""
        score = 0
        white_pawns = self.board.pieces(chess.PAWN, chess.WHITE)
        black_pawns = self.board.pieces(chess.PAWN, chess.BLACK)

        # Đánh giá tốt được bảo vệ
        for square in white_pawns:
            if any(self.board.is_pawn_attack(defender, square) for defender in white_pawns):
                score += 15

        for square in black_pawns:
            if any(self.board.is_pawn_attack(defender, square) for defender in black_pawns):
                score -= 15

        # Phạt tốt chặn nhau
        for file_num in range(8):
            file_mask = chess.BB_FILES[file_num]
            white_pawns_in_file = white_pawns & chess.SquareSet(file_mask)
            white_pawn_ranks = [chess.square_rank(sq) for sq in white_pawns_in_file]

            # Kiểm tra tốt chặn nhau (cùng cột nhưng chênh lệch 1 hàng)
            if len(white_pawn_ranks) >= 2:
                white_pawn_ranks.sort()
                for i in range(len(white_pawn_ranks) - 1):
                    if white_pawn_ranks[i + 1] - white_pawn_ranks[i] == 1:
                        score -= 25  # Phạt nặng hơn cho tốt chặn nhau

            # Tương tự cho quân đen
            black_pawns_in_file = black_pawns & chess.SquareSet(file_mask)
            black_pawn_ranks = [chess.square_rank(sq) for sq in black_pawns_in_file]
            if len(black_pawn_ranks) >= 2:
                black_pawn_ranks.sort()
                for i in range(len(black_pawn_ranks) - 1):
                    if black_pawn_ranks[i] - black_pawn_ranks[i + 1] == 1:
                        score += 25

        return score

    def _evaluate_king_safety(self, is_endgame):
        """Đánh giá an toàn vua nâng cao"""
        score = 0

        if not is_endgame:
            # Đánh giá quyền nhập thành
            if self.board.has_kingside_castling_rights(chess.WHITE):
                score += 30
            if self.board.has_queenside_castling_rights(chess.WHITE):
                score += 20
            if self.board.has_kingside_castling_rights(chess.BLACK):
                score -= 30
            if self.board.has_queenside_castling_rights(chess.BLACK):
                score -= 20

            # Kiểm tra vua đã nhập thành chưa
            white_king_square = self.board.king(chess.WHITE)
            if white_king_square == chess.G1 or white_king_square == chess.C1:
                score += 50  # Thưởng cho việc đã nhập thành

            black_king_square = self.board.king(chess.BLACK)
            if black_king_square == chess.G8 or black_king_square == chess.C8:
                score -= 50

            # Đánh giá tường tốt bảo vệ vua
            if white_king_square is not None:
                score += self._evaluate_king_pawn_shield(white_king_square, chess.WHITE)

            if black_king_square is not None:
                score -= self._evaluate_king_pawn_shield(black_king_square, chess.BLACK)

            # Phạt cho đường mở tới vua
            score += self._evaluate_king_open_files(chess.WHITE)
            score -= self._evaluate_king_open_files(chess.BLACK)

        return score

    def _evaluate_king_pawn_shield(self, king_square, color):
        """Đánh giá tường tốt bảo vệ vua"""
        score = 0
        king_file = chess.square_file(king_square)
        king_rank = chess.square_rank(king_square)

        # Xác định hàng để kiểm tra dựa trên màu
        pawn_ranks = range(king_rank + 1, min(king_rank + 3, 8)) if color == chess.WHITE else range(
            max(king_rank - 2, 0), king_rank)

        # Kiểm tra tốt phía trước vua
        shield_count = 0
        for f in range(max(0, king_file - 1), min(7, king_file + 1) + 1):
            for r in pawn_ranks:
                square = chess.square(f, r)
                piece = self.board.piece_at(square)
                if piece and piece.piece_type == chess.PAWN and piece.color == color:
                    shield_count += 1
                    # Thưởng thêm cho tốt ở cột vua
                    if f == king_file:
                        score += 5

        # Thưởng dựa vào số lượng tốt bảo vệ
        score += shield_count * 10

        return score

    def _evaluate_king_open_files(self, color):
        """Phạt cho đường mở tới vua"""
        score = 0
        king_square = self.board.king(color)

        if king_square is None:
            return 0

        king_file = chess.square_file(king_square)

        # Kiểm tra cột vua và các cột kề
        for f in range(max(0, king_file - 1), min(7, king_file + 1) + 1):
            file_mask = chess.BB_FILES[f]

            # Kiểm tra xem có tốt nào trên cột này không
            pawns_on_file = self.board.pieces(chess.PAWN, chess.WHITE) | self.board.pieces(chess.PAWN, chess.BLACK)
            pawns_on_file &= chess.SquareSet(file_mask)

            if not pawns_on_file:
                # Cột mở - phạt điểm
                penalty = -30 if f == king_file else -15
                score += penalty

        return score

    def _get_king_attack_zone(self, king_square):
        """Get squares around the king that constitute the attack zone"""
        attack_zone = set()
        king_file = chess.square_file(king_square)
        king_rank = chess.square_rank(king_square)

        for f in range(max(0, king_file - 1), min(7, king_file + 1) + 1):
            for r in range(max(0, king_rank - 1), min(7, king_rank + 1) + 1):
                square = chess.square(f, r)
                if square != king_square:
                    attack_zone.add(square)

        return attack_zone

    def _evaluate_mobility(self):
        """Evaluate piece mobility"""
        # Save current turn
        original_turn = self.board.turn
        score = 0

        # Evaluate white mobility
        self.board.turn = chess.WHITE
        white_mobility = len(list(self.board.legal_moves))

        # Evaluate black mobility
        self.board.turn = chess.BLACK
        black_mobility = len(list(self.board.legal_moves))

        # Restore original turn
        self.board.turn = original_turn

        mobility_score = 2 * (white_mobility - black_mobility)

        # Add check/checkmate threat bonus
        if self.board.is_check():
            if self.board.turn == chess.WHITE:
                score -= 50  # White is in check
            else:
                score += 50  # Black is in check

        return score + mobility_score

    def _is_endgame(self):
        """Determine if the position is in the endgame phase"""
        # Count major pieces (queens and rooks)
        queens = len(self.board.pieces(chess.QUEEN, chess.WHITE)) + len(self.board.pieces(chess.QUEEN, chess.BLACK))
        rooks = len(self.board.pieces(chess.ROOK, chess.WHITE)) + len(self.board.pieces(chess.ROOK, chess.BLACK))
        total_pieces = queens + rooks + len(self.board.pieces(chess.KNIGHT, chess.WHITE)) + len(
            self.board.pieces(chess.KNIGHT, chess.BLACK)) + len(self.board.pieces(chess.BISHOP, chess.WHITE)) + len(
            self.board.pieces(chess.BISHOP, chess.BLACK))

        # Endgame if:
        # 1. No queens, or
        # 2. Each side has at most one major piece and less than 6 total pieces
        return queens == 0 or (queens + rooks <= 2 and total_pieces <= 6)

    def get_board_evaluation(self):
        """Get current board evaluation"""
        return self._evaluate_position()

    def set_depth(self, depth):
        """Set search depth"""
        self.depth = max(1, depth)

    def set_time_limit(self, seconds):
        """Set time limit in seconds"""
        self.time_limit = max(1, seconds)

    def _find_stockfish(self):
        """Tìm đường dẫn đến tệp thực thi Stockfish"""
        # Thử tìm trong thư mục hiện tại hoặc thư mục 'engines'
        common_paths = []

        # Thêm đường dẫn tương đối trong thư mục dự án
        current_dir = os.path.dirname(__file__)
        common_paths.append(os.path.join(current_dir, 'stockfish'))
        common_paths.append(os.path.join(current_dir, 'engines', 'stockfish'))

        # Thêm đường dẫn dựa trên hệ điều hành
        if platform.system() == 'Windows':
            common_paths.append(os.path.join(os.path.dirname(__file__), 'stockfish.exe'))
            common_paths.append(os.path.join(os.path.dirname(__file__), 'engines', 'stockfish.exe'))

            common_paths.append(os.path.join(os.path.dirname(__file__), 'stockfish-windows-x86-64-avx2.exe'))
            common_paths.append(os.path.join(os.path.dirname(__file__), 'engines', 'stockfish-windows-x86-64-avx2.exe'))

            # Thêm đường dẫn cài đặt phổ biến của Windows
            program_files = os.environ.get('ProgramFiles', 'C:\\Program Files')
            common_paths.append(os.path.join(program_files, 'Stockfish', 'stockfish.exe'))

            common_paths.append(os.path.join(program_files, 'Stockfish', 'stockfish-windows-x86-64-avx2.exe'))
        elif platform.system() == 'Linux':
            # Kiểm tra nếu stockfish có trong PATH
            stockfish_in_path = shutil.which('stockfish')
            if stockfish_in_path:
                return stockfish_in_path
            common_paths.append('/usr/games/stockfish')
            common_paths.append('/usr/local/bin/stockfish')
        elif platform.system() == 'Darwin':  # macOS
            common_paths.append('/usr/local/bin/stockfish')
            common_paths.append('/opt/homebrew/bin/stockfish')

        # Kiểm tra từng đường dẫn
        for path in common_paths:
            if os.path.isfile(path) and os.access(path, os.X_OK):
                return path

        print("Không tìm thấy Stockfish. Sử dụng AI tích hợp.")
        return None

    def _init_stockfish(self):
        """Khởi tạo quá trình Stockfish"""
        if not self.stockfish_path:
            self.use_stockfish = False
            return False

        try:
            # Khởi tạo quá trình Stockfish
            self.stockfish_process = subprocess.Popen(
                self.stockfish_path,
                universal_newlines=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=1  # Line buffered
            )

            # Gửi các lệnh khởi tạo
            self._send_to_stockfish("uci")
            self._send_to_stockfish(f"setoption name Skill Level value {self.stockfish_strength}")
            self._send_to_stockfish("ucinewgame")
            self._send_to_stockfish("isready")

            # Đọc phản hồi cho đến khi gặp "readyok"
            while True:
                line = self.stockfish_process.stdout.readline().strip()
                if line == "readyok":
                    break

            return True
        except Exception as e:
            print(f"Lỗi khi khởi tạo Stockfish: {e}")
            self.use_stockfish = False
            return False

    def _send_to_stockfish(self, command):
        """Gửi lệnh đến Stockfish"""
        if self.stockfish_process and self.stockfish_process.stdin:
            self.stockfish_process.stdin.write(command + "\n")
            self.stockfish_process.stdin.flush()

    def _get_stockfish_move(self, time_ms=1000):
        """Lấy nước đi từ Stockfish với giới hạn thời gian (ms)"""
        if not self.stockfish_process:
            return None

        # Gửi trạng thái bàn cờ hiện tại
        self._send_to_stockfish(f"position fen {self.board.fen()}")

        # Yêu cầu Stockfish tìm nước đi tốt nhất
        depth_cmd = f"go depth {self.depth}"
        time_cmd = f"go movetime {time_ms}"

        # Chọn lệnh dựa vào độ khó
        if self.stockfish_strength < 10:  # Dễ
            self._send_to_stockfish(depth_cmd)
        else:  # Khó hơn, sử dụng giới hạn thời gian
            self._send_to_stockfish(time_cmd)

        best_move = None
        while True:
            line = self.stockfish_process.stdout.readline().strip()
            if line.startswith("bestmove"):
                best_move = line.split()[1]
                break

        # Chuyển đổi định dạng nước đi
        if best_move:
            try:
                return chess.Move.from_uci(best_move)
            except ValueError:
                print(f"Lỗi định dạng nước đi Stockfish: {best_move}")
                return None

        return None

    def set_stockfish_strength(self, level):
        """Đặt độ mạnh của Stockfish (1-20)"""
        self.stockfish_strength = max(1, min(20, level))
        if self.stockfish_process:
            self._send_to_stockfish(f"setoption name Skill Level value {self.stockfish_strength}")
            self._send_to_stockfish("ucinewgame")

    def toggle_stockfish(self, use_stockfish):
        """Bật/tắt sử dụng Stockfish"""
        self.use_stockfish = use_stockfish
        if use_stockfish and not self.stockfish_process and self.stockfish_path:
            self._init_stockfish()

    def set_stockfish_strength(self, level):
        """Đặt độ khó cho Stockfish (1-20)"""
        self.stockfish_strength = max(1, min(20, level))
        if self.stockfish_process:
            self._send_to_stockfish(f"setoption name Skill Level value {self.stockfish_strength}")

    def toggle_stockfish_opponent(self, enable):
        """Bật/tắt chế độ đấu với Stockfish"""
        self.use_stockfish_as_opponent = enable
        if enable and not self.stockfish_process and self.stockfish_path:
            self._init_stockfish()


