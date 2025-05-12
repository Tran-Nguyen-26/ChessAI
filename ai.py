import chess
import chess.polyglot
import sys
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
    0, 0, 0, 0, 0, 0, 0, 0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
    5, 5, 10, 25, 25, 10, 5, 5,
    0, 0, 0, 20, 20, 0, 0, 0,
    5, -5, -10, 0, 0, -10, -5, 5,
    5, 10, 10, -20, -20, 10, 10, 5,
    0, 0, 0, 0, 0, 0, 0, 0
]

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
    def __init__(self, depth=4, time_limit=10, opening_book_path="assets/books/komodo.bin"): # <--- Thêm opening_book_path
        self.depth = depth
        self.time_limit = time_limit
        self.board = chess.Board()
        self.transposition_table = {}
        self.history_table = {} # Thêm history_table nếu chưa có (đã có trong code bạn cung cấp)
        self.killer_moves = [[None, None] for _ in range(100)] # Khởi tạo killer_moves (đã có)
        self.nodes_searched = 0
        self.max_nodes = 1000000
        self.best_move_found = None
        self.eval_cache = {} # Mặc dù không thấy dùng trong code mới, giữ lại nếu cần
        self.stop_search = False # Thêm cờ này nếu chưa có (đã có)
        self.start_time = 0 # Khởi tạo self.start_time (đã có)


        # Flags for Stockfish usage, controlled by GUI
        self.use_stockfish_for_main_ai = False # Sẽ được set bởi toggle_stockfish
        self.use_stockfish_as_opponent = False # Sẽ được set bởi toggle_stockfish_opponent

        self.stockfish_path = self._find_stockfish()
        self.stockfish_process = None
        self.stockfish_strength = 10 # Default, GUI có thể thay đổi


        self.piece_values = {
            chess.PAWN: PAWN_VALUE,
            chess.KNIGHT: KNIGHT_VALUE,
            chess.BISHOP: BISHOP_VALUE,
            chess.ROOK: ROOK_VALUE,
            chess.QUEEN: QUEEN_VALUE,
            chess.KING: KING_VALUE
        }

        # --- Opening Book Integration ---
        self.opening_book_path = opening_book_path
        self.opening_book_reader = None
        self._load_opening_book()
        # --- End Opening Book Integration ---

        # Initialize Stockfish if path exists. Actual use depends on flags.
        if self.stockfish_path: # Chỉ _init_stockfish nếu self.stockfish_path tồn tại
             self._init_stockfish() # Không truyền self.use_stockfish nữa

    def _load_opening_book(self):
        """Loads the Polyglot opening book if available."""
        if not self.opening_book_path:
            print("AI (Internal): No opening book path specified. Opening book disabled.")
            self.opening_book_reader = None
            return

        book_file_to_try = self.opening_book_path
        if not os.path.isabs(book_file_to_try):
            try:
                # sys.argv[0] is the path to the currently running script (main.py)
                script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
                book_file_to_try = os.path.join(script_dir, self.opening_book_path)
            except Exception as e:
                print(
                    f"AI (Internal): Error determining script directory for opening book: {e}. Using provided path directly.")
                # book_file_to_try remains self.opening_book_path

        if not os.path.exists(book_file_to_try):
            print(f"AI (Internal): Opening book file not found at '{book_file_to_try}'. Opening book disabled.")
            self.opening_book_reader = None
            return

        try:
            self.opening_book_reader = chess.polyglot.open_reader(book_file_to_try)
            print(f"AI (Internal): Successfully loaded opening book: {book_file_to_try}")
        except AttributeError:
            print("AI (Internal): Error loading opening book. 'chess.polyglot' not found. "
                  "Please ensure 'python-chess' library is installed correctly and up-to-date (pip install --upgrade python-chess).")
            self.opening_book_reader = None
        except Exception as e:
            print(f"AI (Internal): Error loading opening book '{book_file_to_try}': {e}")
            self.opening_book_reader = None

    def reset_board(self):
        """Reset the board to starting position"""
        self.board = chess.Board()
        self.transposition_table = {}
        self.history_table = {}
        self.killer_moves = [[None, None] for _ in range(100)]
        # Reset Stockfish for a new game if it's running
        if self.stockfish_process:
            self._send_to_stockfish("ucinewgame")
            self._send_to_stockfish("isready")
            # Wait for readyok
            output_lines = []  # To prevent infinite loop if SF crashes
            max_wait_lines = 20
            lines_read = 0
            while True:
                if not self.stockfish_process or not self.stockfish_process.stdout or lines_read > max_wait_lines:
                    break
                line = self.stockfish_process.stdout.readline().strip()
                lines_read += 1
                if line == "readyok":
                    break
                if not line and self.stockfish_process.poll() is not None:
                    print("AI: Stockfish process ended unexpectedly during reset_board's readyok wait.")
                    # self._init_stockfish() # Optionally try to restart
                    break
                output_lines.append(line)

    def get_ai_move(self):
        # Logic for determining which AI to use (Stockfish opponent, Stockfish main AI, or Internal AI)
        if self.use_stockfish_as_opponent and self.board.turn == chess.BLACK:
            print("AI: Getting move from Stockfish (opponent)...")
            if not self.stockfish_process and self.stockfish_path: self._init_stockfish()
            if self.stockfish_process:
                self._send_to_stockfish(f"setoption name Skill Level value {self.stockfish_strength}")
                return self._get_stockfish_move(time_ms=1000)
            else:
                print("AI: Stockfish opponent not available, internal AI will play for Black (fallback).")
                return self._get_internal_ai_move() # Internal AI plays

        elif self.use_stockfish_for_main_ai:
            print(f"AI: Getting move from Stockfish (main engine, strength {self.stockfish_strength})...")
            if not self.stockfish_process and self.stockfish_path: self._init_stockfish()
            if self.stockfish_process:
                self._send_to_stockfish(f"setoption name Skill Level value {self.stockfish_strength}")
                thinking_time_ms = 50 + self.stockfish_strength * 50
                thinking_time_ms = min(max(thinking_time_ms, 50), 3000) # Cap at 3s for SF main
                move = self._get_stockfish_move(time_ms=thinking_time_ms)
                if move:
                    # print(f"AI: Stockfish (main engine) move: {self.board.san(move)}") # SAN can be slow
                    print(f"AI: Stockfish (main engine) move: {move.uci()}")
                    return move
                else:
                    print("AI: Stockfish (main engine) failed. Falling back to internal AI.")
                    return self._get_internal_ai_move()
            else:
                print("AI: Stockfish (main engine) not available. Falling back to internal AI.")
                return self._get_internal_ai_move()
        else:
            print("AI: Getting move from Internal AI (Minimax)...")
            return self._get_internal_ai_move()

    def _get_internal_ai_move(self):
        self.nodes_searched = 0
        self.start_time = time.time()  # Ensure start_time is set for each internal AI move
        self.best_move_found = None
        self.stop_search = False

        # 1. Check Polyglot opening book first for Internal AI
        if self.opening_book_reader:
            try:
                # Use weighted_choice for a more natural selection from book
                entry = self.opening_book_reader.weighted_choice(self.board)
                if entry:
                    book_move = entry.move
                    # Crucial: Verify the book move is legal in the current position
                    if book_move in self.board.legal_moves:
                        print(f"AI (Internal): Using opening book move: {book_move.uci()}")
                        return book_move
                    else:
                        print(f"AI (Internal): Book move {book_move.uci()} is illegal. Proceeding with search.")
            except IndexError:  # Can happen if position not in book or no weighted moves
                print("AI (Internal): Position not in opening book or no suitable book move.")
            except Exception as e:
                print(f"AI (Internal): Error accessing opening book: {e}")
        # End of opening book check for Internal AI

        legal_moves = list(self.board.legal_moves)
        if not legal_moves:  # No legal moves, game should be over
            return None
        if len(legal_moves) == 1:
            return legal_moves[0]

        if legal_moves:  # Initialize best_move_found to prevent None if search times out early
            self.best_move_found = legal_moves[0]

        max_depth = self._calculate_adaptive_depth()
        print(f"AI (Internal): Calculated adaptive depth: {max_depth}")

        for current_depth in range(1, max_depth + 1):
            # print(f"AI (Internal): Starting search at depth {current_depth}") # Optional detailed log
            self._search_with_iterative_deepening(current_depth)

            if self.stop_search or (
                    time.time() - self.start_time > self.time_limit * 0.95):  # Check time more frequently
                print(f"AI (Internal): Time limit approaching/reached or search stopped after depth {current_depth}")
                break

        elapsed_time = time.time() - self.start_time
        print(
            f"AI (Internal): Searched {self.nodes_searched} nodes in {elapsed_time:.2f} seconds to depth {current_depth if 'current_depth' in locals() else 'N/A'}.")

        if self.best_move_found is None and legal_moves:
            print(
                "AI (Internal): Warning: No best move found by search, selecting random move (likely due to early timeout).")
            self.best_move_found = random.choice(legal_moves)

        # print(f"AI (Internal): Final best move: {self.best_move_found.uci() if self.best_move_found else 'None'}")
        return self.best_move_found

    def _check_opening_book(self):
        # Lấy trạng thái bàn cờ dưới dạng chuỗi FEN
        fen = self.board.fen()
        # Kiểm trạng thái có trong từ điển opening_book không
        if fen in self.opening_book:
            return chess.Move.from_uci(
                random.choice(self.opening_book[fen]))  # Trả về các nước đi ngẫu nhiên opening_book

        # Tạo một chuỗi FEN đơn giản hóa từ chuỗi FEN đầy đủ.
        simplified_fen = ' '.join(fen.split(' ')[:2])
        for book_fen in self.opening_book:
            if book_fen.startswith(simplified_fen):
                return chess.Move.from_uci(random.choice(self.opening_book[book_fen]))

        return None

    def __del__(self):
        if self.stockfish_process:
            try:
                self._send_to_stockfish("quit")
                self.stockfish_process.terminate()
                self.stockfish_process.wait(timeout=1)  # Wait for termination
                print("AI: Stockfish process terminated.")
            except Exception as e:
                print(f"AI: Error terminating Stockfish: {e}")

        if self.opening_book_reader:  # <--- THÊM ĐÓNG SÁCH KHAI CUỘC
            try:
                self.opening_book_reader.close()
                print("AI: Opening book closed.")
            except Exception as e:
                print(f"AI: Error closing opening book: {e}")

    def _check_opening_book(self):
        # Lấy trạng thái bàn cờ dưới dạng chuỗi FEN
        fen = self.board.fen()
        # Kiểm trạng thái có trong từ điển opening_book không
        if fen in self.opening_book:
            return chess.Move.from_uci(
                random.choice(self.opening_book[fen]))  # Trả về các nước đi ngẫu nhiên opening_book

        # Tạo một chuỗi FEN đơn giản hóa từ chuỗi FEN đầy đủ.
        simplified_fen = ' '.join(fen.split(' ')[:2])
        for book_fen in self.opening_book:
            if book_fen.startswith(simplified_fen):
                return chess.Move.from_uci(random.choice(self.opening_book[book_fen]))

        return None

    def _calculate_adaptive_depth(self):
        """Calculate adaptive search depth based on position complexity"""
        base_depth = self.depth
        total_pieces = sum(1 for _ in self.board.piece_map())
        if total_pieces <= 10:  # Endgame
            return min(base_depth + 2, 7) # Capped max depth for endgame to 7 for performance
        elif total_pieces <= 20:  # Late middlegame
            return min(base_depth + 1, 6) # Capped max depth for midgame
        else:
            return base_depth # Max depth in opening/early midgame based on self.depth

    def _search_with_iterative_deepening(self, depth):
        alpha = float('-inf')
        beta = float('inf')
        # best_score_at_this_depth = float('-inf') # Không cần thiết vì self.best_move_found được cập nhật trực tiếp

        # Aspiration window logic
        aspiration_window_active = False
        if depth >= 3 and self.best_move_found:  # Chỉ dùng aspiration nếu đã có best_move từ độ sâu trước
            prev_eval = self._get_stored_evaluation()  # Lấy eval của thế cờ, không phải của nước đi
            if prev_eval != float('-inf'):  # Đổi điều kiện từ float('inf') sang float('-inf') cho eval
                window = 50  # Initial window size
                current_alpha, current_beta = prev_eval - window, prev_eval + window
                # print(f"Depth {depth}: Trying aspiration window [{current_alpha}, {current_beta}] based on prev_eval {prev_eval}")

                # Important: self.best_move_found will be updated inside _alpha_beta if a better move is found
                score = self._alpha_beta(depth, current_alpha, current_beta, 0, True)

                if score <= current_alpha or score >= current_beta:  # Search failed high or low
                    # print(f"Depth {depth}: Aspiration search failed (score {score}). Re-searching with full window.")
                    # Reset alpha/beta for full search
                    alpha = float('-inf')
                    beta = float('inf')
                    score = self._alpha_beta(depth, alpha, beta, 0, True)
                # else:
                # print(f"Depth {depth}: Aspiration search successful (score {score}).")

                # best_score_at_this_depth = score # Cập nhật điểm số tốt nhất ở độ sâu này
                aspiration_window_active = True

        if not aspiration_window_active:  # Nếu aspiration không được dùng hoặc thất bại và cần full search
            score = self._alpha_beta(depth, alpha, beta, 0, True)
            # best_score_at_this_depth = score

        # self.best_move_found đã được cập nhật trong _alpha_beta(is_root=True)
        if self.best_move_found:  # Chỉ in nếu tìm được nước đi
            # print(f"AI (Internal) Depth {depth}: Best move so far = {self.best_move_found.uci()}, Score = {best_score_at_this_depth}")
            pass  # Ít log hơn

        # self._store_evaluation(best_score_at_this_depth) # Lưu trữ đánh giá của thế cờ
        # Nên là eval của root node, không phải của move
        # _alpha_beta nên trả về eval của board
        # và _store_evaluation nên lưu eval đó với board_hash hiện tại

    def _get_stored_evaluation(self):
        """Get stored evaluation for current position"""
        board_hash = hash(self.board._transposition_key())
        if board_hash in self.transposition_table:
            return self.transposition_table[board_hash][1]
        return float('inf')

    def _store_evaluation(self, score):
        """Store evaluation for aspiration window"""
        board_hash = hash(self.board._transposition_key())
        if board_hash not in self.transposition_table:
            self.transposition_table[board_hash] = (0, score)

    def _order_moves(self, moves, depth):
        """Enhanced move ordering for better alpha-beta efficiency"""
        scored_moves = []
        tt_move = self._get_tt_move()

        for move in moves:
            score = 0

            # 1. Prioritize transposition table move
            if tt_move and move == tt_move:
                score += 10000

            # 2. Prioritize captures by MVV-LVA (Most Valuable Victim - Least Valuable Aggressor)
            if self.board.is_capture(move):
                victim_square = move.to_square
                victim_piece = self.board.piece_at(victim_square)

                # Handle en passant captures
                if self.board.is_en_passant(move):
                    score += 10 * PAWN_VALUE
                elif victim_piece:
                    aggressor_piece = self.board.piece_at(move.from_square)
                    score += 10 * self.piece_values[victim_piece.piece_type] - self.piece_values[
                        aggressor_piece.piece_type]

            # 3. Prioritize promotions
            if move.promotion:
                score += 900 if move.promotion == chess.QUEEN else 500

            # 4. Killer move heuristic (quiet moves that cause beta cutoffs)
            if self.killer_moves[depth][0] == move:
                score += 80
            elif self.killer_moves[depth][1] == move:
                score += 70

            # 5. History heuristic (moves that have been good in the past)
            if str(move) in self.history_table:
                score += min(self.history_table[str(move)], 60)  # Cap to avoid overriding captures

            # 6. Prioritize checks
            self.board.push(move)
            if self.board.is_check():
                score += 50
            self.board.pop()

            # 7. Prioritize castling
            if self.board.is_castling(move):
                score += 60

            # 8. Piece development in opening
            if self._is_opening():
                from_square = move.from_square
                piece = self.board.piece_at(from_square)
                if piece and piece.piece_type in [chess.KNIGHT, chess.BISHOP] and chess.square_rank(from_square) in [0,
                                                                                                                     7]:
                    score += 30  # Develop minor pieces

                # Control center with pawns
                if piece and piece.piece_type == chess.PAWN:
                    to_square = move.to_square
                    to_file = chess.square_file(to_square)
                    to_rank = chess.square_rank(to_square)

                    # Center control
                    if (to_file in [3, 4] and to_rank in [3, 4]):
                        score += 25

            scored_moves.append((move, score))

        # Sort moves by score in descending order
        scored_moves.sort(key=lambda x: x[1], reverse=True)
        return [move for move, _ in scored_moves]

    def _get_tt_move(self):
        """Get the best move from transposition table"""
        board_hash = hash(self.board._transposition_key())
        if board_hash in self.transposition_table and len(self.transposition_table[board_hash]) > 2:
            return self.transposition_table[board_hash][2]  # Return the stored best move
        return None

    def _is_opening(self):
        """Check if the game is in opening phase"""
        # Simple check based on move number and pieces developed
        return self.board.fullmove_number < 10 and len(self.board.piece_map()) >= 28

    def _alpha_beta(self, depth, alpha, beta, ply, is_root=False):
        """Enhanced alpha-beta pruning with PVS (Principal Variation Search)"""
        self.nodes_searched += 1

        # Check time periodically
        if self.nodes_searched % 1000 == 0 and time.time() - self.start_time > self.time_limit * 0.8:
            self.stop_search = True
            return 0

        # Check transposition table
        board_hash = hash(self.board._transposition_key())
        alpha_orig = alpha

        if board_hash in self.transposition_table and self.transposition_table[board_hash][0] >= depth:
            tt_entry = self.transposition_table[board_hash]
            tt_value = tt_entry[1]
            tt_flag = tt_entry[3] if len(tt_entry) > 3 else None

            if tt_flag == 'EXACT':
                return tt_value
            elif tt_flag == 'LOWERBOUND':
                alpha = max(alpha, tt_value)
            elif tt_flag == 'UPPERBOUND':
                beta = min(beta, tt_value)

            if alpha >= beta:
                return tt_value

        # Check terminal states
        if self.board.is_checkmate():
            return -10000 + ply if self.board.turn else 10000 - ply  # Prefer faster checkmate
        if self.board.is_stalemate() or self.board.is_insufficient_material() or self.board.is_fifty_moves():
            return 0

        # Quiescence search at leaf nodes to handle horizon effect
        if depth <= 0:
            return self._quiescence_search(alpha, beta)

        # Check for draw by repetition
        if self.board.is_repetition(2):  # 2-fold repetition
            return 0

        # Generate and order moves
        moves = self._order_moves(list(self.board.legal_moves), ply)

        if not moves:
            return 0  # No legal moves, but not checkmate or stalemate (should never happen)

        best_score = float('-inf')
        best_move = None

        # Principal Variation Search
        for i, move in enumerate(moves):
            self.board.push(move)

            # First move is searched with full window
            if i == 0:
                score = -self._alpha_beta(depth - 1, -beta, -alpha, ply + 1)
            else:
                # Search with null window to prove this move is worse
                score = -self._alpha_beta(depth - 1, -alpha - 1, -alpha, ply + 1)
                # If the move might be better than our current best, do a full search
                if alpha < score < beta:
                    score = -self._alpha_beta(depth - 1, -beta, -alpha, ply + 1)

            self.board.pop()

            if self.stop_search:
                return 0

            if score > best_score:
                best_score = score
                best_move = move

                if is_root:
                    self.best_move_found = move

            alpha = max(alpha, score)
            if alpha >= beta:
                # Update killer moves (non-captures that cause cutoffs)
                if not self.board.is_capture(move):
                    if self.killer_moves[ply][0] != move:
                        self.killer_moves[ply][1] = self.killer_moves[ply][0]
                        self.killer_moves[ply][0] = move

                # Update history table
                if str(move) not in self.history_table:
                    self.history_table[str(move)] = 0
                self.history_table[str(move)] += depth * depth

                break  # Beta cutoff

        # Store result in transposition table
        tt_flag = 'EXACT'
        if best_score <= alpha_orig:
            tt_flag = 'UPPERBOUND'
        elif best_score >= beta:
            tt_flag = 'LOWERBOUND'

        self.transposition_table[board_hash] = (depth, best_score, best_move, tt_flag)
        return best_score

    def _quiescence_search(self, alpha, beta, depth=0, max_depth=4):
        """Enhanced quiescence search to evaluate only quiet positions"""
        self.nodes_searched += 1

        # Check periodically if we should stop
        if self.nodes_searched % 1000 == 0 and time.time() - self.start_time > self.time_limit * 0.8:
            self.stop_search = True
            return 0

        # Prevent excessive depth in quiescence search
        if depth >= max_depth:
            return self._evaluate_position()

        stand_pat = self._evaluate_position()

        # Delta pruning - if even capturing the most valuable piece wouldn't improve alpha
        if stand_pat >= beta:
            return beta

        # Improve alpha with stand_pat
        if stand_pat > alpha:
            alpha = stand_pat

        # Look at captures only
        captures = [move for move in self.board.legal_moves if self.board.is_capture(move)]
        captures = self._order_moves(captures, depth)

        # Also consider checks in quiescence to avoid missing tactical opportunities
        if depth < 2:  # Limit depth for check extensions to avoid explosion
            for move in self.board.legal_moves:
                if not self.board.is_capture(move):
                    self.board.push(move)
                    is_check = self.board.is_check()
                    self.board.pop()
                    if is_check:
                        captures.append(move)

        for move in captures:
            self.board.push(move)
            score = -self._quiescence_search(-beta, -alpha, depth + 1, max_depth)
            self.board.pop()

            if self.stop_search:
                return 0

            if score >= beta:
                return beta
            if score > alpha:
                alpha = score

        return alpha

    def _evaluate_position(self):
        """Enhanced position evaluation with multiple factors"""
        if self.board.is_checkmate():
            return -10000 if self.board.turn else 10000

        if self.board.is_stalemate() or self.board.is_insufficient_material():
            return 0  # Draw

        material_score = self._evaluate_material()
        position_score = self._evaluate_piece_positioning()
        pawn_structure_score = self._evaluate_pawn_structure()
        mobility_score = self._evaluate_mobility()
        king_safety_score = self._evaluate_king_safety()
        attack_score = self._evaluate_attack_potential()

        # Combine all evaluation components
        total_score = (
                material_score +
                position_score +
                pawn_structure_score +
                mobility_score +
                king_safety_score +
                attack_score
        )

        # Return score from current player's perspective
        return total_score if self.board.turn == chess.WHITE else -total_score

    def _evaluate_material(self):
        """Evaluate material balance with piece values"""
        score = 0

        # Material counting
        for piece_type in [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING]:
            score += len(self.board.pieces(piece_type, chess.WHITE)) * self.piece_values[piece_type]
            score -= len(self.board.pieces(piece_type, chess.BLACK)) * self.piece_values[piece_type]

        # Bishop pair bonus
        if len(self.board.pieces(chess.BISHOP, chess.WHITE)) >= 2:
            score += 50
        if len(self.board.pieces(chess.BISHOP, chess.BLACK)) >= 2:
            score -= 50

        return score

    def _evaluate_piece_positioning(self):
        """Evaluate piece positioning using piece-square tables"""
        score = 0
        is_endgame = self._is_endgame()

        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if not piece:
                continue

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
                score += position_value
            else:
                score -= position_value

        return score

    def _evaluate_pawn_structure(self):
        """Enhanced pawn structure evaluation"""
        score = 0

        white_pawns = self.board.pieces(chess.PAWN, chess.WHITE)
        black_pawns = self.board.pieces(chess.PAWN, chess.BLACK)

        # Passed pawns
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
                # More value for advanced passed pawns - exponential bonus
                score += 20 + (rank * rank * 2)

                # Check if the passed pawn is supported
                if rank > 0:
                    for support_file in [max(0, file - 1), min(7, file + 1)]:
                        support_square = chess.square(support_file, rank - 1)
                        if support_square in white_pawns:
                            score += 10  # Bonus for supported passed pawns

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
                # More value for advanced passed pawns - exponential bonus
                score -= 20 + ((7 - rank) * (7 - rank) * 2)

                # Check if the passed pawn is supported
                if rank < 7:
                    for support_file in [max(0, file - 1), min(7, file + 1)]:
                        support_square = chess.square(support_file, rank + 1)
                        if support_square in black_pawns:
                            score -= 10  # Bonus for supported passed pawns

        # Doubled pawns
        for file_num in range(8):
            file_mask = chess.BB_FILES[file_num]

            white_pawns_in_file = len(white_pawns & chess.SquareSet(file_mask))
            black_pawns_in_file = len(black_pawns & chess.SquareSet(file_mask))

            if white_pawns_in_file > 1:
                score -= 15 * (white_pawns_in_file - 1)  # Penalty for doubled pawns
            if black_pawns_in_file > 1:
                score += 15 * (black_pawns_in_file - 1)  # Penalty for doubled pawns

        # Isolated pawns
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
                score -= 20  # Penalty for isolated pawns

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
                score += 20  # Penalty for isolated pawns

        # Backward pawns detection
        for square in white_pawns:
            file_num = chess.square_file(square)
            rank = chess.square_rank(square)
            is_backward = False

            # Check if adjacent files have pawns more advanced
            left_file = max(0, file_num - 1)
            right_file = min(7, file_num + 1)

            # Is there any pawn on adjacent files more advanced?
            more_advanced_adjacent = False
            for f in [left_file, right_file]:
                for r in range(rank + 1, 8):
                    if chess.square(f, r) in white_pawns:
                        more_advanced_adjacent = True
                        break

            # Can this pawn be safely advanced?
            can_advance = True
            if rank < 7:
                advance_square = chess.square(file_num, rank + 1)
                if self.board.piece_at(advance_square):  # Square is blocked
                    can_advance = False
                else:
                    # Check if square is attacked by enemy pawns
                    for f in [max(0, file_num - 1), min(7, file_num + 1)]:
                        if rank + 2 < 8 and chess.square(f, rank + 2) in black_pawns:
                            can_advance = False
                            break

            if more_advanced_adjacent and not can_advance:
                score -= 10  # Penalty for backward pawns

        for square in black_pawns:
            file_num = chess.square_file(square)
            rank = chess.square_rank(square)
            is_backward = False

            # Check if adjacent files have pawns more advanced
            left_file = max(0, file_num - 1)
            right_file = min(7, file_num + 1)

            # Is there any pawn on adjacent files more advanced?
            more_advanced_adjacent = False
            for f in [left_file, right_file]:
                for r in range(0, rank):
                    if chess.square(f, r) in black_pawns:
                        more_advanced_adjacent = True
                        break

            # Can this pawn be safely advanced?
            can_advance = True
            if rank > 0:
                advance_square = chess.square(file_num, rank - 1)
                if self.board.piece_at(advance_square):  # Square is blocked
                    can_advance = False
                else:
                    # Check if square is attacked by enemy pawns
                    for f in [max(0, file_num - 1), min(7, file_num + 1)]:
                        if rank - 2 >= 0 and chess.square(f, rank - 2) in white_pawns:
                            can_advance = False
                            break

            if more_advanced_adjacent and not can_advance:
                score += 10  # Penalty for backward pawns

        # Pawn chains
        for square in white_pawns:
            file_num = chess.square_file(square)
            rank = chess.square_rank(square)

            # Check for defending pawns
            if file_num > 0 and rank > 0:
                if chess.square(file_num - 1, rank - 1) in white_pawns:
                    score += 5  # Bonus for pawn chains

            if file_num < 7 and rank > 0:
                if chess.square(file_num + 1, rank - 1) in white_pawns:
                    score += 5  # Bonus for pawn chains

        for square in black_pawns:
            file_num = chess.square_file(square)
            rank = chess.square_rank(square)

            # Check for defending pawns
            if file_num > 0 and rank < 7:
                if chess.square(file_num - 1, rank + 1) in black_pawns:
                    score -= 5  # Bonus for pawn chains

            if file_num < 7 and rank < 7:
                if chess.square(file_num + 1, rank + 1) in black_pawns:
                    score -= 5  # Bonus for pawn chains

        return score

    def _evaluate_mobility(self):
        """Evaluate piece mobility with improved weights"""
        original_turn = self.board.turn
        score = 0

        # Evaluate white mobility
        self.board.turn = chess.WHITE
        white_moves = list(self.board.legal_moves)
        white_mobility = len(white_moves)

        # Get only quiet moves (non-captures)
        white_quiet_moves = sum(1 for move in white_moves if not self.board.is_capture(move))

        # Evaluate black mobility
        self.board.turn = chess.BLACK
        black_moves = list(self.board.legal_moves)
        black_mobility = len(black_moves)

        # Get only quiet moves (non-captures)
        black_quiet_moves = sum(1 for move in black_moves if not self.board.is_capture(move))

        # Restore original turn
        self.board.turn = original_turn

        # Quiet moves are weighted less than total mobility
        mobility_score = 2 * (white_mobility - black_mobility) + (white_quiet_moves - black_quiet_moves)

        # Add check/checkmate threat bonus
        if self.board.is_check():
            if self.board.turn == chess.WHITE:
                score -= 50  # White is in check
            else:
                score += 50  # Black is in check

        return score + mobility_score

    def _evaluate_king_safety(self):
        """Enhanced king safety evaluation"""
        score = 0
        is_endgame = self._is_endgame()

        if not is_endgame:
            # Castling rights evaluation
            if self.board.has_kingside_castling_rights(chess.WHITE):
                score += 40
            if self.board.has_queenside_castling_rights(chess.WHITE):
                score += 30
            if self.board.has_kingside_castling_rights(chess.BLACK):
                score -= 40
            if self.board.has_queenside_castling_rights(chess.BLACK):
                score -= 30

            # Has already castled bonus (detect by king position)
            white_king = self.board.king(chess.WHITE)
            if white_king is not None:
                wk_file = chess.square_file(white_king)
                wk_rank = chess.square_rank(white_king)
                if wk_rank == 0:
                    if wk_file in [6, 7]:  # King-side castled
                        score += 60
                    elif wk_file in [0, 1, 2]:  # Queen-side castled
                        score += 50

            black_king = self.board.king(chess.BLACK)
            if black_king is not None:
                bk_file = chess.square_file(black_king)
                bk_rank = chess.square_rank(black_king)
                if bk_rank == 7:
                    if bk_file in [6, 7]:  # King-side castled
                        score -= 60
                    elif bk_file in [0, 1, 2]:  # Queen-side castled
                        score -= 50

            # King pawn shield - weighted by distance
            if white_king is not None:
                wk_file = chess.square_file(white_king)
                wk_rank = chess.square_rank(white_king)

                # Define pawn shield area (depends on castle side)
                shield_files = []
                if wk_file < 3:  # Queenside castle
                    shield_files = [max(0, wk_file - 1), wk_file, wk_file + 1]
                elif wk_file > 4:  # Kingside castle
                    shield_files = [wk_file - 1, wk_file, min(7, wk_file + 1)]
                else:  # Middle (not castled or e-file)
                    shield_files = [max(0, wk_file - 1), wk_file, min(7, wk_file + 1)]

                # Check pawns in shield area
                for f in shield_files:
                    for r in range(wk_rank + 1, min(wk_rank + 3, 8)):
                        square = chess.square(f, r)
                        piece = self.board.piece_at(square)
                        if piece and piece.piece_type == chess.PAWN and piece.color == chess.WHITE:
                            # Closer pawns are more valuable
                            distance = abs(r - wk_rank) + abs(f - wk_file)
                            score += max(15 - 5 * distance, 5)

            if black_king is not None:
                bk_file = chess.square_file(black_king)
                bk_rank = chess.square_rank(black_king)

                # Define pawn shield area (depends on castle side)
                shield_files = []
                if bk_file < 3:  # Queenside castle
                    shield_files = [max(0, bk_file - 1), bk_file, bk_file + 1]
                elif bk_file > 4:  # Kingside castle
                    shield_files = [bk_file - 1, bk_file, min(7, bk_file + 1)]
                else:  # Middle (not castled or e-file)
                    shield_files = [max(0, bk_file - 1), bk_file, min(7, bk_file + 1)]

                # Check pawns in shield area
                for f in shield_files:
                    for r in range(max(0, bk_rank - 2), bk_rank):
                        square = chess.square(f, r)
                        piece = self.board.piece_at(square)
                        if piece and piece.piece_type == chess.PAWN and piece.color == chess.BLACK:
                            # Closer pawns are more valuable
                            distance = abs(r - bk_rank) + abs(f - bk_file)
                            score -= max(15 - 5 * distance, 5)

            # King attack zone and safety
            if white_king is not None:
                attack_zone = self._get_king_attack_zone(white_king)
                black_attackers = 0
                attacker_weight = 0

                for square in attack_zone:
                    attackers = self.board.attackers(chess.BLACK, square)
                    black_attackers += len(attackers)

                    # Weight attackers by piece type
                    for attacker_square in attackers:
                        piece = self.board.piece_at(attacker_square)
                        if piece.piece_type == chess.QUEEN:
                            attacker_weight += 4
                        elif piece.piece_type == chess.ROOK:
                            attacker_weight += 3
                        elif piece.piece_type in [chess.BISHOP, chess.KNIGHT]:
                            attacker_weight += 2
                        else:  # Pawn
                            attacker_weight += 1

                # Safety penalty increases dramatically with more attackers
                safety_penalty = 0
                if black_attackers > 0:
                    # More attackers = exponentially worse
                    safety_penalty = 5 * black_attackers + 5 * attacker_weight
                    if black_attackers >= 2:
                        safety_penalty *= 2
                    if black_attackers >= 3:
                        safety_penalty = int(safety_penalty * 1.5)

                score -= safety_penalty

            if black_king is not None:
                attack_zone = self._get_king_attack_zone(black_king)
                white_attackers = 0
                attacker_weight = 0

                for square in attack_zone:
                    attackers = self.board.attackers(chess.WHITE, square)
                    white_attackers += len(attackers)

                    # Weight attackers by piece type
                    for attacker_square in attackers:
                        piece = self.board.piece_at(attacker_square)
                        if piece.piece_type == chess.QUEEN:
                            attacker_weight += 4
                        elif piece.piece_type == chess.ROOK:
                            attacker_weight += 3
                        elif piece.piece_type in [chess.BISHOP, chess.KNIGHT]:
                            attacker_weight += 2
                        else:  # Pawn
                            attacker_weight += 1

                # Safety penalty increases dramatically with more attackers
                safety_penalty = 0
                if white_attackers > 0:
                    # More attackers = exponentially worse
                    safety_penalty = 5 * white_attackers + 5 * attacker_weight
                    if white_attackers >= 2:
                        safety_penalty *= 2
                    if white_attackers >= 3:
                        safety_penalty = int(safety_penalty * 1.5)

                score += safety_penalty
        else:
            # In endgame, kings should be more active
            white_king = self.board.king(chess.WHITE)
            black_king = self.board.king(chess.BLACK)

            if white_king is not None and black_king is not None:
                # Center manhattan distance for kings in endgame
                wk_file = chess.square_file(white_king)
                wk_rank = chess.square_rank(white_king)
                bk_file = chess.square_file(black_king)
                bk_rank = chess.square_rank(black_king)

                # Distance to center (lower is better)
                white_center_dist = abs(3.5 - wk_file) + abs(3.5 - wk_rank)
                black_center_dist = abs(3.5 - bk_file) + abs(3.5 - bk_rank)

                # In endgame, active king is good
                score += 10 * (black_center_dist - white_center_dist)

                # King opposition
                kings_file_distance = abs(wk_file - bk_file)
                kings_rank_distance = abs(wk_rank - bk_rank)
                kings_distance = kings_file_distance + kings_rank_distance

                # Kings' opposition in endgame
                if kings_distance == 2 and ((kings_file_distance == 0) or (kings_rank_distance == 0)):
                    if self.board.turn == chess.WHITE:
                        score += 20  # White has the opposition
                    else:
                        score -= 20  # Black has the opposition

        return score

    def _get_king_attack_zone(self, king_square):
        """Get expanded attack zone around the king"""
        attack_zone = set()
        king_file = chess.square_file(king_square)
        king_rank = chess.square_rank(king_square)

        # Two-square radius around king
        for f in range(max(0, king_file - 2), min(8, king_file + 3)):
            for r in range(max(0, king_rank - 2), min(8, king_rank + 3)):
                square = chess.square(f, r)
                if square != king_square:
                    attack_zone.add(square)

        return attack_zone

    def _evaluate_attack_potential(self):
        """Evaluate piece coordination and attack potential"""
        score = 0

        # Center control (d4, d5, e4, e5)
        central_squares = [chess.D4, chess.E4, chess.D5, chess.E5]
        for square in central_squares:
            # Count attackers of each color
            white_attackers = len(self.board.attackers(chess.WHITE, square))
            black_attackers = len(self.board.attackers(chess.BLACK, square))
            score += 10 * (white_attackers - black_attackers)

        # Extended center control
        extended_center = [
            chess.C3, chess.D3, chess.E3, chess.F3,
            chess.C4, chess.F4, chess.C5, chess.F5,
            chess.C6, chess.D6, chess.E6, chess.F6
        ]
        for square in extended_center:
            white_attackers = len(self.board.attackers(chess.WHITE, square))
            black_attackers = len(self.board.attackers(chess.BLACK, square))
            score += 5 * (white_attackers - black_attackers)

        # Development advantage in opening
        if self._is_opening():
            white_development = 0
            black_development = 0

            # Count developed minor pieces (knights and bishops)
            white_knights = self.board.pieces(chess.KNIGHT, chess.WHITE)
            black_knights = self.board.pieces(chess.KNIGHT, chess.BLACK)
            white_bishops = self.board.pieces(chess.BISHOP, chess.WHITE)
            black_bishops = self.board.pieces(chess.BISHOP, chess.BLACK)

            # Check if knights moved from starting squares
            if not chess.B1 in white_knights and not chess.G1 in white_knights:
                white_development += 2  # Both knights developed
            elif not chess.B1 in white_knights or not chess.G1 in white_knights:
                white_development += 1  # One knight developed

            if not chess.B8 in black_knights and not chess.G8 in black_knights:
                black_development += 2
            elif not chess.B8 in black_knights or not chess.G8 in black_knights:
                black_development += 1

            # Check if bishops moved from starting squares
            if not chess.C1 in white_bishops and not chess.F1 in white_bishops:
                white_development += 2  # Both bishops developed
            elif not chess.C1 in white_bishops or not chess.F1 in white_bishops:
                white_development += 1  # One bishop developed

            if not chess.C8 in black_bishops and not chess.F8 in black_bishops:
                black_development += 2
            elif not chess.C8 in black_bishops or not chess.F8 in black_bishops:
                black_development += 1

            # Bonus for development advantage
            score += 15 * (white_development - black_development)

        # Attack on enemy king
        white_king = self.board.king(chess.BLACK)  # Enemy king for white
        black_king = self.board.king(chess.WHITE)  # Enemy king for black

        if white_king:
            king_file = chess.square_file(white_king)
            king_rank = chess.square_rank(white_king)

            # Count attacks near enemy king
            for f in range(max(0, king_file - 1), min(8, king_file + 2)):
                for r in range(max(0, king_rank - 1), min(8, king_rank + 2)):
                    square = chess.square(f, r)
                    white_attackers = len(self.board.attackers(chess.WHITE, square))
                    score += 3 * white_attackers  # White attacking black king area

        if black_king:
            king_file = chess.square_file(black_king)
            king_rank = chess.square_rank(black_king)

            # Count attacks near enemy king
            for f in range(max(0, king_file - 1), min(8, king_file + 2)):
                for r in range(max(0, king_rank - 1), min(8, king_rank + 2)):
                    square = chess.square(f, r)
                    black_attackers = len(self.board.attackers(chess.BLACK, square))
                    score -= 3 * black_attackers  # Black attacking white king area

        # Piece coordination - adjacent pieces protecting each other
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if not piece:
                continue

            # Count how many pieces are defended
            defenders = self.board.attackers(piece.color, square)
            if piece.color == chess.WHITE:
                score += 2 * len(defenders)  # Small bonus for protected pieces
            else:
                score -= 2 * len(defenders)

        # Rooks on open files
        white_rooks = self.board.pieces(chess.ROOK, chess.WHITE)
        black_rooks = self.board.pieces(chess.ROOK, chess.BLACK)
        white_pawns = self.board.pieces(chess.PAWN, chess.WHITE)
        black_pawns = self.board.pieces(chess.PAWN, chess.BLACK)

        for square in white_rooks:
            file_num = chess.square_file(square)
            file_mask = chess.BB_FILES[file_num]

            # Check if file has no pawns (open) or only enemy pawns (half-open)
            white_pawns_in_file = white_pawns & chess.SquareSet(file_mask)
            black_pawns_in_file = black_pawns & chess.SquareSet(file_mask)

            if not white_pawns_in_file and not black_pawns_in_file:
                score += 25  # Open file
            elif not white_pawns_in_file:
                score += 15  # Half-open file

            # Extra bonus for connected rooks
            for other_square in white_rooks:
                if square != other_square:
                    if chess.square_file(square) == chess.square_file(other_square) or \
                            chess.square_rank(square) == chess.square_rank(other_square):
                        # Check if no pieces between rooks
                        between_squares = chess.SquareSet(chess.between(square, other_square))
                        if not any(self.board.piece_at(s) for s in between_squares):
                            score += 20  # Connected rooks

        for square in black_rooks:
            file_num = chess.square_file(square)
            file_mask = chess.BB_FILES[file_num]

            # Check if file has no pawns (open) or only enemy pawns (half-open)
            white_pawns_in_file = white_pawns & chess.SquareSet(file_mask)
            black_pawns_in_file = black_pawns & chess.SquareSet(file_mask)

            if not white_pawns_in_file and not black_pawns_in_file:
                score -= 25  # Open file
            elif not black_pawns_in_file:
                score -= 15  # Half-open file

            # Extra bonus for connected rooks
            for other_square in black_rooks:
                if square != other_square:
                    if chess.square_file(square) == chess.square_file(other_square) or \
                            chess.square_rank(square) == chess.square_rank(other_square):
                        # Check if no pieces between rooks
                        between_squares = chess.SquareSet(chess.between(square, other_square))
                        if not any(self.board.piece_at(s) for s in between_squares):
                            score -= 20  # Connected rooks

        # Outposts for knights and bishops
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if not piece:
                continue

            rank = chess.square_rank(square)
            file = chess.square_file(square)

            # White outposts
            if piece.color == chess.WHITE and piece.piece_type in [chess.KNIGHT, chess.BISHOP]:
                if rank >= 4:  # Advanced piece
                    is_outpost = True

                    # Check if square can be attacked by enemy pawns
                    for f in [max(0, file - 1), min(7, file + 1)]:
                        for r in range(rank + 1, 8):
                            pawn_square = chess.square(f, r)
                            if self.board.piece_at(pawn_square) == chess.Piece(chess.PAWN, chess.BLACK):
                                is_outpost = False
                                break
                        if not is_outpost:
                            break

                    # Check if supported by friendly pawn
                    pawn_support = False
                    for f in [max(0, file - 1), min(7, file + 1)]:
                        if rank > 0:
                            pawn_square = chess.square(f, rank - 1)
                            if self.board.piece_at(pawn_square) == chess.Piece(chess.PAWN, chess.WHITE):
                                pawn_support = True
                                break

                    if is_outpost:
                        score += 15  # Base outpost value
                        if pawn_support:
                            score += 10  # Additional value if supported by pawn

            # Black outposts
            elif piece.color == chess.BLACK and piece.piece_type in [chess.KNIGHT, chess.BISHOP]:
                if rank <= 3:  # Advanced piece
                    is_outpost = True

                    # Check if square can be attacked by enemy pawns
                    for f in [max(0, file - 1), min(7, file + 1)]:
                        for r in range(0, rank):
                            pawn_square = chess.square(f, r)
                            if self.board.piece_at(pawn_square) == chess.Piece(chess.PAWN, chess.WHITE):
                                is_outpost = False
                                break
                        if not is_outpost:
                            break

                    # Check if supported by friendly pawn
                    pawn_support = False
                    for f in [max(0, file - 1), min(7, file + 1)]:
                        if rank < 7:
                            pawn_square = chess.square(f, rank + 1)
                            if self.board.piece_at(pawn_square) == chess.Piece(chess.PAWN, chess.BLACK):
                                pawn_support = True
                                break

                    if is_outpost:
                        score -= 15  # Base outpost value
                        if pawn_support:
                            score -= 10  # Additional value if supported by pawn

        return score

    def _is_endgame(self):
        """Enhanced endgame detection with material thresholds"""
        # Count material for both sides
        white_material = sum(self.piece_values[p.piece_type] for p in self.board.piece_map().values()
                             if p.color == chess.WHITE and p.piece_type != chess.KING)
        black_material = sum(self.piece_values[p.piece_type] for p in self.board.piece_map().values()
                             if p.color == chess.BLACK and p.piece_type != chess.KING)

        # Count queens
        white_queens = len(self.board.pieces(chess.QUEEN, chess.WHITE))
        black_queens = len(self.board.pieces(chess.QUEEN, chess.BLACK))

        # Count minor pieces (knights and bishops)
        white_minor = (len(self.board.pieces(chess.KNIGHT, chess.WHITE)) +
                       len(self.board.pieces(chess.BISHOP, chess.WHITE)))
        black_minor = (len(self.board.pieces(chess.KNIGHT, chess.BLACK)) +
                       len(self.board.pieces(chess.BISHOP, chess.BLACK)))

        # Endgame if:
        # 1. No queens and at most one minor piece each, or
        # 2. Both sides have <= 1300 material (excluding king), or
        # 3. One side has queen and no other pieces, other side has <= one minor piece
        return (
                (white_queens == 0 and black_queens == 0 and white_minor <= 1 and black_minor <= 1) or
                (white_material <= 1300 and black_material <= 1300) or
                (white_queens == 1 and white_material - self.piece_values[
                    chess.QUEEN] == 0 and black_minor <= 1 and black_queens == 0) or
                (black_queens == 1 and black_material - self.piece_values[
                    chess.QUEEN] == 0 and white_minor <= 1 and white_queens == 0)
        )

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
