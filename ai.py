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

# Position tables (unchanged for brevity)
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
        self.killer_moves = {}  # Store killer moves for each depth
        self.nodes_searched = 0
        self.max_nodes = 1000000  # Limit to prevent freeze
        self.best_move_found = None
        self.eval_cache = {}

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
        self.killer_moves = {}
        self.eval_cache = {}

    def get_ai_move(self):
        if self.use_stockfish_as_opponent and self.board.turn == chess.BLACK:
            return self._get_stockfish_move(1000)
        else:
            return self._get_internal_ai_move()

    def _get_internal_ai_move(self):
        legal_moves = list(self.board.legal_moves)
        if not legal_moves:
            return None
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
        max_time = self.time_limit

        # Dynamic time management
        complexity_factor = min(1.5, 1 + len(legal_moves) / 20)
        max_time *= complexity_factor

        for current_depth in range(1, self.depth + 1):
            alpha = float('-inf')
            beta = float('inf')
            best_score = float('-inf')
            moves = self._order_moves(legal_moves, current_depth)

            for move in moves:
                self.board.push(move)
                score = -self._alpha_beta(current_depth - 1, -beta, -alpha, start_time, max_time)
                self.board.pop()

                if score > best_score:
                    best_score = score
                    self.best_move_found = move

                alpha = max(alpha, score)

                if time.time() - start_time > max_time or self.nodes_searched > self.max_nodes:
                    break

            print(f"Depth {current_depth}: Best move = {self.best_move_found}, Score = {best_score}")

            if time.time() - start_time > max_time or self.nodes_searched > self.max_nodes:
                print(f"Stopped at depth {current_depth} due to time or node limit")
                break

        elapsed_time = time.time() - start_time
        print(f"Searched {self.nodes_searched} nodes in {elapsed_time:.2f} seconds")

        if self.best_move_found is None and legal_moves:
            print("Warning: No best move found, selecting random move")
            self.best_move_found = random.choice(legal_moves)

        return self.best_move_found

    def __del__(self):
        if self.stockfish_process:
            self._send_to_stockfish("quit")
            self.stockfish_process.terminate()

    def _order_moves(self, moves, depth):
        scored_moves = []
        killer_move = self.killer_moves.get(depth, None)

        for move in moves:
            score = 0
            if move == killer_move:
                score += 1000  # Prioritize killer move
            if self.board.is_capture(move):
                victim_square = move.to_square
                victim_piece = self.board.piece_at(victim_square)
                if self.board.is_en_passant(move):
                    score += 10 * PAWN_VALUE
                elif victim_piece:
                    aggressor_piece = self.board.piece_at(move.from_square)
                    score += 10 * self.piece_values[victim_piece.piece_type] - self.piece_values[aggressor_piece.piece_type]
            if move.promotion:
                score += 900 if move.promotion == chess.QUEEN else 500
            self.board.push(move)
            if self.board.is_check():
                score += 100
            self.board.pop()
            if self.board.is_castling(move):
                score += 60
            scored_moves.append((move, score))

        scored_moves.sort(key=lambda x: x[1], reverse=True)
        return [move for move, _ in scored_moves]

    def _alpha_beta(self, depth, alpha, beta, start_time, max_time):
        self.nodes_searched += 1
        if self.nodes_searched > self.max_nodes or time.time() - start_time > max_time:
            return self._evaluate_position()  # Early exit

        board_hash = hash(self.board._transposition_key())
        tt_entry = self.transposition_table.get(board_hash)
        if tt_entry and tt_entry[0] >= depth:
            return tt_entry[1]

        if self.board.is_checkmate():
            return -10000 if self.board.turn else 10000
        if self.board.is_stalemate() or self.board.is_insufficient_material():
            return 0

        if depth <= 0:
            return self._quiescence_search(alpha, beta, start_time, max_time)

        moves = self._order_moves(list(self.board.legal_moves), depth)
        best_score = float('-inf')
        for move in moves:
            self.board.push(move)
            score = -self._alpha_beta(depth - 1, -beta, -alpha, start_time, max_time)
            self.board.pop()
            if score > best_score:
                best_score = score
                if score >= beta:
                    self.killer_moves[depth] = move  # Store killer move
            alpha = max(alpha, score)
            if alpha >= beta:
                break
        self.transposition_table[board_hash] = (depth, best_score)
        return best_score

    def _quiescence_search(self, alpha, beta, start_time, max_time, depth=0, max_depth=3):
        if depth >= max_depth or time.time() - start_time > max_time or self.nodes_searched > self.max_nodes:
            return self._evaluate_position()

        stand_pat = self._evaluate_position()
        if stand_pat >= beta:
            return beta
        if alpha < stand_pat:
            alpha = stand_pat

        moves = [m for m in self.board.legal_moves if self.board.is_capture(m) or self.board.gives_check(m)]
        moves = self._order_moves(moves, depth)
        for move in moves[:10]:  # Limit to top 10 moves to reduce computation
            self.board.push(move)
            score = -self._quiescence_search(-beta, -alpha, start_time, max_time, depth + 1, max_depth)
            self.board.pop()
            if score >= beta:
                return beta
            if score > alpha:
                alpha = score
        return alpha

    def _evaluate_position(self):
        board_hash = hash(self.board._transposition_key())
        if board_hash in self.eval_cache:
            return self.eval_cache[board_hash]

        if self.board.is_checkmate():
            score = -10000 if self.board.turn else 10000
        elif self.board.is_stalemate() or self.board.is_insufficient_material():
            score = 0
        else:
            score = 0
            is_endgame = self._is_endgame()
            for square in chess.SQUARES:
                piece = self.board.piece_at(square)
                if not piece:
                    continue
                value = self.piece_values[piece.piece_type]
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
                    position_value = KING_END_TABLE[square if piece.color else 63 - square] if is_endgame else KING_MIDDLE_TABLE[square if piece.color else 63 - square]
                score += (value + position_value) if piece.color == chess.WHITE else -(value + position_value)
            score += self._evaluate_center_control()
            score = score if self.board.turn == chess.WHITE else -score

        self.eval_cache[board_hash] = score
        return score

    def _evaluate_center_control(self):
        score = 0
        central_squares = [chess.D4, chess.E4, chess.D5, chess.E5]
        for square in central_squares:
            piece = self.board.piece_at(square)
            if piece:
                bonus = 10 if piece.piece_type in [chess.PAWN, chess.KNIGHT] else 5
                score += bonus if piece.color == chess.WHITE else -bonus
            score += 8 * len(self.board.attackers(chess.WHITE, square))
            score -= 8 * len(self.board.attackers(chess.BLACK, square))
        return score

    def _is_endgame(self):
        queens = len(self.board.pieces(chess.QUEEN, chess.WHITE)) + len(self.board.pieces(chess.QUEEN, chess.BLACK))
        rooks = len(self.board.pieces(chess.ROOK, chess.WHITE)) + len(self.board.pieces(chess.ROOK, chess.BLACK))
        total_pieces = queens + rooks + len(self.board.pieces(chess.KNIGHT, chess.WHITE)) + len(self.board.pieces(chess.KNIGHT, chess.BLACK)) + len(self.board.pieces(chess.BISHOP, chess.WHITE)) + len(self.board.pieces(chess.BISHOP, chess.BLACK))
        return queens == 0 or (queens + rooks <= 2 and total_pieces <= 6)

    def get_board_evaluation(self):
        return self._evaluate_position()

    def set_depth(self, depth):
        self.depth = max(1, depth)

    def set_time_limit(self, seconds):
        self.time_limit = max(1, seconds)

    def _find_stockfish(self):
        common_paths = []
        current_dir = os.path.dirname(__file__)
        common_paths.append(os.path.join(current_dir, 'stockfish'))
        common_paths.append(os.path.join(current_dir, 'engines', 'stockfish'))
        if platform.system() == 'Windows':
            common_paths.append(os.path.join(current_dir, 'stockfish.exe'))
            common_paths.append(os.path.join(current_dir, 'engines', 'stockfish.exe'))
            common_paths.append(os.path.join(current_dir, 'stockfish-windows-x86-64-avx2.exe'))
            common_paths.append(os.path.join(current_dir, 'engines', 'stockfish', 'stockfish-windows-x86-64-avx2.exe'))
            program_files = os.environ.get('ProgramFiles', 'C:\\Program Files')
            common_paths.append(os.path.join(program_files, 'Stockfish', 'stockfish.exe'))
            common_paths.append(os.path.join(program_files, 'Stockfish', 'stockfish-windows-x86-64-avx2.exe'))
        elif platform.system() == 'Linux':
            stockfish_in_path = shutil.which('stockfish')
            if stockfish_in_path:
                return stockfish_in_path
            common_paths.append('/usr/games/stockfish')
            common_paths.append('/usr/local/bin/stockfish')
        elif platform.system() == 'Darwin':
            common_paths.append('/usr/local/bin/stockfish')
            common_paths.append('/opt/homebrew/bin/stockfish')
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
        if self.stockfish_process and self.stockfish_process.stdin:
            self.stockfish_process.stdin.write(command + "\n")
            self.stockfish_process.stdin.flush()

    def _get_stockfish_move(self, time_ms=1000):
        if not self.stockfish_process:
            return None
        self._send_to_stockfish(f"position fen {self.board.fen()}")
        time_cmd = f"go movetime {time_ms}"
        self._send_to_stockfish(time_cmd)
        best_move = None
        while True:
            line = self.stockfish_process.stdout.readline().strip()
            if line.startswith("bestmove"):
                best_move = line.split()[1]
                break
        if best_move:
            try:
                return chess.Move.from_uci(best_move)
            except ValueError:
                print(f"Invalid Stockfish move format: {best_move}")
                return None
        return None

    def set_stockfish_strength(self, level):
        self.stockfish_strength = max(1, min(20, level))
        if self.stockfish_process:
            self._send_to_stockfish(f"setoption name Skill Level value {self.stockfish_strength}")
            self._send_to_stockfish("ucinewgame")

    def toggle_stockfish(self, use_stockfish):
        self.use_stockfish = use_stockfish
        if use_stockfish and not self.stockfish_process and self.stockfish_path:
            self._init_stockfish()

    def toggle_stockfish_opponent(self, enable):
        self.use_stockfish_as_opponent = enable
        if enable and not self.stockfish_process and self.stockfish_path:
            self._init_stockfish()