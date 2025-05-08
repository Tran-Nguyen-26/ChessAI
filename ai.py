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
KING_VALUE = 20000

# Position tables (unchanged)
PAWN_TABLE = [
    0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
    5,  5, 10, 25, 25, 10,  5,  5,
    0,  0,  0, 20, 20,  0,  0,  0,
    5, -5,-10,  0,  0,-10, -5,  5,
    5, 10, 10,-20,-20, 10, 10,  5,
    0,  0,  0,  0,  0,  0,  0,  0
]

KNIGHT_TABLE = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50
]

BISHOP_TABLE = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -20,-10,-10,-10,-10,-10,-10,-20
]

ROOK_TABLE = [
    0,  0,  0,  0,  0,  0,  0,  0,
    5, 10, 10, 10, 10, 10, 10,  5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    0,  0,  0,  5,  5,  0,  0,  0
]

QUEEN_TABLE = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
    -5,  0,  5,  5,  5,  5,  0, -5,
    0,  0,  5,  5,  5,  5,  0, -5,
    -10,  5,  5,  5,  5,  5,  0,-10,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20
]

KING_MIDDLE_TABLE = [
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -10,-20,-20,-20,-20,-20,-20,-10,
    20, 20,  0,  0,  0,  0, 20, 20,
    20, 30, 10,  0,  0, 10, 30, 20
]

KING_END_TABLE = [
    -50,-40,-30,-20,-20,-30,-40,-50,
    -30,-20,-10,  0,  0,-10,-20,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-30,  0,  0,  0,  0,-30,-30,
    -50,-30,-30,-30,-30,-30,-30,-50
]

class ChessAI:
    def __init__(self, depth=4, time_limit=5):
        self.depth = depth
        self.time_limit = time_limit
        self.board = chess.Board()
        self.transposition_table = {}
        self.nodes_searched = 0
        self.best_move_found = None
        self.killer_moves = [[] for _ in range(depth + 1)]  # Killer moves for each depth

        self.use_stockfish = True
        self.stockfish_path = self._find_stockfish()
        self.stockfish_process = None
        self.stockfish_strength = 20
        self.use_stockfish_as_opponent = False

        self.piece_values = {
            chess.PAWN: PAWN_VALUE,
            chess.KNIGHT: KNIGHT_VALUE,
            chess.BISHOP: BISHOP_VALUE,
            chess.ROOK: ROOK_VALUE,
            chess.QUEEN: QUEEN_VALUE,
            chess.KING: KING_VALUE
        }

        if self.stockfish_path and self.use_stockfish:
            self._init_stockfish()

    def reset_board(self):
        self.board = chess.Board()
        self.transposition_table = {}
        self.killer_moves = [[] for _ in range(self.depth + 1)]

    def set_board_from_fen(self, fen):
        try:
            self.board = chess.Board(fen)
            self.transposition_table = {}
            self.killer_moves = [[] for _ in range(self.depth + 1)]
            return True
        except ValueError:
            return False

    def make_move(self, move):
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
        if self.use_stockfish_as_opponent and self.board.turn == chess.BLACK:
            return self._get_stockfish_move(1000)
        else:
            return self._get_internal_ai_move()

    def _get_internal_ai_move(self):
        legal_moves = list(self.board.legal_moves)
        if len(legal_moves) == 1:
            return legal_moves[0]

        if self.use_stockfish and self.stockfish_process:
            thinking_time = {2: 100, 3: 500, 4: 1000, 5: 2000}.get(self.depth, 1000)
            move = self._get_stockfish_move(thinking_time)
            if move:
                print("Using Stockfish move:", move)
                return move
            print("Stockfish failed, falling back to internal AI")

        self.nodes_searched = 0
        start_time = time.time()
        self.best_move_found = None

        for current_depth in range(1, self.depth + 1):
            alpha = float('-inf')
            beta = float('inf')
            best_score = float('-inf')
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

            if time.time() - start_time > self._dynamic_time_limit(legal_moves):
                print(f"Time limit reached after depth {current_depth}")
                break

        elapsed_time = time.time() - start_time
        print(f"Searched {self.nodes_searched} nodes in {elapsed_time:.2f} seconds")

        if self.best_move_found is None and legal_moves:
            print("Warning: No best move found, selecting random move")
            self.best_move_found = random.choice(legal_moves)

        return self.best_move_found

    def __del__(self):
        if self.stockfish_process:
            try:
                self._send_to_stockfish("quit")
                self.stockfish_process.terminate()
            except Exception as e:
                print(f"Error terminating Stockfish: {e}")
            finally:
                self.stockfish_process = None

    def _dynamic_time_limit(self, legal_moves):
        """Dynamically adjust time limit based on position complexity"""
        base_time = self.time_limit
        branching_factor = len(legal_moves)
        if branching_factor > 30:
            return base_time * 1.5  # More time for complex positions
        return base_time

    def _order_moves(self, moves, depth=0):
        scored_moves = []
        killer_moves = self.killer_moves[depth] if depth < len(self.killer_moves) else []

        for move in moves:
            score = 0
            if move in killer_moves:
                score += 10000  # High priority for killer moves
            if self.board.is_capture(move):
                victim_piece = self.board.piece_at(move.to_square) or chess.Piece(chess.PAWN, not self.board.turn)
                aggressor_piece = self.board.piece_at(move.from_square)
                score += 10 * self.piece_values[victim_piece.piece_type] - self.piece_values[aggressor_piece.piece_type]
            if move.promotion:
                score += 900 if move.promotion == chess.QUEEN else 500
            self.board.push(move)
            if self.board.is_check():
                score += 50
            self.board.pop()
            if self.board.is_castling(move):
                score += 60
            scored_moves.append((move, score))

        scored_moves.sort(key=lambda x: x[1], reverse=True)
        return [move for move, _ in scored_moves]

    def _alpha_beta(self, depth, alpha, beta):
        self.nodes_searched += 1
        board_hash = hash(self.board._transposition_key())
        if board_hash in self.transposition_table and self.transposition_table[board_hash][0] >= depth:
            return self.transposition_table[board_hash][1]

        if self.board.is_checkmate():
            return -10000 if self.board.turn else 10000
        if self.board.is_stalemate() or self.board.is_insufficient_material():
            return 0

        if depth <= 0:
            return self._quiescence_search(alpha, beta)

        moves = self._order_moves(list(self.board.legal_moves), depth)
        best_score = float('-inf')
        best_move = None

        for move in moves:
            self.board.push(move)
            score = -self._alpha_beta(depth - 1, -beta, -alpha)
            self.board.pop()

            if score > best_score:
                best_score = score
                best_move = move

            alpha = max(alpha, score)
            if alpha >= beta:
                if depth < len(self.killer_moves) and move not in self.killer_moves[depth]:
                    self.killer_moves[depth].append(move)
                break

        self.transposition_table[board_hash] = (depth, best_score, best_move)
        return best_score

    def _quiescence_search(self, alpha, beta, depth=0, max_depth=3):
        if depth >= max_depth:
            return self._evaluate_position()

        stand_pat = self._evaluate_position()
        if stand_pat >= beta:
            return beta
        if alpha < stand_pat:
            alpha = stand_pat

        for move in self._order_moves([m for m in self.board.legal_moves if self.board.is_capture(m)], depth):
            self.board.push(move)
            score = -self._quiescence_search(-beta, -alpha, depth + 1, max_depth)
            self.board.pop()

            if score >= beta:
                return beta
            if score > alpha:
                alpha = score

        return alpha

    def _evaluate_position(self):
        if self.board.is_checkmate():
            return -10000 if self.board.turn else 10000
        if self.board.is_stalemate() or self.board.is_insufficient_material():
            return 0

        total_score = 0
        is_endgame = self._is_endgame()

        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if not piece:
                continue

            value = self.piece_values[piece.piece_type]
            position_value = {
                chess.PAWN: PAWN_TABLE,
                chess.KNIGHT: KNIGHT_TABLE,
                chess.BISHOP: BISHOP_TABLE,
                chess.ROOK: ROOK_TABLE,
                chess.QUEEN: QUEEN_TABLE,
                chess.KING: KING_END_TABLE if is_endgame else KING_MIDDLE_TABLE
            }[piece.piece_type][square if piece.color else 63 - square]

            total_score += (value + position_value) if piece.color == chess.WHITE else -(value + position_value)

        # Bishop pair bonus
        if len(self.board.pieces(chess.BISHOP, chess.WHITE)) >= 2:
            total_score += 30
        if len(self.board.pieces(chess.BISHOP, chess.BLACK)) >= 2:
            total_score -= 30

        total_score += self._evaluate_center_control()
        total_score += self._evaluate_pawn_structure()
        total_score += self._evaluate_king_safety(is_endgame)
        total_score += self._evaluate_mobility()

        return total_score if self.board.turn == chess.WHITE else -total_score

    def _evaluate_center_control(self):
        score = 0
        central_squares = [chess.D4, chess.E4, chess.D5, chess.E5]
        extended_center = [chess.C3, chess.D3, chess.E3, chess.F3,
                           chess.C4, chess.F4,
                           chess.C5, chess.F5,
                           chess.C6, chess.D6, chess.E6, chess.F6]

        for square in central_squares:
            piece = self.board.piece_at(square)
            if piece:
                bonus = 10 if piece.piece_type in [chess.PAWN, chess.KNIGHT] else 5
                score += bonus if piece.color == chess.WHITE else -bonus
            score += 8 * len(self.board.attackers(chess.WHITE, square))
            score -= 8 * len(self.board.attackers(chess.BLACK, square))

        for square in extended_center:
            score += 4 * len(self.board.attackers(chess.WHITE, square))
            score -= 4 * len(self.board.attackers(chess.BLACK, square))

        return score

    def _evaluate_pawn_structure(self):
        score = 0
        white_pawns = self.board.pieces(chess.PAWN, chess.WHITE)
        black_pawns = self.board.pieces(chess.PAWN, chess.BLACK)

        for square in white_pawns:
            rank = chess.square_rank(square)
            file = chess.square_file(square)
            is_passed = all(chess.square(f, r) not in black_pawns
                            for f in range(max(0, file - 1), min(7, file + 2))
                            for r in range(rank + 1, 8))
            if is_passed:
                score += 20 + 10 * rank

        for square in black_pawns:
            rank = chess.square_rank(square)
            file = chess.square_file(square)
            is_passed = all(chess.square(f, r) not in white_pawns
                            for f in range(max(0, file - 1), min(7, file + 2))
                            for r in range(0, rank))
            if is_passed:
                score -= 20 + 10 * (7 - rank)

        for file_num in range(8):
            file_mask = chess.BB_FILES[file_num]
            white_pawns_in_file = len(white_pawns & chess.SquareSet(file_mask))
            black_pawns_in_file = len(black_pawns & chess.SquareSet(file_mask))
            if white_pawns_in_file > 1:
                score -= 10 * (white_pawns_in_file - 1)
            if black_pawns_in_file > 1:
                score += 10 * (black_pawns_in_file - 1)

        for square in white_pawns:
            file_num = chess.square_file(square)
            isolated = not any(white_pawns & chess.SquareSet(chess.BB_FILES[adj_file])
                               for adj_file in [file_num - 1, file_num + 1] if 0 <= adj_file <= 7)
            if isolated:
                score -= 15

        for square in black_pawns:
            file_num = chess.square_file(square)
            isolated = not any(black_pawns & chess.SquareSet(chess.BB_FILES[adj_file])
                               for adj_file in [file_num - 1, file_num + 1] if 0 <= adj_file <= 7)
            if isolated:
                score += 15

        return score

    def _evaluate_king_safety(self, is_endgame):
        score = 0
        if not is_endgame:
            if self.board.has_kingside_castling_rights(chess.WHITE):
                score += 30
            if self.board.has_queenside_castling_rights(chess.WHITE):
                score += 20
            if self.board.has_kingside_castling_rights(chess.BLACK):
                score -= 30
            if self.board.has_queenside_castling_rights(chess.BLACK):
                score -= 20

            white_king = self.board.king(chess.WHITE)
            black_king = self.board.king(chess.BLACK)

            if white_king is not None:
                file = chess.square_file(white_king)
                rank = chess.square_rank(white_king)
                for f in range(max(0, file - 1), min(7, file + 2)):
                    for r in range(rank + 1, min(rank + 3, 8)):
                        piece = self.board.piece_at(chess.square(f, r))
                        if piece and piece.piece_type == chess.PAWN and piece.color == chess.WHITE:
                            score += 10
                attackers = len(self.board.attackers(chess.BLACK, white_king))
                score -= 10 * attackers

            if black_king is not None:
                file = chess.square_file(black_king)
                rank = chess.square_rank(black_king)
                for f in range(max(0, file - 1), min(7, file + 2)):
                    for r in range(max(0, rank - 2), rank):
                        piece = self.board.piece_at(chess.square(f, r))
                        if piece and piece.piece_type == chess.PAWN and piece.color == chess.BLACK:
                            score -= 10
                attackers = len(self.board.attackers(chess.WHITE, black_king))
                score += 10 * attackers

        return score

    def _evaluate_mobility(self):
        original_turn = self.board.turn
        self.board.turn = chess.WHITE
        white_mobility = len(list(self.board.legal_moves))
        self.board.turn = chess.BLACK
        black_mobility = len(list(self.board.legal_moves))
        self.board.turn = original_turn
        return 2 * (white_mobility - black_mobility)

    def _is_endgame(self):
        total_material = sum(len(self.board.pieces(pt, c)) * self.piece_values[pt]
                            for pt in [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]
                            for c in [chess.WHITE, chess.BLACK])
        queens = len(self.board.pieces(chess.QUEEN, chess.WHITE)) + len(self.board.pieces(chess.QUEEN, chess.BLACK))
        return total_material < 2000 or queens == 0

    def get_board_evaluation(self):
        return self._evaluate_position()

    def set_depth(self, depth):
        self.depth = max(1, depth)
        self.killer_moves = [[] for _ in range(self.depth + 1)]

    def set_time_limit(self, seconds):
        self.time_limit = max(1, seconds)

    def _find_stockfish(self):
        current_dir = os.path.dirname(__file__)
        common_paths = [
            os.path.join(current_dir, 'stockfish'),
            os.path.join(current_dir, 'engines', 'stockfish')
        ]
        if platform.system() == 'Windows':
            common_paths.extend([
                os.path.join(current_dir, 'stockfish.exe'),
                os.path.join(current_dir, 'engines', 'stockfish.exe'),
                os.path.join(os.environ.get('ProgramFiles', 'C:\\Program Files'), 'Stockfish', 'stockfish.exe')
            ])
        elif platform.system() == 'Linux':
            stockfish_in_path = shutil.which('stockfish')
            if stockfish_in_path:
                return stockfish_in_path
            common_paths.extend(['/usr/games/stockfish', '/usr/local/bin/stockfish'])
        elif platform.system() == 'Darwin':
            common_paths.extend(['/usr/local/bin/stockfish', '/opt/homebrew/bin/stockfish'])

        for path in common_paths:
            if os.path.isfile(path) and os.access(path, os.X_OK):
                return path
        print("Stockfish not found. Using internal AI.")
        return None

    def _init_stockfish(self):
        if not self.stockfish_path:
            self.use_stockfish = False
            return False
        try:
            self.stockfish_process = subprocess.Popen(
                self.stockfish_path,
                universal_newlines=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=1
            )
            self._send_to_stockfish("uci")
            self._send_to_stockfish(f"setoption name Skill Level value {self.stockfish_strength}")
            self._send_to_stockfish("ucinewgame")
            self._send_to_stockfish("isready")
            while True:
                line = self.stockfish_process.stdout.readline().strip()
                if line == "readyok":
                    break
            return True
        except Exception as e:
            print(f"Error initializing Stockfish: {e}")
            self.use_stockfish = False
            return False

    def _send_to_stockfish(self, command):
        try:
            if self.stockfish_process and self.stockfish_process.stdin:
                self.stockfish_process.stdin.write(command + "\n")
                self.stockfish_process.stdin.flush()
        except Exception as e:
            print(f"Error sending command to Stockfish: {e}")
            self.use_stockfish = False

    def _get_stockfish_move(self, time_ms=1000):
        if not self.stockfish_process:
            return None
        try:
            self._send_to_stockfish(f"position fen {self.board.fen()}")
            self._send_to_stockfish(f"go movetime {time_ms}")
            best_move = None
            while True:
                line = self.stockfish_process.stdout.readline().strip()
                if line.startswith("bestmove"):
                    best_move = line.split()[1]
                    break
            return chess.Move.from_uci(best_move) if best_move else None
        except Exception as e:
            print(f"Error getting Stockfish move: {e}")
            return None

    def set_stockfish_strength(self, level):
        self.stockfish_strength = max(1, min(20, level))
        if self.stockfish_process:
            self._send_to_stockfish(f"setoption name Skill Level value {self.stockfish_strength}")

    def toggle_stockfish(self, use_stockfish):
        self.use_stockfish = use_stockfish
        if use_stockfish and not self.stockfish_process and self.stockfish_path:
            self._init_stockfish()

    def toggle_stockfish_opponent(self, enable):
        self.use_stockfish_as_opponent = enable
        if enable and not self.stockfish_process and self.stockfish_path:
            self._init_stockfish()