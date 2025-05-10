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
        total_buttons_width = 5*(button_width + button_spacing) + 20 + 100
        required_width = max(self.board_size + 2*self.margin, total_buttons_width + 2*self.margin)
        self.window_size = (required_width, self.board_size + self.margin * 2 + 100)

        self.screen = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption("ChessAI")
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 14)
        self.status_font = pygame.font.SysFont("Arial", 16)
        
        self.ai = ChessAI(depth=3)
        
        self.selected_square = None
        self.possible_moves = []
        self.player_color = chess.WHITE
        
        self.status_text = "Your turn (White pieces)"
        self.difficulty = "Medium"
        self.ai_thinking_time = 0  # Thời gian AI suy nghĩ
        
        self.load_images()
        
        self.new_game_btn = pygame.Rect(start_x, self.board_size + self.margin + 20, button_width, button_height)
        self.switch_sides_btn = pygame.Rect(start_x + button_width + button_spacing, self.board_size + self.margin + 20, button_width, button_height)
        self.difficulty_btn = pygame.Rect(start_x + 2*(button_width + button_spacing), self.board_size + self.margin + 20, button_width, button_height)
        
        self.running = True
        self.need_ai_move = False

        self.use_stockfish = True
        self.stockfish_btn = pygame.Rect(start_x + 3*(button_width + button_spacing), self.board_size + self.margin + 20, button_width, button_height)
        self.stockfish_battle_btn = pygame.Rect(start_x + 4*(button_width + button_spacing), self.board_size + self.margin + 20, button_width + 20, button_height)
        self.stockfish_slider = pygame.Rect(start_x + 5*(button_width + button_spacing) + 20, self.board_size + self.margin + 20, 100, button_height)
        self.stockfish_battle_mode = False
        self.stockfish_level = 10
        self.last_ai_move_time = 0
        
    def load_images(self):
        self.piece_images = {}
        try:
            pieces_image = pygame.image.load("assets/images/Chess_Pieces.png")
            piece_width = pieces_image.get_width() // 6
            piece_height = pieces_image.get_height() // 2
            piece_types = ['K', 'Q', 'B', 'N', 'R', 'P']
            for i, piece_type in enumerate(piece_types):
                x = i * piece_width
                white_piece = pieces_image.subsurface((x, 0, piece_width, piece_height))
                self.piece_images[piece_type] = pygame.transform.scale(white_piece, (self.square_size, self.square_size))
                black_piece = pieces_image.subsurface((x, piece_height, piece_width, piece_height))
                self.piece_images[piece_type.lower()] = pygame.transform.scale(black_piece, (self.square_size, self.square_size))
        except pygame.error:
            print("Không thể tải hình ảnh quân cờ. Sử dụng hình ảnh mặc định.")
            self.create_default_piece_images()

    def create_default_piece_images(self):
        piece_types = ['K', 'Q', 'B', 'N', 'R', 'P']
        for piece_type in piece_types:
            white_img = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
            pygame.draw.circle(white_img, (255, 255, 255), (self.square_size//2, self.square_size//2), self.square_size//3)
            self.piece_images[piece_type] = white_img
            black_img = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
            pygame.draw.circle(black_img, (0, 0, 0), (self.square_size//2, self.square_size//2), self.square_size//3)
            self.piece_images[piece_type.lower()] = black_img
            font = pygame.font.SysFont("Arial", 24)
            white_text = font.render(piece_type, True, (0, 0, 0))
            black_text = font.render(piece_type, True, (255, 255, 255))
            white_img.blit(white_text, (self.square_size//2 - white_text.get_width()//2, 
                                        self.square_size//2 - white_text.get_height()//2))
            black_img.blit(black_text, (self.square_size//2 - black_text.get_width()//2,
                                        self.square_size//2 - black_text.get_height()//2))

    def draw_board(self):
        self.screen.fill((240, 240, 240))
        for row in range(8):
            for col in range(8):
                x = col * self.square_size + self.margin
                y = row * self.square_size + self.margin
                color = (240, 217, 181) if (row + col) % 2 == 0 else (181, 136, 99)
                square = chess.square(col, 7 - row)
                if square == self.selected_square:
                    color = (170, 170, 255)
                elif square in self.possible_moves:
                    color = (170, 255, 153) if (row + col) % 2 == 0 else (136, 204, 119)
                pygame.draw.rect(self.screen, color, (x, y, self.square_size, self.square_size))
                if row == 7:
                    text = self.font.render(chess.FILE_NAMES[col], True, (0, 0, 0))
                    self.screen.blit(text, (x + self.square_size - 15, y + self.square_size - 15))
                if col == 0:
                    text = self.font.render(chess.RANK_NAMES[7 - row], True, (0, 0, 0))
                    self.screen.blit(text, (x + 5, y + 5))
        
        for square in chess.SQUARES:
            piece = self.ai.board.piece_at(square)
            if piece:
                col = chess.square_file(square)
                row = 7 - chess.square_rank(square)
                x = col * self.square_size + self.margin
                y = row * self.square_size + self.margin
                piece_symbol = piece.symbol()
                if piece_symbol in self.piece_images:
                    self.screen.blit(self.piece_images[piece_symbol], (x, y))
        
        buttons = [
            (self.new_game_btn, "New game"),
            (self.switch_sides_btn, "Switch sides"),
            (self.difficulty_btn, f"Diff: {self.difficulty}"),
            (self.stockfish_btn, f"SF: {'On' if self.use_stockfish else 'Off'}"),
            (self.stockfish_battle_btn, "VS Stockfish")
        ]
        
        for rect, text in buttons:
            pygame.draw.rect(self.screen, (200, 200, 200), rect)
            btn_text = self.font.render(text, True, (0, 0, 0))
            self.screen.blit(btn_text, (rect.x + 10, rect.y + 8))
        
        if self.stockfish_battle_mode:
            pygame.draw.rect(self.screen, (200, 200, 200), self.stockfish_slider)
            pygame.draw.rect(self.screen, (100, 100, 255), 
                            (self.stockfish_slider.x + (self.stockfish_level-1)*5, 
                            self.stockfish_slider.y, 
                            10, self.stockfish_slider.h))
            level_text = self.font.render(f"Lvl: {self.stockfish_level}", True, (0, 0, 0))
            self.screen.blit(level_text, (self.stockfish_slider.x + 40, self.stockfish_slider.y + 8))

        if self.stockfish_battle_mode:
            mode_text = self.font.render("Mode: Internal AI vs Stockfish", True, (0, 100, 0))
            self.screen.blit(mode_text, (self.margin, self.board_size + self.margin + 60))

        status_text = self.status_font.render(f"{self.status_text} (AI Time: {self.ai_thinking_time:.2f}s)", True, (0, 0, 0))
        self.screen.blit(status_text, (self.margin, self.margin // 2))

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
        elif self.ai.board.is_stalemate():
            self.status_text = "Stalemate!"
            self.show_game_over_message("Stalemate!")
        elif self.ai.board.is_insufficient_material():
            self.status_text = "Draw by insufficient material!"
            self.show_game_over_message("Draw by insufficient material!")
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
            self.ai.set_stockfish_strength(20)
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