import chess
import time
import random
import os
import platform
import subprocess
import shutil
from SFController import SF

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


class ChessAI(SF):
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
        """Order moves to improve alpha-beta pruning efficiency"""
        scored_moves = []

        for move in moves:
            score = 0
            # Prioritize captures by victim-aggressor value
            if self.board.is_capture(move):
                victim_square = move.to_square
                victim_piece = self.board.piece_at(victim_square)

                # Handle en passant captures
                if self.board.is_en_passant(move):
                    score = 10 * PAWN_VALUE
                elif victim_piece:
                    # MVV-LVA (Most Valuable Victim - Least Valuable Aggressor)
                    aggressor_piece = self.board.piece_at(move.from_square)
                    score = 10 * self.piece_values[victim_piece.piece_type] - self.piece_values[
                        aggressor_piece.piece_type]

            # Prioritize promotions
            if move.promotion:
                score += 900 if move.promotion == chess.QUEEN else 500

            # Prioritize checks
            self.board.push(move)
            if self.board.is_check():
                score += 50
            self.board.pop()

            # Prioritize castling
            if self.board.is_castling(move):
                score += 60

            scored_moves.append((move, score))

        # Sort moves by score in descending order
        scored_moves.sort(key=lambda x: x[1], reverse=True)
        return [move for move, _ in scored_moves]

    def _alpha_beta(self, depth, alpha, beta):
        """Alpha-beta pruning search algorithm"""
        self.nodes_searched += 1

        # Check transposition table
        board_hash = hash(self.board._transposition_key())
        if board_hash in self.transposition_table and self.transposition_table[board_hash][0] >= depth:
            return self.transposition_table[board_hash][1]

        # Check terminal states
        if self.board.is_checkmate():
            return -10000 if self.board.turn else 10000
        if self.board.is_stalemate() or self.board.is_insufficient_material():
            return 0

        # Quiescence search at leaf nodes to handle horizon effect
        if depth <= 0:
            return self._quiescence_search(alpha, beta)

        # Generate and order moves
        moves = self._order_moves(list(self.board.legal_moves))

        best_score = float('-inf')
        for move in moves:
            self.board.push(move)
            score = -self._alpha_beta(depth - 1, -beta, -alpha)
            self.board.pop()

            best_score = max(best_score, score)
            alpha = max(alpha, score)
            if alpha >= beta:
                break  # Beta cutoff

        # Store result in transposition table
        self.transposition_table[board_hash] = (depth, best_score)
        return best_score

    def _quiescence_search(self, alpha, beta, depth=0, max_depth=3):
        """Quiescence search to evaluate only quiet positions"""
        # Prevent excessive depth in quiescence search
        if depth >= max_depth:
            return self._evaluate_position()

        stand_pat = self._evaluate_position()

        # Delta pruning
        if stand_pat >= beta:
            return beta
        if alpha < stand_pat:
            alpha = stand_pat

        # Look at captures only
        for move in self._order_moves([m for m in self.board.legal_moves if self.board.is_capture(m)]):
            self.board.push(move)
            score = -self._quiescence_search(-beta, -alpha, depth + 1, max_depth)
            self.board.pop()

            if score >= beta:
                return beta
            if score > alpha:
                alpha = score

        return alpha

    def _evaluate_position(self):
        """Evaluate the current board position"""
        if self.board.is_checkmate():
            return -10000 if self.board.turn else 10000

        if self.board.is_stalemate() or self.board.is_insufficient_material():
            return 0  # Draw

        total_score = 0
        is_endgame = self._is_endgame()

        # Material and position evaluation
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if not piece:
                continue

            # Basic piece value
            value = self.piece_values[piece.piece_type]

            # Position value based on piece-square tables
            position_value = 0
            if piece.piece_type == chess.PAWN:
                position_value = PAWN_TABLE[square if piece.color else 63 - square]
            elif piece.piece_type == chess.KNIGHT:
                position_value = KNIGHT_TABLE[square if piece.color else 63 - square]
            elif piece.piece_type == chess.BISHOP:
                position_value = BISHOP_TABLE[square if piece.color else 63 - square]
            elif piece.piece_type == chess.ROOK:
                position_value = ROOK_TABLE[square if piece.color else 63 - square]
            elif piece.piece_type == chess.QUEEN:
                position_value = QUEEN_TABLE[square if piece.color else 63 - square]
            elif piece.piece_type == chess.KING:
                position_value = KING_END_TABLE[square if piece.color else 63 - square] if is_endgame else \
                KING_MIDDLE_TABLE[square if piece.color else 63 - square]

            # Add or subtract based on piece color
            if piece.color == chess.WHITE:
                total_score += value + position_value
            else:
                total_score -= value + position_value

        # Additional evaluation factors
        total_score += self._evaluate_center_control()
        total_score += self._evaluate_pawn_structure()
        total_score += self._evaluate_king_safety(is_endgame)
        total_score += self._evaluate_mobility()

        # Return score from current player's perspective
        return total_score if self.board.turn == chess.WHITE else -total_score

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
        """Evaluate pawn structure"""
        score = 0

        # Passed pawns
        white_pawns = self.board.pieces(chess.PAWN, chess.WHITE)
        black_pawns = self.board.pieces(chess.PAWN, chess.BLACK)

        # Reward passed pawns
        for square in white_pawns:
            rank = chess.square_rank(square)
            file = chess.square_file(square)
            is_passed = True

            # Check if there are any black pawns that can block this pawn
            for f in range(max(0, file - 1), min(7, file + 1) + 1):
                for r in range(rank + 1, 8):
                    if chess.square(f, r) in black_pawns:
                        is_passed = False
                        break
                if not is_passed:
                    break

            if is_passed:
                score += 20 + 10 * rank  # More value for advanced passed pawns

        for square in black_pawns:
            rank = chess.square_rank(square)
            file = chess.square_file(square)
            is_passed = True

            # Check if there are any white pawns that can block this pawn
            for f in range(max(0, file - 1), min(7, file + 1) + 1):
                for r in range(0, rank):
                    if chess.square(f, r) in white_pawns:
                        is_passed = False
                        break
                if not is_passed:
                    break

            if is_passed:
                score -= 20 + 10 * (7 - rank)  # More value for advanced passed pawns

        # Penalize doubled pawns
        for file_num in range(8):  # Files from 0 (a-file) to 7 (h-file)
            file_mask = chess.BB_FILES[file_num]

            white_pawns_in_file = len(white_pawns & chess.SquareSet(file_mask))
            black_pawns_in_file = len(black_pawns & chess.SquareSet(file_mask))

            if white_pawns_in_file > 1:
                score -= 10 * (white_pawns_in_file - 1)
            if black_pawns_in_file > 1:
                score += 10 * (black_pawns_in_file - 1)

        # Penalize isolated pawns
        for square in white_pawns:
            file_num = chess.square_file(square)
            isolated = True

            # Check adjacent files for friendly pawns
            for adj_file in [max(0, file_num - 1), min(7, file_num + 1)]:
                if adj_file == file_num:
                    continue
                if white_pawns & chess.SquareSet(chess.BB_FILES[adj_file]):
                    isolated = False
                    break

            if isolated:
                score -= 15

        for square in black_pawns:
            file_num = chess.square_file(square)
            isolated = True

            # Check adjacent files for friendly pawns
            for adj_file in [max(0, file_num - 1), min(7, file_num + 1)]:
                if adj_file == file_num:
                    continue
                if black_pawns & chess.SquareSet(chess.BB_FILES[adj_file]):
                    isolated = False
                    break

            if isolated:
                score += 15

        return score

    def _evaluate_king_safety(self, is_endgame):
        """Evaluate king safety"""
        score = 0

        if not is_endgame:
            # Castling rights
            if self.board.has_kingside_castling_rights(chess.WHITE):
                score += 30
            if self.board.has_queenside_castling_rights(chess.WHITE):
                score += 20
            if self.board.has_kingside_castling_rights(chess.BLACK):
                score -= 30
            if self.board.has_queenside_castling_rights(chess.BLACK):
                score -= 20

            # King safety - pawn shield
            white_king_square = self.board.king(chess.WHITE)
            black_king_square = self.board.king(chess.BLACK)

            if white_king_square is not None:
                white_king_file = chess.square_file(white_king_square)
                white_king_rank = chess.square_rank(white_king_square)

                # Check for pawn shield in front of king
                for f in range(max(0, white_king_file - 1), min(7, white_king_file + 1) + 1):
                    for r in range(white_king_rank + 1, min(white_king_rank + 3, 8)):
                        square = chess.square(f, r)
                        piece = self.board.piece_at(square)
                        if piece and piece.piece_type == chess.PAWN and piece.color == chess.WHITE:
                            score += 10

            if black_king_square is not None:
                black_king_file = chess.square_file(black_king_square)
                black_king_rank = chess.square_rank(black_king_square)

                # Check for pawn shield in front of king
                for f in range(max(0, black_king_file - 1), min(7, black_king_file + 1) + 1):
                    for r in range(max(black_king_rank - 2, 0), black_king_rank):
                        square = chess.square(f, r)
                        piece = self.board.piece_at(square)
                        if piece and piece.piece_type == chess.PAWN and piece.color == chess.BLACK:
                            score -= 10

            # King attack zone
            if white_king_square is not None:
                attack_zone = self._get_king_attack_zone(white_king_square)
                black_attackers = 0

                for square in attack_zone:
                    attackers = self.board.attackers(chess.BLACK, square)
                    black_attackers += len(attackers)

                # Penalize heavily for attackers near the king
                score -= 5 * black_attackers

            if black_king_square is not None:
                attack_zone = self._get_king_attack_zone(black_king_square)
                white_attackers = 0

                for square in attack_zone:
                    attackers = self.board.attackers(chess.WHITE, square)
                    white_attackers += len(attackers)

                # Penalize heavily for attackers near the king
                score += 5 * white_attackers

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
