import chess
import time
import random
import math

# Piece values - slightly adjusted for improved balance
PAWN_VALUE = 100
KNIGHT_VALUE = 320  
BISHOP_VALUE = 330
ROOK_VALUE = 500
QUEEN_VALUE = 900
KING_VALUE = 20000

# Position tables for each piece
# Enhanced pawn table with more emphasis on center control and promotion
PAWN_TABLE = [
    0,   0,   0,   0,   0,   0,   0,   0,
    50, 50,  50,  50,  50,  50,  50,  50,
    15, 15,  25,  35,  35,  25,  15,  15,
    5,  5,   15,  30,  30,  15,   5,   5,
    0,  0,   5,   25,  25,  5,    0,   0,
    5,  -5,  -10, 0,   0,   -10,  -5,  5,
    5,  10,  10,  -20, -20, 10,   10,  5,
    0,  0,   0,   0,   0,   0,    0,   0
]

# Knights are most effective in the center, penalized on edges
KNIGHT_TABLE = [
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20, 0,   5,   5,   0,   -20, -40,
    -30, 5,   15,  20,  20,  15,  5,   -30,
    -30, 0,   20,  25,  25,  20,  0,   -30,
    -30, 0,   20,  25,  25,  20,  0,   -30,
    -30, 5,   15,  20,  20,  15,  5,   -30,
    -40, -20, 0,   5,   5,   0,   -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50
]

# Enhanced bishop table - stronger control of diagonals
BISHOP_TABLE = [
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10, 5,   0,   0,   0,   0,   5,   -10,
    -10, 10,  10,  10,  10,  10,  10,  -10,
    -10, 0,   10,  15,  15,  10,  0,   -10,
    -10, 5,   5,   15,  15,  5,   5,   -10,
    -10, 0,   10,  10,  10,  10,  0,   -10,
    -10, 5,   0,   0,   0,   0,   5,   -10,
    -20, -10, -10, -10, -10, -10, -10, -20
]

# Improved rook table - stronger on open files and 7th rank
ROOK_TABLE = [
    0,  0,  0,  5,  5,  0,  0,  0,
    -5, 0,  0,  0,  0,  0,  0,  -5,
    -5, 0,  0,  0,  0,  0,  0,  -5,
    -5, 0,  0,  0,  0,  0,  0,  -5,
    -5, 0,  0,  0,  0,  0,  0,  -5,
    -5, 0,  0,  0,  0,  0,  0,  -5,
    5,  10, 10, 10, 10, 10, 10, 5,
    0,  0,  0,  0,  0,  0,  0,  0
]

# Enhanced queen table - improved central control
QUEEN_TABLE = [
    -20, -10, -10, -5,  -5,  -10, -10, -20,
    -10, 0,   0,   0,   0,   0,   0,   -10,
    -10, 0,   5,   5,   5,   5,   0,   -10,
    -5,  0,   5,   10,  10,  5,   0,   -5,
    0,   0,   5,   10,  10,  5,   0,   -5,
    -10, 5,   5,   5,   5,   5,   0,   -10,
    -10, 0,   5,   0,   0,   0,   0,   -10,
    -20, -10, -10, -5,  -5,  -10, -10, -20
]

# King tables - enhanced for better king safety
KING_MIDDLE_TABLE = [
    -40, -50, -50, -60, -60, -50, -50, -40,
    -40, -50, -50, -60, -60, -50, -50, -40,
    -40, -50, -50, -60, -60, -50, -50, -40,
    -40, -50, -50, -60, -60, -50, -50, -40,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -20, -30, -30, -30, -30, -30, -30, -20,
    20,  20,  -10, -10, -10, -10, 20,  20,
    20,  30,  10,  0,   0,   10,  30,  20
]

# Enhanced endgame king table - more aggressive king
KING_END_TABLE = [
    -50, -40, -30, -20, -20, -30, -40, -50,
    -30, -20, -10, 0,   0,   -10, -20, -30,
    -30, -10, 20,  30,  30,  20,  -10, -30,
    -30, -10, 30,  40,  40,  30,  -10, -30,
    -30, -10, 30,  40,  40,  30,  -10, -30,
    -30, -10, 20,  30,  30,  20,  -10, -30,
    -30, -20, -10, 0,   0,   -10, -20, -30,
    -50, -30, -30, -30, -30, -30, -30, -50
]

class ChessAI:
    def __init__(self, depth=4, time_limit=10):
        self.depth = depth
        self.time_limit = time_limit  # Maximum time in seconds
        self.board = chess.Board()
        self.transposition_table = {}
        self.nodes_searched = 0
        self.best_move_found = None
        self.start_time = 0
        self.stop_search = False
        self.history_table = {}  # For history heuristic
        self.killer_moves = [[None, None] for _ in range(100)]  # For killer heuristic
        
        # Static piece values
        self.piece_values = {
            chess.PAWN: PAWN_VALUE,
            chess.KNIGHT: KNIGHT_VALUE,
            chess.BISHOP: BISHOP_VALUE,
            chess.ROOK: ROOK_VALUE,
            chess.QUEEN: QUEEN_VALUE,
            chess.KING: KING_VALUE
        }
        
        # Opening book - simplified but effective
        self.opening_book = {
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -": ["e2e4", "d2d4", "c2c4", "g1f3"],  # Common white openings
            "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3": ["e7e5", "c7c5", "e7e6", "c7c6"],  # Replies to e4
            "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq d3": ["d7d5", "g8f6", "e7e6", "c7c5"],  # Replies to d4
        }
        
    def reset_board(self):
        """Reset the board to starting position"""
        self.board = chess.Board()
        self.transposition_table = {}
        self.history_table = {}
        self.killer_moves = [[None, None] for _ in range(100)]
        
    def set_board_from_fen(self, fen):
        """Set board from FEN notation"""
        try:
            self.board = chess.Board(fen)
            self.transposition_table = {}
            self.history_table = {}
            self.killer_moves = [[None, None] for _ in range(100)]
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

        self.nodes_searched = 0
        self.start_time = time.time()
        self.best_move_found = None
        self.stop_search = False
        
        # Check opening book first
        book_move = self._check_opening_book()
        if book_move:
            print(f"Using opening book move: {book_move}")
            return book_move
        
        # If there's only one legal move, play it immediately
        legal_moves = list(self.board.legal_moves)
        if len(legal_moves) == 1:
            return legal_moves[0]
        
        # Set starting best move to avoid None results
        if legal_moves:
            self.best_move_found = legal_moves[0]
        
        # Iterative deepening with adaptive depth
        max_depth = self._calculate_adaptive_depth()
        
        for current_depth in range(1, max_depth + 1):
            self._search_with_iterative_deepening(current_depth)
            
            # Check if time limit is exceeded
            if time.time() - self.start_time > self.time_limit * 0.8 or self.stop_search:
                print(f"Time limit approaching/reached after depth {current_depth}")
                break
                
        elapsed_time = time.time() - self.start_time
        print(f"Searched {self.nodes_searched} nodes in {elapsed_time:.2f} seconds")
        
        # Fallback to a random move if no best move was found (shouldn't happen)
        if self.best_move_found is None and legal_moves:
            print("Warning: No best move found, selecting random move")
            self.best_move_found = random.choice(legal_moves)
            
        return self.best_move_found
    
    def _check_opening_book(self):
        """Check if current position is in opening book"""
        fen = self.board.fen()
        # Check if exact position is in book
        if fen in self.opening_book:
            return chess.Move.from_uci(random.choice(self.opening_book[fen]))
        
        # Check simplified position (just board position and side to move)
        simplified_fen = ' '.join(fen.split(' ')[:2])
        for book_fen in self.opening_book:
            if book_fen.startswith(simplified_fen):
                return chess.Move.from_uci(random.choice(self.opening_book[book_fen]))
                
        return None
    
    def _calculate_adaptive_depth(self):
        """Calculate adaptive search depth based on position complexity"""
        # Get base depth from settings
        base_depth = self.depth
        
        # Count pieces to estimate complexity
        total_pieces = sum(1 for _ in self.board.piece_map())
        
        # Fewer pieces = can search deeper
        if total_pieces <= 10:  # Endgame
            return min(base_depth + 2, 8)
        elif total_pieces <= 20:  # Late middlegame
            return min(base_depth + 1, 7)
        else:  # Opening/early middlegame
            return base_depth
    
    def _search_with_iterative_deepening(self, depth):
        """Perform search at a specific depth"""
        alpha = float('-inf')
        beta = float('inf')
        best_score = float('-inf')
        current_best_move = None
        
        # For aspiration window - improves search efficiency
        if depth >= 3 and self.best_move_found:
            # Get previous evaluation
            prev_eval = self._get_stored_evaluation()
            if prev_eval != float('inf'):
                # Create aspiration window
                window = 50  # initial window size (in centipawns)
                alpha = prev_eval - window
                beta = prev_eval + window
                
                # Try search with aspiration window
                score = self._alpha_beta(depth, alpha, beta, 0, True)
                
                # If score is outside window, retry with full window
                if score <= alpha or score >= beta:
                    alpha = float('-inf')
                    beta = float('inf')
                    score = self._alpha_beta(depth, alpha, beta, 0, True)
                    
                best_score = score
            else:
                # No previous evaluation, do full search
                best_score = self._alpha_beta(depth, alpha, beta, 0, True)
        else:
            # Full window search for early depths
            best_score = self._alpha_beta(depth, alpha, beta, 0, True)
            
        if self.best_move_found:
            print(f"Depth {depth}: Best move = {self.best_move_found}, Score = {best_score}")
            
        # Store evaluation for aspiration window
        self._store_evaluation(best_score)
    
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
                    score += 10 * self.piece_values[victim_piece.piece_type] - self.piece_values[aggressor_piece.piece_type]
            
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
                if piece and piece.piece_type in [chess.KNIGHT, chess.BISHOP] and chess.square_rank(from_square) in [0, 7]:
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
                position_value = KING_END_TABLE[square if piece.color else 63 - square] if is_endgame else KING_MIDDLE_TABLE[square if piece.color else 63 - square]
            
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
                    shield_files = [max(0, wk_file-1), wk_file, wk_file+1]
                elif wk_file > 4:  # Kingside castle
                    shield_files = [wk_file-1, wk_file, min(7, wk_file+1)]
                else:  # Middle (not castled or e-file)
                    shield_files = [max(0, wk_file-1), wk_file, min(7, wk_file+1)]
                    
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
                    shield_files = [max(0, bk_file-1), bk_file, bk_file+1]
                elif bk_file > 4:  # Kingside castle
                    shield_files = [bk_file-1, bk_file, min(7, bk_file+1)]
                else:  # Middle (not castled or e-file)
                    shield_files = [max(0, bk_file-1), bk_file, min(7, bk_file+1)]
                    
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
            (white_queens == 1 and white_material - self.piece_values[chess.QUEEN] == 0 and black_minor <= 1 and black_queens == 0) or
            (black_queens == 1 and black_material - self.piece_values[chess.QUEEN] == 0 and white_minor <= 1 and white_queens == 0)
        )
        
    def _is_opening(self):
        """Detect if the game is still in opening phase"""
        # Consider it opening if less than 10 moves have been played
        # and both sides still have most of their original pieces
        
        # Check move number
        if self.board.fullmove_number <= 10:
            # Count total pieces remaining
            total_pieces = len(self.board.piece_map())
            
            # In a typical opening, there should be at least 24+ pieces on the board
            # (32 - a few captures)
            if total_pieces >= 24:
                return True
        
        return False