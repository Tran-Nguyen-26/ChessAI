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

        button_width = 100
        button_height = 30
        button_spacing = 10
        start_x = self.margin
        total_buttons_width = 5 * (button_width + button_spacing) + 20 + 100
        required_width = max(self.board_size + 2 * self.margin, total_buttons_width + 2 * self.margin)
        self.window_size = (required_width, self.board_size + self.margin * 2 + 100)

        # Modified line: Added pygame.DOUBLEBUF
        self.screen = pygame.display.set_mode(self.window_size, pygame.DOUBLEBUF)
        pygame.display.set_caption("ChessAI")

        self.clock = pygame.time.Clock()
        # For potentially better text, ensure you have a good quality "Arial" or consider
        # pygame.font.Font("your_custom_font.ttf", 14) if you bundle a font.

        try:
            self.font = pygame.font.Font("assets/fonts/Roboto-Regular.ttf", 14)
            self.status_font = pygame.font.Font("assets/fonts/Roboto-Medium.ttf", 16)
            self.title_font = pygame.font.Font("assets/fonts/Roboto-Bold.ttf", 24)
        except:
            # Fallback nếu không tìm thấy font
            self.font = pygame.font.SysFont("Arial", 14)
            self.status_font = pygame.font.SysFont("Arial", 16)
            self.title_font = pygame.font.SysFont("Arial", 24, bold=True)
        self.ai = ChessAI(depth=3)  # Assuming ChessAI class is defined elsewhere

        self.selected_square = None
        self.possible_moves = []
        self.player_color = chess.WHITE  # Assuming chess module is imported

        self.status_text = "Your turn (White pieces)"
        self.difficulty = "Medium"
        self.ai_thinking_time = 0  # Thời gian AI suy nghĩ

        self.load_images()

        self.new_game_btn = pygame.Rect(start_x, self.board_size + self.margin + 20, button_width, button_height)
        self.switch_sides_btn = pygame.Rect(start_x + button_width + button_spacing, self.board_size + self.margin + 20,
                                            button_width, button_height)
        self.difficulty_btn = pygame.Rect(start_x + 2 * (button_width + button_spacing),
                                          self.board_size + self.margin + 20, button_width, button_height)

        self.running = True
        self.need_ai_move = False

        self.use_stockfish = True
        self.stockfish_btn = pygame.Rect(start_x + 3 * (button_width + button_spacing),
                                         self.board_size + self.margin + 20, button_width, button_height)
        self.stockfish_battle_btn = pygame.Rect(start_x + 4 * (button_width + button_spacing),
                                                self.board_size + self.margin + 20, button_width + 20, button_height)
        self.stockfish_slider = pygame.Rect(start_x + 5 * (button_width + button_spacing) + 20,
                                            self.board_size + self.margin + 20, 100, button_height)
        self.stockfish_battle_mode = False
        self.stockfish_level = 10
        self.last_ai_move_time = 0

    def load_images(self):
        self.piece_images = {}
        try:
            pieces_image = pygame.image.load("assets/images/Chess_Pieces.png")
            # For optimal quality, ensure Chess_Pieces.png is high resolution.
            # If it has a specific background color instead of transparency, you might need:
            # pieces_image.set_colorkey(COLOR_KEY_OF_BACKGROUND)
            piece_width = pieces_image.get_width() // 6
            piece_height = pieces_image.get_height() // 2
            piece_types = ['K', 'Q', 'B', 'N', 'R', 'P']
            for i, piece_type in enumerate(piece_types):
                x = i * piece_width
                white_piece_surf = pieces_image.subsurface((x, 0, piece_width, piece_height))
                # Modified line: Used smoothscale
                self.piece_images[piece_type] = pygame.transform.smoothscale(white_piece_surf,
                                                                             (self.square_size, self.square_size))

                black_piece_surf = pieces_image.subsurface((x, piece_height, piece_width, piece_height))
                # Modified line: Used smoothscale
                self.piece_images[piece_type.lower()] = pygame.transform.smoothscale(black_piece_surf,
                                                                                     (self.square_size,
                                                                                      self.square_size))
        except pygame.error as e:  # Catch specific error and print it
            print(f"Không thể tải hình ảnh quân cờ: {e}. Sử dụng hình ảnh mặc định.")
            self.create_default_piece_images()

    def create_default_piece_images(self):
        piece_types = ['K', 'Q', 'B', 'N', 'R', 'P']
        # Consider using a font object created once if performance is critical,
        # but for setup, this is fine.
        # Using pygame.font.Font(None, 24) might give a more consistent default look
        # if Arial is not available or looks poor on some systems.
        piece_font = pygame.font.SysFont("Arial", self.square_size // 3)  # Adjusted font size relative to square_size

        for piece_type in piece_types:
            # White piece
            white_img = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
            white_img.fill((0, 0, 0, 0))  # Ensure transparent background
            pygame.draw.circle(white_img, (220, 220, 220), (self.square_size // 2, self.square_size // 2),
                               int(self.square_size // 2.8))  # Slightly smaller circle
            pygame.draw.circle(white_img, (180, 180, 180), (self.square_size // 2, self.square_size // 2),
                               int(self.square_size // 2.8), 2)  # Outline
            self.piece_images[piece_type] = white_img

            # Black piece
            black_img = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
            black_img.fill((0, 0, 0, 0))  # Ensure transparent background
            pygame.draw.circle(black_img, (50, 50, 50), (self.square_size // 2, self.square_size // 2),
                               int(self.square_size // 2.8))  # Slightly smaller circle
            pygame.draw.circle(black_img, (80, 80, 80), (self.square_size // 2, self.square_size // 2),
                               int(self.square_size // 2.8), 2)  # Outline
            self.piece_images[piece_type.lower()] = black_img

            # Render text (already antialiased by default with the 'True' flag)
            # Text color black for white pieces, white for black pieces for contrast
            white_text_surf = piece_font.render(piece_type, True, (0, 0, 0))
            black_text_surf = piece_font.render(piece_type, True, (255, 255, 255))

            # Center text on the images
            wt_rect = white_text_surf.get_rect(center=(self.square_size // 2, self.square_size // 2))
            bt_rect = black_text_surf.get_rect(center=(self.square_size // 2, self.square_size // 2))

            white_img.blit(white_text_surf, wt_rect.topleft)
            black_img.blit(black_text_surf, bt_rect.topleft)

    def draw_board(self):
        self.screen.fill((240, 240, 240))  # Light gray background

        # Board background and squares
        board_surface_x = self.margin
        board_surface_y = self.margin

        for row in range(8):
            for col in range(8):
                x = col * self.square_size + board_surface_x
                y = row * self.square_size + board_surface_y

                # Standard chess board colors
                light_square_color = (240, 217, 181)  # Beige
                dark_square_color = (181, 136, 99)  # Brown

                current_color = light_square_color if (row + col) % 2 == 0 else dark_square_color

                square = chess.square(col, 7 - row)  # chess.square(file, rank)

                if square == self.selected_square:
                    current_color = (135, 167, 255)  # Light blue for selected
                elif square in self.possible_moves:
                    # Differentiate highlight for light/dark squares
                    if (row + col) % 2 == 0:  # Light square
                        current_color = (170, 255, 153)  # Light green highlight
                    else:  # Dark square
                        current_color = (136, 204, 119)  # Darker green highlight

                pygame.draw.rect(self.screen, current_color, (x, y, self.square_size, self.square_size))

                # Draw rank/file labels (subtly, and only once)
                label_color = (50, 50, 50)  # Dark gray for labels
                if row == 7:  # Bottom row for file names (a-h)
                    text_surf = self.font.render(chess.FILE_NAMES[col], True, label_color)
                    # Position bottom-right of the square
                    self.screen.blit(text_surf, (x + self.square_size - text_surf.get_width() - 5,
                                                 y + self.square_size - text_surf.get_height() - 2))
                if col == 0:  # Leftmost column for rank names (1-8)
                    text_surf = self.font.render(chess.RANK_NAMES[7 - row], True, label_color)
                    # Position top-left of the square
                    self.screen.blit(text_surf, (x + 3, y + 2))

        # Draw pieces
        for square_idx in chess.SQUARES:
            piece = self.ai.board.piece_at(square_idx)
            if piece:
                col = chess.square_file(square_idx)
                row = 7 - chess.square_rank(square_idx)  # Pygame Y is inverted from chess rank

                piece_rect = pygame.Rect(
                    col * self.square_size + board_surface_x,
                    row * self.square_size + board_surface_y,
                    self.square_size,
                    self.square_size
                )
                piece_symbol = piece.symbol()
                if piece_symbol in self.piece_images:
                    self.screen.blit(self.piece_images[piece_symbol], piece_rect)

        # --- UI Elements ---
        button_color = (220, 220, 220)
        button_hover_color = (200, 200, 200)
        text_color = (0, 0, 0)

        buttons = [
            (self.new_game_btn, "New Game"),
            (self.switch_sides_btn, "Switch Sides"),
            (self.difficulty_btn, f"Diff: {self.difficulty}"),
            (self.stockfish_btn, f"SF: {'On' if self.use_stockfish else 'Off'}"),
            (self.stockfish_battle_btn, "VS Stockfish")
        ]

        mouse_pos = pygame.mouse.get_pos()

        for rect, text_content in buttons:
            current_button_color = button_hover_color if rect.collidepoint(mouse_pos) else button_color
            pygame.draw.rect(self.screen, current_button_color, rect, border_radius=5)  # Rounded corners
            pygame.draw.rect(self.screen, (150, 150, 150), rect, width=1, border_radius=5)  # Outline

            btn_text_surf = self.font.render(text_content, True, text_color)
            text_rect = btn_text_surf.get_rect(center=rect.center)
            self.screen.blit(btn_text_surf, text_rect.topleft)

        # Stockfish Level Slider (if in battle mode)
        if self.stockfish_battle_mode:
            slider_bg_color = (220, 220, 220)
            slider_bar_color = (100, 100, 255)
            handle_width = 10  # Width of the draggable part of the slider

            pygame.draw.rect(self.screen, slider_bg_color, self.stockfish_slider, border_radius=5)  # Background
            pygame.draw.rect(self.screen, (150, 150, 150), self.stockfish_slider, width=1, border_radius=5)  # Outline

            # Calculate handle position based on stockfish_level (1-20)
            # Slider track width: self.stockfish_slider.w - handle_width
            # Position for level 1: self.stockfish_slider.x
            # Position for level 20: self.stockfish_slider.x + self.stockfish_slider.w - handle_width
            level_percentage = (self.stockfish_level - 1) / (20 - 1)  # Max level is 20 for Stockfish
            handle_x = self.stockfish_slider.x + level_percentage * (self.stockfish_slider.w - handle_width)

            handle_rect = pygame.Rect(handle_x, self.stockfish_slider.y, handle_width, self.stockfish_slider.h)
            pygame.draw.rect(self.screen, slider_bar_color, handle_rect, border_radius=3)  # Handle

            level_text_surf = self.font.render(f"Lvl: {self.stockfish_level}", True, text_color)
            level_text_rect = level_text_surf.get_rect(center=self.stockfish_slider.center)
            # Adjust if text overlaps too much with handle, e.g., place it to one side or above/below
            self.screen.blit(level_text_surf, (self.stockfish_slider.right + 10,
                                               self.stockfish_slider.centery - level_text_surf.get_height() // 2))

        # Mode and Status Text
        if self.stockfish_battle_mode:
            mode_text_surf = self.status_font.render("Mode: Internal AI vs Stockfish", True, (0, 100, 0))  # Green text
            self.screen.blit(mode_text_surf, (self.margin, self.board_size + self.margin + 60))

        status_display_text = f"{self.status_text} (AI Time: {self.ai_thinking_time:.2f}s)"
        status_text_surf = self.status_font.render(status_display_text, True, (0, 0, 0))  # Black text
        self.screen.blit(status_text_surf, (self.margin,
                                            self.margin // 2 - status_text_surf.get_height() // 2))  # Center vertically in top margin

        # pygame.display.flip() # This should be in your main game loop

    def handle_click(self, pos):
        x, y = pos
        if self.new_game_btn.collidepoint(x, y):
            self.new_game()
        elif self.switch_sides_btn.collidepoint(x, y):
            self.switch_sides()
        elif self.difficulty_btn.collidepoint(x, y):
            self.cycle_difficulty()
        elif self.stockfish_btn.collidepoint(x, y):
            self.toggle_stockfish()
        elif self.stockfish_battle_btn.collidepoint(x, y):
            self.toggle_stockfish_battle()
        elif self.stockfish_battle_mode and self.stockfish_slider.collidepoint(x, y):
            self.stockfish_level = min(20, max(1, int((x - self.stockfish_slider.x) / 5)))
            self.ai.set_stockfish_strength(self.stockfish_level)

        if x < self.margin or x > self.board_size + self.margin or y < self.margin or y > self.board_size + self.margin:
            return

        if self.ai.board.is_game_over() or self.ai.board.turn != self.player_color:
            return

        col = (x - self.margin) // self.square_size
        row = (y - self.margin) // self.square_size
        square = chess.square(col, 7 - row)

        if self.selected_square is None:
            piece = self.ai.board.piece_at(square)
            if piece and piece.color == self.player_color:
                self.selected_square = square
                self.possible_moves = [move.to_square for move in self.ai.board.legal_moves
                                    if move.from_square == square]
        else:
            move = chess.Move(self.selected_square, square)
            if self.ai.board.piece_at(self.selected_square) and \
               self.ai.board.piece_at(self.selected_square).piece_type == chess.PAWN and \
               ((self.player_color == chess.WHITE and chess.square_rank(square) == 7) or \
                (self.player_color == chess.BLACK and chess.square_rank(square) == 0)):
                move = chess.Move(self.selected_square, square, promotion=chess.QUEEN)

            if move in self.ai.board.legal_moves:
                self.ai.board.push(move)
                self.status_text = "Thinking..."
                self.selected_square = None
                self.possible_moves = []
                self.need_ai_move = True
            else:
                piece = self.ai.board.piece_at(square)
                if piece and piece.color == self.player_color:
                    self.selected_square = square
                    self.possible_moves = [move.to_square for move in self.ai.board.legal_moves
                                         if move.from_square == square]
                else:
                    self.selected_square = None
                    self.possible_moves = []

    def toggle_stockfish(self):
        self.use_stockfish = not self.use_stockfish
        self.ai.toggle_stockfish(self.use_stockfish)
        status = "On" if self.use_stockfish else "Off"
        self.status_text = f"Stockfish engine is {status}"

    def make_ai_move(self):
        if self.ai.board.is_game_over():
            return
        start_time = time.time()
        ai_move = self.ai.get_ai_move()
        self.ai_thinking_time = time.time() - start_time
        if ai_move:
            self.ai.board.push(ai_move)
            move_text = ai_move.uci()
            if self.stockfish_battle_mode:
                self.status_text = f"AI played: {move_text}"
            else:
                self.status_text = f"AI played: {move_text}. Your turn."
        self.need_ai_move = False
        self.update_game_status()

    def update_game_status(self):
        if self.ai.board.is_checkmate():
            winner = "White" if not self.ai.board.turn else "Black"
            self.status_text = f"Checkmate! {winner} wins"
            self.show_game_over_message(f"Checkmate! {winner} wins")
            self.new_game()
        elif self.ai.board.is_stalemate():
            self.status_text = "Stalemate!"
            self.show_game_over_message("Stalemate!")
            self.new_game()
        elif self.ai.board.is_insufficient_material():
            self.status_text = "Draw by insufficient material!"
            self.show_game_over_message("Draw by insufficient material!")
            self.new_game()
        elif self.ai.board.is_check():
            self.status_text = "Check! " + ("White" if self.ai.board.turn else "Black") + " to move"

    def show_game_over_message(self, message):
        overlay = pygame.Surface(self.window_size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        font = pygame.font.SysFont("Arial", 32)
        text = font.render(message, True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.window_size[0]//2, self.window_size[1]//2))
        self.screen.blit(text, text_rect)
        pygame.display.update()
        pygame.time.wait(2000)

    def new_game(self):
        self.ai.reset_board()
        self.selected_square = None
        self.possible_moves = []
        self.last_ai_move_time = pygame.time.get_ticks()
        if self.stockfish_battle_mode:
            self.status_text = f"Internal AI vs Stockfish (Level {self.stockfish_level})"
        else:
            self.status_text = "New game! " + ("You" if self.player_color == chess.WHITE else "AI") + " goes first (White pieces)"
        self.need_ai_move = (self.ai.board.turn != self.player_color)

    def switch_sides(self):
        self.player_color = not self.player_color
        self.new_game()

    def cycle_difficulty(self):
        difficulties = ["Easy", "Medium", "Hard", "Very Hard"]
        current_index = difficulties.index(self.difficulty)
        next_index = (current_index + 1) % len(difficulties)
        self.difficulty = difficulties[next_index]
        if self.difficulty == "Easy":
            self.ai.depth = 2
            self.ai.set_stockfish_strength(5)
        elif self.difficulty == "Medium":
            self.ai.depth = 3
            self.ai.set_stockfish_strength(10)
        elif self.difficulty == "Hard":
            self.ai.depth = 4
            self.ai.set_stockfish_strength(15)
        elif self.difficulty == "Very Hard":
            self.ai.depth = 5
            self.ai.set_stockfish_strength(10)
        self.status_text = f"Difficulty set: {self.difficulty}"

    def toggle_stockfish_battle(self):
        self.stockfish_battle_mode = not self.stockfish_battle_mode
        if self.stockfish_battle_mode:
            self.status_text = f"Internal AI vs Stockfish (Level {self.stockfish_level})"
            self.ai.toggle_stockfish_opponent(True)
            self.ai.set_stockfish_strength(self.stockfish_level)
            self.player_color = chess.WHITE
        else:
            self.status_text = "Stockfish battle mode - Off"
            self.ai.toggle_stockfish_opponent(False)

    def run(self):
        ai_move_delay = 500
        while self.running:
            current_time = pygame.time.get_ticks()
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.handle_click(event.pos)

            self.draw_board()
            pygame.display.update()

            if self.stockfish_battle_mode and not self.ai.board.is_game_over():
                if current_time - self.last_ai_move_time > ai_move_delay:
                    self.make_ai_move()
                    self.last_ai_move_time = current_time
            elif self.need_ai_move:
                pygame.time.wait(100)
                self.make_ai_move()

            self.update_game_status()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()