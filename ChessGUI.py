import chess
import time
import random
import pygame
import sys
from pygame.locals import *

from ai import ChessAI


class ChessGUI:
    def __init__(self):
        pygame.init()
        self.square_size = 80
        self.board_size = self.square_size * 8
        self.margin = 40

        # Determine required width for game screen elements
        game_button_width = 100
        game_button_height = 40
        game_button_spacing = 10
        game_buttons_total_width = 5 * (game_button_width + game_button_spacing) + 20 + 100  # From original code

        # General window size, can be adjusted if start screen needs more space
        # Using a fixed reasonable width for now, can be made dynamic
        # Max of board width and game buttons width
        required_game_content_width = max(self.board_size + 2 * self.margin, game_buttons_total_width + 2 * self.margin)
        self.window_width = max(required_game_content_width, 800)  # Ensure at least 800px for start screen aesthetics
        self.window_height = self.board_size + self.margin * 2 + 100  # Height for game screen
        self.window_size = (self.window_width, self.window_height)

        self.screen = pygame.display.set_mode(self.window_size, pygame.DOUBLEBUF)
        pygame.display.set_caption("ChessAI")

        self.clock = pygame.time.Clock()

        try:
            self.font = pygame.font.Font("assets/fonts/Roboto-Regular.ttf", 16)
            self.status_font = pygame.font.Font("assets/fonts/Roboto-Medium.ttf", 18)
            self.title_font_large = pygame.font.Font("assets/fonts/Roboto-Bold.ttf", 60)
            self.title_font_medium = pygame.font.Font("assets/fonts/Roboto-Bold.ttf", 36)
            self.button_font = pygame.font.Font("assets/fonts/Roboto-Medium.ttf", 22)
        except:
            self.font = pygame.font.SysFont("Arial", 16)
            self.status_font = pygame.font.SysFont("Arial", 18, bold=True)
            self.title_font_large = pygame.font.SysFont("Arial", 60, bold=True)
            self.title_font_medium = pygame.font.SysFont("Arial", 36, bold=True)
            self.button_font = pygame.font.SysFont("Arial", 22, bold=True)

        self.ai = ChessAI(depth=3)

        self.selected_square = None
        self.possible_moves = []
        self.player_color = chess.WHITE

        self.status_text = "Welcome to ChessAI!"
        self.difficulty = "Medium"
        self.ai_thinking_time = 0

        self._load_assets()

        # --- Game State and Start Screen Buttons ---
        self.game_state = "START_SCREEN"  # "START_SCREEN", "PLAYING", "INSTRUCTIONS"

        start_button_width = 280
        start_button_height = 70
        start_button_spacing = 25

        # Center buttons vertically. Total height of buttons + spacing:
        total_buttons_stack_height = 3 * start_button_height + 2 * start_button_spacing
        start_screen_buttons_y_top = (
                                                 self.window_height - total_buttons_stack_height) // 2 + 60  # Shift down a bit from true center for title

        self.start_play_btn = pygame.Rect(
            self.window_width // 2 - start_button_width // 2,
            start_screen_buttons_y_top,
            start_button_width,
            start_button_height
        )
        self.start_instruction_btn = pygame.Rect(
            self.window_width // 2 - start_button_width // 2,
            start_screen_buttons_y_top + start_button_height + start_button_spacing,
            start_button_width,
            start_button_height
        )
        self.start_quit_btn = pygame.Rect(
            self.window_width // 2 - start_button_width // 2,
            start_screen_buttons_y_top + 2 * (start_button_height + start_button_spacing),
            start_button_width,
            start_button_height
        )

        # Instruction Screen Button
        back_button_width = 180
        back_button_height = 50
        self.instruction_back_btn = pygame.Rect(
            self.window_width // 2 - back_button_width // 2,
            self.window_height - back_button_height - 40,  # Near bottom
            back_button_width,
            back_button_height
        )

        # --- Game Screen Buttons (defined relative to board position) ---
        # These are positioned based on self.margin and self.board_size
        game_btn_y = self.board_size + self.margin + 20
        game_btn_start_x = self.margin  # Start from the left margin of the board

        self.new_game_btn = pygame.Rect(game_btn_start_x, game_btn_y, game_button_width, game_button_height)
        self.switch_sides_btn = pygame.Rect(game_btn_start_x + game_button_width + game_button_spacing, game_btn_y,
                                            game_button_width, game_button_height)
        self.difficulty_btn = pygame.Rect(game_btn_start_x + 2 * (game_button_width + game_button_spacing), game_btn_y,
                                          game_button_width, game_button_height)
        self.stockfish_btn = pygame.Rect(game_btn_start_x + 3 * (game_button_width + game_button_spacing), game_btn_y,
                                         game_button_width, game_button_height)
        self.stockfish_battle_btn = pygame.Rect(game_btn_start_x + 4 * (game_button_width + game_button_spacing),
                                                game_btn_y,
                                                game_button_width + 20, game_button_height)  # This button is wider
        self.stockfish_slider = pygame.Rect(game_btn_start_x + 5 * (game_button_width + game_button_spacing) + 20,
                                            game_btn_y,
                                            100, game_button_height)

        self.running = True
        self.need_ai_move = False  # AI's turn to move in Player vs AI

        self.use_stockfish = True  # Default for internal AI assistance
        self.stockfish_battle_mode = False
        self.stockfish_level = 10  # Default SF level
        self.last_ai_move_time = 0  # For AI vs AI battle timing

    def load_images(self):
        self.piece_images = {}
        try:
            pieces_image = pygame.image.load("assets/images/Chess_Pieces.png")
            piece_width = pieces_image.get_width() // 6
            piece_height = pieces_image.get_height() // 2
            piece_types = ['K', 'Q', 'B', 'N', 'R', 'P']
            for i, piece_type in enumerate(piece_types):
                x = i * piece_width
                white_piece_surf = pieces_image.subsurface((x, 0, piece_width, piece_height))
                self.piece_images[piece_type] = pygame.transform.smoothscale(white_piece_surf,
                                                                             (self.square_size, self.square_size))
                black_piece_surf = pieces_image.subsurface((x, piece_height, piece_width, piece_height))
                self.piece_images[piece_type.lower()] = pygame.transform.smoothscale(black_piece_surf,
                                                                                     (self.square_size,
                                                                                      self.square_size))
        except pygame.error as e:
            print(f"Không thể tải hình ảnh quân cờ: {e}. Sử dụng hình ảnh mặc định.")
            self.create_default_piece_images()

    def _load_start_screen_background(self):
        """Tải và thay đổi kích thước ảnh nền cho màn hình bắt đầu."""
        try:
            # Đảm bảo bạn có một file ảnh tại đường dẫn này
            # Ví dụ: "assets/images/start_background.jpg" hoặc "assets/images/start_background.png"
            image_path = "assets/images/start_screen_background.png"  # THAY ĐỔI ĐƯỜNG DẪN NÀY
            original_image = pygame.image.load(image_path)
            # Thay đổi kích thước ảnh để vừa với cửa sổ game
            self.start_screen_background_image = pygame.transform.smoothscale(
                original_image,
                (self.window_width, self.window_height)
            )
            # .convert() giúp tối ưu hóa việc vẽ ảnh (blit) nhanh hơn
            self.start_screen_background_image = self.start_screen_background_image.convert()
        except pygame.error as e:
            print(f"Lỗi: Không thể tải ảnh nền màn hình bắt đầu '{image_path}': {e}")
            self.start_screen_background_image = None  # Sử dụng fallback nếu không tải được

    def _load_assets(self):
        """Tải tất cả tài sản hình ảnh và font chữ."""
        self.load_images()  # Tải ảnh quân cờ
        self._load_start_screen_background()

    def create_default_piece_images(self):
        piece_types = ['K', 'Q', 'B', 'N', 'R', 'P']
        piece_font = pygame.font.SysFont("Arial", self.square_size // 3)
        for piece_type in piece_types:
            white_img = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
            pygame.draw.circle(white_img, (220, 220, 220), (self.square_size // 2, self.square_size // 2),
                               int(self.square_size // 2.8))
            pygame.draw.circle(white_img, (180, 180, 180), (self.square_size // 2, self.square_size // 2),
                               int(self.square_size // 2.8), 2)
            self.piece_images[piece_type] = white_img
            black_img = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
            pygame.draw.circle(black_img, (50, 50, 50), (self.square_size // 2, self.square_size // 2),
                               int(self.square_size // 2.8))
            pygame.draw.circle(black_img, (80, 80, 80), (self.square_size // 2, self.square_size // 2),
                               int(self.square_size // 2.8), 2)
            self.piece_images[piece_type.lower()] = black_img
            white_text_surf = piece_font.render(piece_type, True, (0, 0, 0))
            black_text_surf = piece_font.render(piece_type, True, (255, 255, 255))
            wt_rect = white_text_surf.get_rect(center=(self.square_size // 2, self.square_size // 2))
            bt_rect = black_text_surf.get_rect(center=(self.square_size // 2, self.square_size // 2))
            white_img.blit(white_text_surf, wt_rect.topleft)
            black_img.blit(black_text_surf, bt_rect.topleft)

    def draw_start_screen(self):
        if self.start_screen_background_image:
            self.screen.blit(self.start_screen_background_image, (0, 0))
        else:
            self.screen.fill((50, 50, 70))  # Fallback: tô màu nếu không có ảnh  # Dark blueish background

        # Title
        title_text_surf = self.title_font_large.render("ChessAI", True, (220, 220, 255))
        title_rect = title_text_surf.get_rect(center=(self.window_width // 2, self.window_height // 4 - 20))
        self.screen.blit(title_text_surf, title_rect)

        buttons_to_draw = [
            (self.start_play_btn, "Play Game"),
            (self.start_instruction_btn, "Instructions"),
            (self.start_quit_btn, "Quit")
        ]

        mouse_pos = pygame.mouse.get_pos()
        button_base_color = (58, 68, 58)
        button_hover_color = (75, 88, 75)
        button_text_color = (210, 220, 210)
        button_outline_color = (90, 105, 90)

        for rect, text_content in buttons_to_draw:
            current_button_color = button_hover_color if rect.collidepoint(mouse_pos) else button_base_color
            pygame.draw.rect(self.screen, current_button_color, rect, border_radius=12)
            pygame.draw.rect(self.screen, button_outline_color, rect, width=3, border_radius=12)

            btn_text_surf = self.button_font.render(text_content, True, button_text_color)
            text_rect = btn_text_surf.get_rect(center=rect.center)
            self.screen.blit(btn_text_surf, text_rect.topleft)

    def draw_instruction_screen(self):
        self.screen.fill((230, 230, 240))  # Light background

        # Title
        instr_title_surf = self.title_font_medium.render("How to Play ChessAI", True, (50, 50, 50))
        instr_title_rect = instr_title_surf.get_rect(center=(self.window_width // 2, self.margin * 2))
        self.screen.blit(instr_title_surf, instr_title_rect)

        instruction_lines = [
            "Welcome to ChessAI!",
            "",
            "Objective:",
            "  Checkmate your opponent's king.",
            "",
            "Basic Gameplay:",
            "- Click on one of your pieces to select it.",
            "- Valid moves for the selected piece will be highlighted.",
            "- Click on a highlighted square to make your move.",
            "- Pawns reaching the opponent's back rank are automatically promoted to Queens.",
            "",
            "Game Controls (Below the Board):",
            "  New Game: Starts a fresh game.",
            "  Switch Sides: Toggles your playing color (White/Black) and restarts.",
            "  Diff: Cycles AI difficulty (Easy, Medium, Hard, Very Hard).",
            "  SF: Toggles the Stockfish engine for the AI opponent (if available).",
            "  VS Stockfish: Pits the internal AI (White) against Stockfish (Black).",
            "    - Use the 'Lvl' slider to set Stockfish's strength (1-20).",
            "",
        ]

        current_y = instr_title_rect.bottom + 30
        text_x_start = self.margin + 30
        line_spacing = 6
        text_color = (30, 30, 30)

        for line_text in instruction_lines:
            is_heading = ":" in line_text and line_text.endswith(
                ":") or "Welcome" in line_text or "Good luck" in line_text
            current_font = self.status_font if is_heading else self.font

            line_surf = current_font.render(line_text, True, text_color)

            x_pos = text_x_start
            if is_heading and "Welcome" not in line_text and "Good luck" not in line_text:  # Indent non-title headings
                x_pos = text_x_start - 15
            elif "Welcome" in line_text or "Good luck" in line_text:  # Center welcome/goodluck
                x_pos = self.window_width // 2 - line_surf.get_width() // 2

            self.screen.blit(line_surf, (x_pos, current_y))
            current_y += line_surf.get_height() + line_spacing
            if line_text == "" or is_heading:
                current_y += line_spacing  # Extra space after blank or heading

        # Back Button
        mouse_pos = pygame.mouse.get_pos()
        button_base_color = (180, 180, 190)
        button_hover_color = (160, 160, 170)
        button_text_color_dark = (20, 20, 20)
        button_outline_color = (100, 100, 110)

        current_button_color = button_hover_color if self.instruction_back_btn.collidepoint(
            mouse_pos) else button_base_color
        pygame.draw.rect(self.screen, current_button_color, self.instruction_back_btn, border_radius=10)
        pygame.draw.rect(self.screen, button_outline_color, self.instruction_back_btn, width=2, border_radius=10)

        back_text_surf = self.button_font.render("Back", True, button_text_color_dark)
        back_text_rect = back_text_surf.get_rect(center=self.instruction_back_btn.center)
        self.screen.blit(back_text_surf, back_text_rect.topleft)

    def draw_board(self):
        self.screen.fill((35, 35, 35))

        board_surface_x = self.margin
        board_surface_y = self.margin

        for row in range(8):
            for col in range(8):
                x = col * self.square_size + board_surface_x
                y = row * self.square_size + board_surface_y
                light_square_color = (58, 58, 58)
                dark_square_color = (49, 49, 49)
                current_color = light_square_color if (row + col) % 2 == 0 else dark_square_color
                square = chess.square(col, 7 - row)
                if square == self.selected_square:
                    current_color = (110, 140, 220)
                elif square in self.possible_moves:
                    current_color = (130, 190, 110) if (row + col) % 2 == 0 else (80, 120, 80)
                pygame.draw.rect(self.screen, current_color, (x, y, self.square_size, self.square_size))
                label_color = (50, 50, 50)
                if row == 7:
                    text_surf = self.font.render(chess.FILE_NAMES[col], True, label_color)
                    self.screen.blit(text_surf, (x + self.square_size - text_surf.get_width() - 5,
                                                 y + self.square_size - text_surf.get_height() - 2))
                if col == 0:
                    text_surf = self.font.render(chess.RANK_NAMES[7 - row], True, label_color)
                    self.screen.blit(text_surf, (x + 3, y + 2))

        for square_idx in chess.SQUARES:
            piece = self.ai.board.piece_at(square_idx)
            if piece:
                col = chess.square_file(square_idx)
                row = 7 - chess.square_rank(square_idx)
                piece_rect = pygame.Rect(col * self.square_size + board_surface_x,
                                         row * self.square_size + board_surface_y, self.square_size, self.square_size)
                piece_symbol = piece.symbol()
                if piece_symbol in self.piece_images:
                    self.screen.blit(self.piece_images[piece_symbol], piece_rect)

        button_color = (220, 220, 220)
        button_hover_color = (200, 200, 200)
        text_color = (0, 0, 0)
        game_buttons = [
            (self.new_game_btn, "New Game"),
            (self.switch_sides_btn, "Switch Sides"),
            (self.difficulty_btn, f"Diff: {self.difficulty}"),
            (self.stockfish_btn, f"SF AI: {'On' if self.use_stockfish else 'Off'}"),  # Clarify this is for AI opponent
            (self.stockfish_battle_btn, "AI vs SF")  # Shorter text
        ]
        mouse_pos = pygame.mouse.get_pos()
        for rect, text_content in game_buttons:
            current_button_color = button_hover_color if rect.collidepoint(mouse_pos) else button_color
            pygame.draw.rect(self.screen, current_button_color, rect, border_radius=5)
            pygame.draw.rect(self.screen, (150, 150, 150), rect, width=1, border_radius=5)
            btn_text_surf = self.font.render(text_content, True, text_color)
            text_rect = btn_text_surf.get_rect(center=rect.center)
            self.screen.blit(btn_text_surf, text_rect.topleft)

        if self.stockfish_battle_mode:
            slider_bg_color = (220, 220, 220)
            slider_bar_color = (100, 100, 255)
            handle_width = 10
            pygame.draw.rect(self.screen, slider_bg_color, self.stockfish_slider, border_radius=5)
            pygame.draw.rect(self.screen, (150, 150, 150), self.stockfish_slider, width=1, border_radius=5)
            level_percentage = (self.stockfish_level - 1) / (20 - 1)
            handle_x = self.stockfish_slider.x + level_percentage * (self.stockfish_slider.w - handle_width)
            handle_rect = pygame.Rect(handle_x, self.stockfish_slider.y, handle_width, self.stockfish_slider.h)
            pygame.draw.rect(self.screen, slider_bar_color, handle_rect, border_radius=3)
            level_text_surf = self.font.render(f"Lvl: {self.stockfish_level}", True, text_color)
            self.screen.blit(level_text_surf, (self.stockfish_slider.right + 10,
                                               self.stockfish_slider.centery - level_text_surf.get_height() // 2))
            mode_text_surf = self.status_font.render("Mode: Internal AI (W) vs Stockfish (B)", True, (0, 100, 0))
            self.screen.blit(mode_text_surf, (self.margin, self.board_size + self.margin + 60))

        status_display_text = f"{self.status_text} (AI Time: {self.ai_thinking_time:.2f}s)"
        status_text_surf = self.status_font.render(status_display_text, True, (250, 250, 250))
        self.screen.blit(status_text_surf, (self.margin, self.margin // 2 - status_text_surf.get_height() // 2))

    def handle_start_screen_click(self, pos):
        if self.start_play_btn.collidepoint(pos):
            self.game_state = "PLAYING"
            self.new_game()  # Initialize and start the game
        elif self.start_instruction_btn.collidepoint(pos):
            self.game_state = "INSTRUCTIONS"
        elif self.start_quit_btn.collidepoint(pos):
            self.running = False

    def handle_instruction_screen_click(self, pos):
        if self.instruction_back_btn.collidepoint(pos):
            self.game_state = "START_SCREEN"

    def handle_click(self, pos):  # Handles clicks during PLAYING state
        x, y = pos
        # Game control buttons
        if self.new_game_btn.collidepoint(x, y):
            self.new_game()
            return
        elif self.switch_sides_btn.collidepoint(x, y):
            self.switch_sides()
            return
        elif self.difficulty_btn.collidepoint(x, y):
            self.cycle_difficulty()
            return
        elif self.stockfish_btn.collidepoint(x, y):
            self.toggle_stockfish_for_ai()  # Renamed for clarity
            return
        elif self.stockfish_battle_btn.collidepoint(x, y):
            self.toggle_stockfish_battle()
            return
        elif self.stockfish_battle_mode and self.stockfish_slider.collidepoint(x, y):
            # Update Stockfish level based on click position on slider
            # Level range 1-20. Slider width is self.stockfish_slider.w
            # Relative click position: (x - self.stockfish_slider.x)
            # Percentage: (x - self.stockfish_slider.x) / self.stockfish_slider.w
            # Level: 1 + percentage * 19
            raw_level = 1 + ((x - self.stockfish_slider.x) / self.stockfish_slider.w) * 19
            self.stockfish_level = min(20, max(1, int(round(raw_level))))
            self.ai.set_stockfish_strength(self.stockfish_level)  # Update AI (Stockfish opponent)
            return

        # Board clicks
        if x < self.margin or x > self.board_size + self.margin or y < self.margin or y > self.board_size + self.margin:
            return  # Click outside board

        if self.ai.board.is_game_over() or (not self.stockfish_battle_mode and self.ai.board.turn != self.player_color):
            return  # Game over or not player's turn (in Player vs AI)

        col = (x - self.margin) // self.square_size
        row = (y - self.margin) // self.square_size
        square = chess.square(col, 7 - row)

        if self.stockfish_battle_mode:  # No player interaction in AI vs AI
            return

        if self.selected_square is None:
            piece = self.ai.board.piece_at(square)
            if piece and piece.color == self.player_color:
                self.selected_square = square
                self.possible_moves = [move.to_square for move in self.ai.board.legal_moves if
                                       move.from_square == square]
        else:
            move = chess.Move(self.selected_square, square)
            if self.ai.board.piece_at(self.selected_square) and \
                    self.ai.board.piece_at(self.selected_square).piece_type == chess.PAWN and \
                    ((self.player_color == chess.WHITE and chess.square_rank(square) == 7) or \
                     (self.player_color == chess.BLACK and chess.square_rank(square) == 0)):
                move = chess.Move(self.selected_square, square, promotion=chess.QUEEN)

            if move in self.ai.board.legal_moves:
                self.ai.board.push(move)
                self.status_text = "AI is thinking..."
                self.selected_square = None
                self.possible_moves = []
                self.need_ai_move = True  # Signal for AI to make a move
            else:  # Invalid move or clicked on another piece
                piece = self.ai.board.piece_at(square)
                if piece and piece.color == self.player_color:  # Clicked on another of player's pieces
                    self.selected_square = square
                    self.possible_moves = [m.to_square for m in self.ai.board.legal_moves if m.from_square == square]
                else:  # Clicked on empty square or opponent piece (not a valid move)
                    self.selected_square = None
                    self.possible_moves = []

    def toggle_stockfish_for_ai(self):  # For the AI opponent in Player vs AI
        self.use_stockfish = not self.use_stockfish
        self.ai.toggle_stockfish(self.use_stockfish)  # This tells ChessAI whether ITS OWN moves should use Stockfish
        status = "On" if self.use_stockfish else "Off"
        self.status_text = f"AI using Stockfish engine: {status}"
        # This does NOT affect stockfish_battle_mode where internal AI plays SF

    def make_ai_move(self):
        if self.ai.board.is_game_over():
            return

        start_time = time.time()
        ai_move = self.ai.get_ai_move()  # This now considers stockfish_battle_mode
        self.ai_thinking_time = time.time() - start_time

        if ai_move:
            # Generate SAN *before* pushing the move
            try:
                move_text = self.ai.board.san(ai_move)  # Use SAN for readability
            except Exception as e:
                # Fallback if san fails for some unexpected reason, though it shouldn't with a legal move
                print(f"Error generating SAN for move {ai_move}: {e}. Using UCI notation.")
                move_text = ai_move.uci()

            self.ai.board.push(ai_move) # Now push the move

            if self.stockfish_battle_mode:
                # After the move, the turn has flipped.
                # So, if it's now Black's turn, White (Internal AI) just played.
                # If it's now White's turn, Black (Stockfish) just played.
                if self.ai.board.turn == chess.BLACK: # Internal AI (White) just moved
                    player_who_moved = "Internal AI (W)"
                else: # Stockfish (Black) just moved
                    player_who_moved = "Stockfish (B)"
                self.status_text = f"{player_who_moved} played: {move_text}"
            else:  # Player vs AI
                self.status_text = f"AI played: {move_text}. Your turn."
        else:
            if not self.ai.board.is_game_over(): # Only show this if game isn't actually over
                self.status_text = "AI cannot make a move (or no legal moves)."
            # If game is over, update_game_status will handle the message.

        self.need_ai_move = False  # AI has moved (in Player vs AI mode)
        self.update_game_status() # Update status after the move

    def update_game_status(self):
        if self.ai.board.is_checkmate():
            winner_color = "White" if not self.ai.board.turn else "Black"  # Winner is the one whose turn it ISN'T
            if self.stockfish_battle_mode:
                winner_player = "Internal AI (White)" if winner_color == "White" else "Stockfish (Black)"
                self.status_text = f"Checkmate! {winner_player} wins."
            else:  # Player vs AI
                winner_player = "You" if (self.player_color == chess.WHITE and winner_color == "White") or \
                                         (self.player_color == chess.BLACK and winner_color == "Black") else "AI"
                self.status_text = f"Checkmate! {winner_player} ({winner_color}) wins."
            self.show_game_over_message(self.status_text)
        elif self.ai.board.is_stalemate():
            self.status_text = "Stalemate! Draw."
            self.show_game_over_message("Stalemate! It's a draw.")
        elif self.ai.board.is_insufficient_material():
            self.status_text = "Draw by insufficient material."
            self.show_game_over_message("Draw by insufficient material.")
        elif self.ai.board.is_repetition(3):
            self.status_text = "Draw by threefold repetition."
            self.show_game_over_message("Draw by threefold repetition.")
        elif self.ai.board.is_fifty_moves():
            self.status_text = "Draw by fifty-move rule."
            self.show_game_over_message("Draw by fifty-move rule.")
        elif self.ai.board.is_check():
            turn_player = ""
            if self.stockfish_battle_mode:
                turn_player = "Internal AI (W)" if self.ai.board.turn == chess.WHITE else "Stockfish (B)"
            else:
                turn_player = "Your" if self.ai.board.turn == self.player_color else "AI's"
            self.status_text = f"Check! {turn_player} turn."

    def show_game_over_message(self, message):
        overlay = pygame.Surface(self.window_size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Semi-transparent overlay
        self.screen.blit(overlay, (0, 0))

        # Display message
        text_surf = self.title_font_medium.render(message, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=(self.window_width // 2, self.window_height // 2 - 30))
        self.screen.blit(text_surf, text_rect)

        # "Click to return to Start Screen" message
        sub_text_surf = self.status_font.render("Click anywhere to return to Start Screen", True, (200, 200, 220))
        sub_text_rect = sub_text_surf.get_rect(center=(self.window_width // 2, self.window_height // 2 + 30))
        self.screen.blit(sub_text_surf, sub_text_rect)

        pygame.display.update()  # Show message

        # Wait for a click to proceed
        waiting_for_click = True
        while waiting_for_click:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                    waiting_for_click = False
                if event.type == MOUSEBUTTONDOWN:
                    waiting_for_click = False
            self.clock.tick(30)

        if self.running:  # If not quit during message
            self.game_state = "START_SCREEN"  # Go back to start screen

    def new_game(self):
        self.ai.reset_board()
        self.selected_square = None
        self.possible_moves = []
        self.ai_thinking_time = 0
        self.last_ai_move_time = pygame.time.get_ticks()  # Reset for AI vs AI battle

        if self.stockfish_battle_mode:
            self.ai.toggle_stockfish_opponent(True)  # Ensure SF opponent is set in AI
            self.ai.set_stockfish_strength(self.stockfish_level)  # Apply current level
            self.status_text = f"AI (W) vs Stockfish (B) Lvl:{self.stockfish_level}. Internal AI's turn."
            # In battle mode, internal AI is always White and starts
            self.player_color = chess.WHITE  # Not really "player", but AI's color
            self.need_ai_move = True  # Internal AI (White) to make the first move
        else:  # Player vs AI
            self.ai.toggle_stockfish_opponent(False)  # Ensure SF opponent is OFF in AI
            self.ai.toggle_stockfish(self.use_stockfish)  # Apply player's choice for AI engine
            if self.player_color == chess.WHITE:
                self.status_text = "New Game! Your turn (White)."
                self.need_ai_move = False
            else:
                self.status_text = "New Game! AI's turn (White)."
                self.need_ai_move = True
        self.update_game_status()

    def switch_sides(self):
        if not self.stockfish_battle_mode:  # Switching sides only makes sense in Player vs AI
            self.player_color = not self.player_color
            self.new_game()  # This will set up turns correctly
        else:
            self.status_text = "Cannot switch sides in AI vs Stockfish mode."

    def cycle_difficulty(self):
        difficulties = ["Easy", "Medium", "Hard", "Very Hard"]
        try:
            current_index = difficulties.index(self.difficulty)
        except ValueError:
            current_index = 1  # Default to medium if somehow not in list
        next_index = (current_index + 1) % len(difficulties)
        self.difficulty = difficulties[next_index]

        depth_map = {"Easy": 2, "Medium": 3, "Hard": 4, "Very Hard": 5}
        # Stockfish strength for AI opponent in Player vs AI (if SF is used for AI)
        sf_strength_map = {"Easy": 5, "Medium": 10, "Hard": 15, "Very Hard": 20}

        self.ai.set_depth(depth_map[self.difficulty])
        # This strength is for when internal AI uses SF as its engine (Player vs AI, use_stockfish=True)
        # It's separate from stockfish_level for SF battle mode.
        # Let's assume ChessAI().set_stockfish_strength applies to its own engine usage
        self.ai.set_stockfish_strength(sf_strength_map[self.difficulty])

        self.status_text = f"Difficulty: {self.difficulty} (Depth: {self.ai.depth})"
        # If currently playing, might want to restart or apply immediately if AI's turn
        if not self.stockfish_battle_mode and self.ai.board.turn != self.player_color:  # If AI's turn
            self.need_ai_move = True  # Let AI re-evaluate with new difficulty

    def toggle_stockfish_battle(self):
        self.stockfish_battle_mode = not self.stockfish_battle_mode
        self.new_game()  # Reset and setup based on new mode

    def run(self):
        ai_vs_ai_delay = 700  # Milliseconds between moves in AI vs AI mode

        while self.running:
            current_time = pygame.time.get_ticks()

            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        if self.game_state == "START_SCREEN":
                            self.handle_start_screen_click(event.pos)
                        elif self.game_state == "PLAYING":
                            # Xử lý click khi đang chơi
                            old_need_ai_move = self.need_ai_move
                            self.handle_click(event.pos)
                            
                            # Nếu trạng thái chuyển từ lượt người chơi sang lượt AI, cập nhật ngay giao diện
                            if not old_need_ai_move and self.need_ai_move:
                                self.draw_board()
                                self.update_game_status()
                                pygame.display.update()
                        elif self.game_state == "INSTRUCTIONS":
                            self.handle_instruction_screen_click(event.pos)
                elif event.type == KEYDOWN:  # Optional: ESC to go to start screen
                    if event.key == K_ESCAPE:
                        if self.game_state == "PLAYING" or self.game_state == "INSTRUCTIONS":
                            self.game_state = "START_SCREEN"

            if self.game_state == "START_SCREEN":
                self.draw_start_screen()
            elif self.game_state == "INSTRUCTIONS":
                self.draw_instruction_screen()
            elif self.game_state == "PLAYING":
                self.draw_board()

                if not self.ai.board.is_game_over():
                    if self.stockfish_battle_mode:
                        if current_time - self.last_ai_move_time > ai_vs_ai_delay:
                            # Cập nhật giao diện trước khi AI di chuyển
                            self.status_text = "AI is thinking..."
                            self.draw_board()
                            pygame.display.update()
                            
                            # Thực hiện nước đi của AI
                            self.make_ai_move()
                            self.last_ai_move_time = current_time
                    elif self.need_ai_move:  # Player vs AI, AI's turn
                        # Cập nhật giao diện để hiển thị trạng thái "AI đang suy nghĩ"
                        self.status_text = "AI is thinking..."
                        self.draw_board()
                        pygame.display.update()
                        
                        # Thực hiện nước đi của AI
                        self.make_ai_move()
                
                # Cập nhật trạng thái game
                if not self.ai.board.is_game_over() and not self.need_ai_move:
                    self.update_game_status()

            pygame.display.update()
            self.clock.tick(60)

        pygame.quit()