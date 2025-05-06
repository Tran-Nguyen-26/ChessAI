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
        self.window_size = (self.board_size + self.margin * 2, 
                       self.board_size + self.margin * 2 + 100)  # Tăng từ 60 lên 100 # Thêm không gian cho controls
        
        # Tạo các button với vị trí mới
        button_width = 100
        button_height = 30
        button_spacing = 10
        start_x = self.margin

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
        self.switch_sides_btn = pygame.Rect(start_x + button_width + button_spacing, self.board_size + self.margin + 20, button_width, button_height)
        self.difficulty_btn = pygame.Rect(start_x + 2*(button_width + button_spacing), self.board_size + self.margin + 20, button_width + 20, button_height)
        
        # Vòng lặp chính của game
        self.running = True
        self.need_ai_move = False

        # Thêm biến và UI cho Stockfish
        self.use_stockfish = True  # Mặc định sử dụng Stockfish nếu có
        # Thêm nút bật/tắt Stockfish
        self.stockfish_btn = pygame.Rect(start_x + 3*(button_width + button_spacing) + 20, self.board_size + self.margin + 20, button_width + 20, button_height)
        # Thêm biến kiểm soát chế độ AI vs AI
        self.ai_vs_ai_mode = False
        self.ai_vs_ai_paused = False
    
        # Thêm nút điều khiển
        self.ai_vs_ai_btn = pygame.Rect(start_x + 4*(button_width + button_spacing) + 40, self.board_size + self.margin + 20, button_width, button_height)
        self.ai_vs_ai_pause_btn = pygame.Rect(start_x, self.board_size + self.margin + 20 + button_height + 10, button_width, button_height)
        
    def load_images(self):
        """Tải hình ảnh các quân cờ"""
        self.piece_images = {}
        
        # Tải hình ảnh quân cờ từ file
        try:
            pieces_image = pygame.image.load("ChessAI/assets/images/Chess_Pieces.png")
            
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
                self.piece_images[piece_type] = pygame.transform.scale(white_piece, (self.square_size, self.square_size))
                
                # Đen ở hàng dưới
                black_piece = pieces_image.subsurface((x, piece_height, piece_width, piece_height))
                self.piece_images[piece_type.lower()] = pygame.transform.scale(black_piece, (self.square_size, self.square_size))
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
            pygame.draw.circle(white_img, (255, 255, 255), (self.square_size//2, self.square_size//2), self.square_size//3)
            self.piece_images[piece_type] = white_img
            
            # Tạo hình ảnh đơn giản cho quân đen
            black_img = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
            pygame.draw.circle(black_img, (0, 0, 0), (self.square_size//2, self.square_size//2), self.square_size//3)
            self.piece_images[piece_type.lower()] = black_img
            
            # Thêm text để phân biệt các loại quân
            font = pygame.font.SysFont("Arial", 24)
            white_text = font.render(piece_type, True, (0, 0, 0))
            black_text = font.render(piece_type, True, (255, 255, 255))
            
            # Vẽ text vào hình ảnh
            white_img.blit(white_text, (self.square_size//2 - white_text.get_width()//2, 
                                        self.square_size//2 - white_text.get_height()//2))
            black_img.blit(black_text, (self.square_size//2 - black_text.get_width()//2,
                                        self.square_size//2 - black_text.get_height()//2))
    
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
                    color = (170, 255, 153) if (row + col) % 2 == 0 else (136, 204, 119)  # Màu xanh lá cho nước đi hợp lệ
                
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
        pygame.draw.rect(self.screen, (200, 200, 200), self.new_game_btn)
        pygame.draw.rect(self.screen, (200, 200, 200), self.switch_sides_btn)
        pygame.draw.rect(self.screen, (200, 200, 200), self.difficulty_btn)
        pygame.draw.rect(self.screen, (200, 200, 200), self.stockfish_btn)
        pygame.draw.rect(self.screen, (200, 200, 200), self.ai_vs_ai_btn)
        
        # Vẽ text cho các button hàng 1
        new_game_text = self.font.render("New game", True, (0, 0, 0))
        switch_sides_text = self.font.render("Switch sides", True, (0, 0, 0))
        difficulty_text = self.font.render(f"Difficulty: {self.difficulty[:1]}", True, (0, 0, 0))  # Rút gọn thành "M" thay vì "Medium"
        stockfish_text = self.font.render(f"SF: {'On' if self.use_stockfish else 'Off'}", True, (0, 0, 0))  # Rút gọn "Stockfish" thành "SF"
        ai_vs_ai_text = self.font.render("AI vs AI", True, (0, 0, 0))
        
        self.screen.blit(new_game_text, (self.new_game_btn.x + 10, self.new_game_btn.y + 8))
        self.screen.blit(switch_sides_text, (self.switch_sides_btn.x + 10, self.switch_sides_btn.y + 8))
        self.screen.blit(difficulty_text, (self.difficulty_btn.x + 10, self.difficulty_btn.y + 8))
        self.screen.blit(stockfish_text, (self.stockfish_btn.x + 10, self.stockfish_btn.y + 8))
        self.screen.blit(ai_vs_ai_text, (self.ai_vs_ai_btn.x + 10, self.ai_vs_ai_btn.y + 8))
    
        # Vẽ button Pause/Resume ở hàng 2 (chỉ khi ở chế độ AI vs AI)
        if self.ai_vs_ai_mode:
            pygame.draw.rect(self.screen, (200, 200, 200), self.ai_vs_ai_pause_btn)
            pause_text = self.font.render("Pause" if not self.ai_vs_ai_paused else "Resume", True, (0, 0, 0))
            self.screen.blit(pause_text, (self.ai_vs_ai_pause_btn.x + 10, self.ai_vs_ai_pause_btn.y + 8))

        # Vẽ trạng thái
        status_text = self.status_font.render(self.status_text, True, (0, 0, 0))
        self.screen.blit(status_text, (self.margin, self.margin // 2))

    
    def handle_click(self, pos):
        """Xử lý sự kiện khi người dùng nhấn chuột"""
        x, y = pos
        
        # Kiểm tra các button
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
            self.toggle_stockfish()
            return
        elif self.ai_vs_ai_btn.collidepoint(x, y):
            self.toggle_ai_vs_ai()
            return
        elif self.ai_vs_ai_pause_btn.collidepoint(x, y):
            self.toggle_ai_vs_ai_pause()
            return
        
        # Kiểm tra button ở hàng 2 (nếu có)
        if self.ai_vs_ai_mode and self.ai_vs_ai_pause_btn.collidepoint(x, y):
            self.toggle_ai_vs_ai_pause()
            return
            
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
            
            # Cập nhật thông báo khác nhau tùy chế độ
            if self.ai_vs_ai_mode:
                player = "White" if self.ai.board.turn == chess.BLACK else "Black"
                self.status_text = f"AI {player} played: {move_text}"
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
        text_rect = text.get_rect(center=(self.window_size[0]//2, self.window_size[1]//2))
        self.screen.blit(text, text_rect)
        
        pygame.display.update()
        pygame.time.wait(2000)  # Chờ 2 giây
    
    def new_game(self):
        """Bắt đầu game mới"""
        self.ai.reset_board()
        self.selected_square = None
        self.possible_moves = []
        
        if self.ai_vs_ai_mode:
            self.status_text = "AI vs AI - New game started"
        else:
            self.status_text = "New game! " + ("You" if self.player_color == chess.WHITE else "AI") + " goes first (White pieces)"
        
        # Nếu AI đi trước hoặc đang ở chế độ AI vs AI
        if self.ai.board.turn != self.player_color or self.ai_vs_ai_mode:
            self.need_ai_move = True
    
    def switch_sides(self):
        """Đổi bên chơi"""
        if not self.ai_vs_ai_mode:
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
    def toggle_ai_vs_ai(self):
        """Bật/tắt chế độ AI đấu với AI"""
        self.ai_vs_ai_mode = not self.ai_vs_ai_mode
        if self.ai_vs_ai_mode:
            self.status_text = "AI vs AI mode - Running"
            self.player_color = None  # Không có người chơi
        else:
            self.status_text = "AI vs AI mode - Off"
            self.player_color = chess.WHITE  # Trở lại chế độ người chơi

    def toggle_ai_vs_ai_pause(self):
        """Tạm dừng/tiếp tục chế độ AI vs AI"""
        if self.ai_vs_ai_mode:
            self.ai_vs_ai_paused = not self.ai_vs_ai_paused
            self.status_text = "AI vs AI mode - " + ("Paused" if self.ai_vs_ai_paused else "Running")
    
    
    def run(self):
        """Vòng lặp chính của game"""
        ai_move_delay = 500  # Thời gian chờ giữa các nước đi AI (ms)
        last_ai_move_time = 0
        while self.running:
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
            
            # Xử lý AI vs AI mode
            if self.ai_vs_ai_mode and not self.ai_vs_ai_paused and not self.ai.board.is_game_over():
                if current_time - last_ai_move_time > ai_move_delay:
                    self.make_ai_move()
                    last_ai_move_time = current_time
            # Xử lý chế độ bình thường
            elif self.need_ai_move:
                pygame.time.wait(500)  # Chờ một chút để người chơi thấy được nước đi của họ
                self.make_ai_move()
            
            # Cập nhật trạng thái game
            self.update_game_status()
            
            # Giới hạn FPS
            self.clock.tick(30)
        
        pygame.quit()
        sys.exit()
