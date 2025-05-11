import chess
import time
import random
import pygame
import sys
from pygame.locals import *

# Giả định rằng module ai với ChessAI class đã được định nghĩa
from ai import ChessAI


class ChessGUI:
    def __init__(self):
        pygame.init()
        self.square_size = 80
        self.board_size = self.square_size * 8
        self.margin = 40  # Lề cho việc hiển thị tọa độ

        # Tạo các button với vị trí mới
        button_width = 100
        button_height = 30
        button_spacing = 10
        start_x = self.margin
        total_buttons_width = 5 * (button_width + button_spacing) + 20 + 100  # 5 nút + thanh trượt
        required_width = max(self.board_size + 2 * self.margin, total_buttons_width + 2 * self.margin)
        self.window_size = (required_width, self.board_size + self.margin * 2 + 100)

        self.screen = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption("ChessAI")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 14)
        self.status_font = pygame.font.SysFont("Arial", 16)

        self.ai = ChessAI(depth=3)  # Khởi tạo AI với độ sâu mặc định

        self.selected_square = None
        self.possible_moves = []
        self.player_color = chess.WHITE  # Mặc định người chơi quân trắng

        self.status_text = "Your turn (White pieces)"
        self.difficulty = "Medium"

        # Tải hình ảnh quân cờ
        self.load_images()

        # Tạo các button
        self.new_game_btn = pygame.Rect(start_x, self.board_size + self.margin + 20, button_width, button_height)
        self.switch_sides_btn = pygame.Rect(start_x + button_width + button_spacing, self.board_size + self.margin + 20,
                                            button_width, button_height)
        self.difficulty_btn = pygame.Rect(start_x + 2 * (button_width + button_spacing),
                                          self.board_size + self.margin + 20, button_width, button_height)

        # Vòng lặp chính của game
        self.running = True
        self.need_ai_move = False

        # Thêm biến và UI cho Stockfish
        self.use_stockfish = True  # Mặc định sử dụng Stockfish nếu có
        # Thêm nút bật/tắt Stockfish
        self.stockfish_btn = pygame.Rect(start_x + 3 * (button_width + button_spacing),
                                         self.board_size + self.margin + 20, button_width, button_height)

        # Thêm nút và biến cho chế độ đấu với Stockfish
        self.stockfish_battle_btn = pygame.Rect(start_x + 4 * (button_width + button_spacing),
                                                self.board_size + self.margin + 20, button_width + 20, button_height)
        self.stockfish_slider = pygame.Rect(start_x + 5 * (button_width + button_spacing) + 20,
                                            self.board_size + self.margin + 20, 100, button_height)
        self.stockfish_battle_mode = False
        self.stockfish_level = 10  # Mức độ khó mặc định
        self.last_ai_move_time = 0  # Biến theo dõi thời gian nước đi AI cuối cùng

    def load_images(self):
        """Tải hình ảnh các quân cờ"""
        self.piece_images = {}

        # Tải hình ảnh quân cờ từ file
        try:
            pieces_image = pygame.image.load("assets/images/Chess_Pieces.png")

            # Kích thước mỗi quân cờ trong ảnh
            piece_width = pieces_image.get_width() // 6  # 6 quân cờ
            piece_height = pieces_image.get_height() // 2  # 2 màu

            # Các ký tự quân cờ theo thứ tự trong ảnh
            piece_types = ['K', 'Q', 'B', 'N', 'R', 'P']

            # Tạo ảnh con cho từng quân cờ
            for i, piece_type in enumerate(piece_types):
                x = i * piece_width
                # Trắng ở hàng trên (y=0)
                white_piece = pieces_image.subsurface((x, 0, piece_width, piece_height))
                self.piece_images[piece_type] = pygame.transform.scale(white_piece,
                                                                       (self.square_size, self.square_size))

                # Đen ở hàng dưới
                black_piece = pieces_image.subsurface((x, piece_height, piece_width, piece_height))
                self.piece_images[piece_type.lower()] = pygame.transform.scale(black_piece,
                                                                               (self.square_size, self.square_size))
        except pygame.error:
            # Nếu không tìm thấy file, tạo các hình ảnh mặc định
            print("Không thể tải hình ảnh quân cờ. Sử dụng hình ảnh mặc định.")
            self.create_default_piece_images()

    def create_default_piece_images(self):
        """Tạo hình ảnh mặc định cho quân cờ"""
        piece_types = ['K', 'Q', 'B', 'N', 'R', 'P']
        for piece_type in piece_types:
            # Tạo hình ảnh đơn giản cho quân trắng
            white_img = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
            pygame.draw.circle(white_img, (255, 255, 255), (self.square_size // 2, self.square_size // 2),
                               self.square_size // 3)
            self.piece_images[piece_type] = white_img

            # Tạo hình ảnh đơn giản cho quân đen
            black_img = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
            pygame.draw.circle(black_img, (0, 0, 0), (self.square_size // 2, self.square_size // 2),
                               self.square_size // 3)
            self.piece_images[piece_type.lower()] = black_img

            # Thêm text để phân biệt các loại quân
            font = pygame.font.SysFont("Arial", 24)
            white_text = font.render(piece_type, True, (0, 0, 0))
            black_text = font.render(piece_type, True, (255, 255, 255))

            # Vẽ text vào hình ảnh
            white_img.blit(white_text, (self.square_size // 2 - white_text.get_width() // 2,
                                        self.square_size // 2 - white_text.get_height() // 2))
            black_img.blit(black_text, (self.square_size // 2 - black_text.get_width() // 2,
                                        self.square_size // 2 - black_text.get_height() // 2))

    def draw_board(self):
        """Vẽ bàn cờ và các quân cờ"""
        # Vẽ nền
        self.screen.fill((240, 240, 240))

        # Vẽ các ô cờ
        for row in range(8):
            for col in range(8):
                x = col * self.square_size + self.margin
                y = row * self.square_size + self.margin

                # Màu ô cờ
                color = (240, 217, 181) if (row + col) % 2 == 0 else (181, 136, 99)  # Màu nâu/be truyền thống

                # Nếu ô này được chọn, đổi màu
                square = chess.square(col, 7 - row)
                if square == self.selected_square:
                    color = (170, 170, 255)  # Màu xanh cho ô được chọn
                elif square in self.possible_moves:
                    color = (170, 255, 153) if (row + col) % 2 == 0 else (136, 204,
                                                                          119)  # Màu xanh lá cho nước đi hợp lệ

                pygame.draw.rect(self.screen, color, (x, y, self.square_size, self.square_size))

                # Vẽ tọa độ
                if row == 7:
                    text = self.font.render(chess.FILE_NAMES[col], True, (0, 0, 0))
                    self.screen.blit(text, (x + self.square_size - 15, y + self.square_size - 15))
                if col == 0:
                    text = self.font.render(chess.RANK_NAMES[7 - row], True, (0, 0, 0))
                    self.screen.blit(text, (x + 5, y + 5))

        # Vẽ các quân cờ
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

        # Vẽ các button ở hàng 1
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

        # Vẽ thanh trượt độ khó Stockfish nếu đang bật chế độ
        if self.stockfish_battle_mode:
            pygame.draw.rect(self.screen, (200, 200, 200), self.stockfish_slider)
            pygame.draw.rect(self.screen, (100, 100, 255),
                             (self.stockfish_slider.x + (self.stockfish_level - 1) * 5,
                              self.stockfish_slider.y,
                              10, self.stockfish_slider.h))
            level_text = self.font.render(f"Lvl: {self.stockfish_level}", True, (0, 0, 0))
            self.screen.blit(level_text, (self.stockfish_slider.x + 40, self.stockfish_slider.y + 8))

        # Hiển thị trạng thái chế độ
        if self.stockfish_battle_mode:
            mode_text = self.font.render("Mode: Internal AI vs Stockfish", True, (0, 100, 0))
            self.screen.blit(mode_text, (self.margin, self.board_size + self.margin + 60))

        # Vẽ trạng thái
        status_text = self.status_font.render(self.status_text, True, (0, 0, 0))
        self.screen.blit(status_text, (self.margin, self.margin // 2))

    def handle_click(self, pos):
        """Xử lý sự kiện khi người dùng nhấn chuột"""
        x, y = pos

        # Kiểm tra các button
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
            # Xử lý thay đổi độ khó Stockfish
            self.stockfish_level = min(20, max(1, int((x - self.stockfish_slider.x) / 5)))
            self.ai.set_stockfish_strength(self.stockfish_level)

        # Kiểm tra nếu click vào bàn cờ
        if x < self.margin or x > self.board_size + self.margin or y < self.margin or y > self.board_size + self.margin:
            return

        # Nếu game đã kết thúc hoặc không phải lượt của người chơi
        if self.ai.board.is_game_over() or self.ai.board.turn != self.player_color:
            return

        # Tính toán ô được chọn
        col = (x - self.margin) // self.square_size
        row = (y - self.margin) // self.square_size
        square = chess.square(col, 7 - row)

        # Xử lý tương tự như trong phiên bản Tkinter
        if self.selected_square is None:
            piece = self.ai.board.piece_at(square)
            if piece and piece.color == self.player_color:
                self.selected_square = square
                self.possible_moves = [move.to_square for move in self.ai.board.legal_moves
                                       if move.from_square == square]
        else:
            # Thử thực hiện nước đi
            move = chess.Move(self.selected_square, square)

            # Kiểm tra phong hậu
            if self.ai.board.piece_at(self.selected_square) and \
                    self.ai.board.piece_at(self.selected_square).piece_type == chess.PAWN and \
                    ((self.player_color == chess.WHITE and chess.square_rank(square) == 7) or \
                     (self.player_color == chess.BLACK and chess.square_rank(square) == 0)):
                move = chess.Move(self.selected_square, square, promotion=chess.QUEEN)

            if move in self.ai.board.legal_moves:
                # Thực hiện nước đi của người chơi
                self.ai.board.push(move)
                self.status_text = "Thinking..."

                # Reset trạng thái chọn
                self.selected_square = None
                self.possible_moves = []

                # Đánh dấu cần thực hiện nước đi AI
                self.need_ai_move = True
            else:
                # Nếu nước đi không hợp lệ, chọn ô mới
                piece = self.ai.board.piece_at(square)
                if piece and piece.color == self.player_color:
                    self.selected_square = square
                    self.possible_moves = [move.to_square for move in self.ai.board.legal_moves
                                           if move.from_square == square]
                else:
                    self.selected_square = None
                    self.possible_moves = []

    # Thêm hàm mới để bật/tắt Stockfish
    def toggle_stockfish(self):
        """Bật/tắt sử dụng Stockfish"""
        self.use_stockfish = not self.use_stockfish
        self.ai.toggle_stockfish(self.use_stockfish)
        status = "On" if self.use_stockfish else "Off"
        self.status_text = f"Stockfish engine is {status}"

    def make_ai_move(self):
        """Để AI thực hiện nước đi"""
        if self.ai.board.is_game_over():
            return

        # Lấy nước đi từ AI
        ai_move = self.ai.get_ai_move()
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
        """Cập nhật trạng thái game"""
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
        """Hiển thị thông báo kết thúc game"""
        # Trong Pygame, chúng ta vẽ thông báo trực tiếp lên màn hình
        overlay = pygame.Surface(self.window_size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))

        font = pygame.font.SysFont("Arial", 32)
        text = font.render(message, True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.window_size[0] // 2, self.window_size[1] // 2))
        self.screen.blit(text, text_rect)

        pygame.display.update()
        pygame.time.wait(2000)  # Chờ 2 giây

    def new_game(self):
        """Bắt đầu game mới"""
        self.ai.reset_board()
        self.selected_square = None
        self.possible_moves = []
        self.last_ai_move_time = pygame.time.get_ticks()  # Reset thời gian
        if self.stockfish_battle_mode:
            self.status_text = f"Internal AI vs Stockfish (Level {self.stockfish_level})"
        else:
            self.status_text = "New game! " + (
                "You" if self.player_color == chess.WHITE else "AI") + " goes first (White pieces)"
        self.need_ai_move = (self.ai.board.turn != self.player_color)

    def switch_sides(self):
        """Đổi bên chơi"""
        self.player_color = not self.player_color
        self.new_game()

    def cycle_difficulty(self):
        """Thay đổi độ khó theo chu kỳ"""
        difficulties = ["Easy", "Medium", "Hard", "Very Hard"]
        current_index = difficulties.index(self.difficulty)
        next_index = (current_index + 1) % len(difficulties)
        self.difficulty = difficulties[next_index]

        # Cập nhật độ sâu cho AI
        if self.difficulty == "Easy":
            self.ai.depth = 2
            self.ai.set_stockfish_strength(5)  # Stockfish yếu
        elif self.difficulty == "Medium":
            self.ai.depth = 3
            self.ai.set_stockfish_strength(10)  # Stockfish trung bình
        elif self.difficulty == "Hard":
            self.ai.depth = 4
            self.ai.set_stockfish_strength(15)  # Stockfish khó
        elif self.difficulty == "Very Hard":
            self.ai.depth = 5
            self.ai.set_stockfish_strength(20)  # Stockfish rất khó

        self.status_text = f"Difficulty set: {self.difficulty}"

    def toggle_stockfish_battle(self):
        """Bật/tắt chế độ đấu với Stockfish"""
        self.stockfish_battle_mode = not self.stockfish_battle_mode
        if self.stockfish_battle_mode:
            self.status_text = f"Internal AI vs Stockfish (Level {self.stockfish_level})"
            self.ai.toggle_stockfish_opponent(True)
            self.ai.set_stockfish_strength(self.stockfish_level)
            self.player_color = chess.WHITE  # Người chơi điều khiển AI thuật toán
        else:
            self.status_text = "Stockfish battle mode - Off"
            self.ai.toggle_stockfish_opponent(False)

    def run(self):
        """Vòng lặp chính của game"""
        ai_move_delay = 500  # Thời gian chờ giữa các nước đi AI (ms)
        while self.running:
            # print(self.stockfish_level)
            # print(self.ai.depth)
            current_time = pygame.time.get_ticks()
            # Xử lý các sự kiện
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:  # Nút chuột trái
                        self.handle_click(event.pos)

            # Vẽ bàn cờ
            self.draw_board()
            pygame.display.update()

            # Xử lý nước đi AI (chỉ cho chế độ stockfish_battle_mode)
            if self.stockfish_battle_mode and not self.ai.board.is_game_over():
                if current_time - self.last_ai_move_time > ai_move_delay:
                    self.make_ai_move()
                    self.last_ai_move_time = current_time

            # Xử lý chế độ bình thường
            elif self.need_ai_move:
                pygame.time.wait(100)  # Chờ một chút để người chơi thấy được nước đi của họ
                self.make_ai_move()

            # Cập nhật trạng thái game
            self.update_game_status()

            # Giới hạn FPS
            self.clock.tick(60)

        pygame.quit()
        sys.exit()