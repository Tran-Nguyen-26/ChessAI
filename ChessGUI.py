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
        self.margin = 40
        self.window_size = (self.board_size + self.margin * 2, self.board_size + self.margin * 2 + 100)  # Tăng chiều cao để chứa thêm nút
        
        self.screen = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption("Cờ vua - AI vs Stockfish")
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 14)
        self.status_font = pygame.font.SysFont("Arial", 16)
        
        self.ai = ChessAI(depth=3)
        self.selected_square = None
        self.possible_moves = []
        self.player_color = chess.WHITE
        self.status_text = "Mời bạn đi trước (Quân trắng)"
        self.difficulty = "Trung bình"
        
        # Thêm biến cho chế độ AI vs Stockfish
        self.ai_vs_stockfish_mode = False
        self.ai_vs_stockfish_btn = pygame.Rect(self.margin + 370, self.board_size + self.margin + 20, 150, 30)
        self.stockfish_level_btn = pygame.Rect(self.margin, self.board_size + self.margin + 60, 150, 30)
        self.ai_level_btn = pygame.Rect(self.margin + 170, self.board_size + self.margin + 60, 150, 30)
        
        self.load_images()
        
        # Các button khác
        self.new_game_btn = pygame.Rect(self.margin, self.board_size + self.margin + 20, 100, 30)
        self.switch_sides_btn = pygame.Rect(self.margin + 120, self.board_size + self.margin + 20, 100, 30)
        self.difficulty_btn = pygame.Rect(self.margin + 240, self.board_size + self.margin + 20, 120, 30)
        
        self.running = True
        self.need_ai_move = False
        
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
        
        # Vẽ các button chính
        pygame.draw.rect(self.screen, (200, 200, 200), self.new_game_btn)
        pygame.draw.rect(self.screen, (200, 200, 200), self.switch_sides_btn)
        pygame.draw.rect(self.screen, (200, 200, 200), self.difficulty_btn)
        
        # Vẽ nút AI vs Stockfish với màu khác khi active
        btn_color = (170, 255, 170) if self.ai_vs_stockfish_mode else (200, 200, 200)
        pygame.draw.rect(self.screen, btn_color, self.ai_vs_stockfish_btn)
        
        # Vẽ text cho các button
        new_game_text = self.font.render("Game mới", True, (0, 0, 0))
        switch_sides_text = self.font.render("Đổi bên", True, (0, 0, 0))
        difficulty_text = self.font.render(f"Độ khó: {self.difficulty}", True, (0, 0, 0))
        ai_vs_sf_text = self.font.render("AI vs Stockfish", True, (0, 0, 0))
        
        self.screen.blit(new_game_text, (self.new_game_btn.x + 10, self.new_game_btn.y + 8))
        self.screen.blit(switch_sides_text, (self.switch_sides_btn.x + 10, self.switch_sides_btn.y + 8))
        self.screen.blit(difficulty_text, (self.difficulty_btn.x + 10, self.difficulty_btn.y + 8))
        self.screen.blit(ai_vs_sf_text, (self.ai_vs_stockfish_btn.x + 10, self.ai_vs_stockfish_btn.y + 8))
        
        # Vẽ các button điều chỉnh level khi ở chế độ AI vs Stockfish
        if self.ai_vs_stockfish_mode:
            pygame.draw.rect(self.screen, (200, 200, 200), self.stockfish_level_btn)
            pygame.draw.rect(self.screen, (200, 200, 200), self.ai_level_btn)
            
            sf_level_text = self.font.render(f"Stockfish: {self.ai.stockfish_skill_level}/20", True, (0, 0, 0))
            ai_level_text = self.font.render(f"AI Depth: {self.ai.depth}", True, (0, 0, 0))
            
            self.screen.blit(sf_level_text, (self.stockfish_level_btn.x + 10, self.stockfish_level_btn.y + 8))
            self.screen.blit(ai_level_text, (self.ai_level_btn.x + 10, self.ai_level_btn.y + 8))
        
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
        elif self.ai_vs_stockfish_btn.collidepoint(x, y):
            self.toggle_ai_vs_stockfish()
            return
        
        # Kiểm tra các button điều chỉnh level khi ở chế độ AI vs Stockfish
        if self.ai_vs_stockfish_mode:
            if self.stockfish_level_btn.collidepoint(x, y):
                self.adjust_stockfish_level()
                return
            elif self.ai_level_btn.collidepoint(x, y):
                self.adjust_ai_level()
                return
            
        if self.ai_vs_stockfish_mode:
            self.status_text = "Đang ở chế độ AI vs Stockfish!"
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
                self.status_text = "Đang suy nghĩ..."
                
                # Reset trạng thái chọn
                self.selected_square = None
                self.possible_moves = []
                
                # Đánh dấu cần thực hiện nước đi AI
                self.need_ai_move = True
                pygame.time.set_timer(USEREVENT + 1, 300)
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
    
    def toggle_ai_vs_stockfish(self):
        """Bật/tắt chế độ AI vs Stockfish"""
        self.ai_vs_stockfish_mode = not self.ai_vs_stockfish_mode
        
        if self.ai_vs_stockfish_mode:
            # Bật chế độ AI vs Stockfish
            self.ai.toggle_ai_vs_stockfish(True)
            self.player_color = None  # Vô hiệu hóa người chơi
            self.status_text = "Chế độ AI vs Stockfish - Đang chạy..."
            
            # Đảm bảo bàn cờ mới
            self.ai.reset_board()
            
            # Kích hoạt ngay lượt đi đầu tiên
            self.need_ai_move = True
            pygame.time.set_timer(USEREVENT + 1, 300)  # Delay ngắn để bắt đầu
        else:
            # Tắt chế độ
            self.ai.toggle_ai_vs_stockfish(False)
            self.player_color = chess.WHITE
            self.status_text = "Chế độ người chơi vs AI"
        
        # Reset trạng thái chọn quân
        self.selected_square = None
        self.possible_moves = []

    def adjust_stockfish_level(self):
        """Điều chỉnh level của Stockfish"""
        new_level = (self.ai.stockfish_skill_level + 5) % 25  # Xoay vòng từ 0-20
        self.ai.set_stockfish_skill(new_level)
        self.status_text = f"Stockfish level: {new_level}/20"

    def adjust_ai_level(self):
        """Điều chỉnh độ sâu của AI"""
        new_depth = self.ai.depth % 5 + 1  # Xoay vòng từ 1-5
        self.ai.set_depth(new_depth)
        self.status_text = f"Độ sâu AI: {new_depth}"

    def make_ai_move(self):
        """Để AI thực hiện nước đi"""
        if self.ai.board.is_game_over():
            self.update_game_status()
            return
        
        print(f"Đang tính nước đi cho {'AI' if self.ai.board.turn == self.ai.ai_color else 'Stockfish'}")
        
        ai_move = self.ai.get_ai_move()
        if ai_move:
            print(f"Nước đi được chọn: {ai_move.uci()}")
            self.ai.board.push(ai_move)
            
            # Cập nhật thông báo
            if self.ai_vs_stockfish_mode:
                player = "AI" if self.ai.board.turn != self.ai.ai_color else "Stockfish"
                self.status_text = f"{player} đã đi: {ai_move.uci()}"
                print(f"Trạng thái bàn cờ:\n{self.ai.board}")
            else:
                self.status_text = f"AI đã đi: {ai_move.uci()}"
        
        self.need_ai_move = False
        self.update_game_status()
    
    def update_game_status(self):
        """Cập nhật trạng thái game"""
        if self.ai.board.is_checkmate():
            winner = "Trắng" if not self.ai.board.turn else "Đen"
            self.status_text = f"Chiếu hết! {winner} thắng"
            self.show_game_over_message(f"Chiếu hết! {winner} thắng")
        elif self.ai.board.is_stalemate():
            self.status_text = "Hòa cờ do bế tắc!"
            self.show_game_over_message("Hòa cờ do bế tắc!")
        elif self.ai.board.is_insufficient_material():
            self.status_text = "Hòa cờ do không đủ quân chiếu hết!"
            self.show_game_over_message("Hòa cờ do không đủ quân chiếu hết!")
        elif self.ai.board.is_check():
            self.status_text = "Chiếu! " + ("Trắng" if self.ai.board.turn else "Đen") + " đi"
    
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
        self.status_text = "Game mới! " + ("Bạn" if self.player_color == chess.WHITE else "AI") + " đi trước (Quân trắng)"
        
        # Nếu AI đi trước
        if self.ai.board.turn != self.player_color:
            self.need_ai_move = True
    
    def switch_sides(self):
        """Đổi bên chơi"""
        self.player_color = not self.player_color
        self.new_game()
    
    def cycle_difficulty(self):
        """Thay đổi độ khó theo chu kỳ"""
        difficulties = ["Dễ", "Trung bình", "Khó", "Rất khó"]
        current_index = difficulties.index(self.difficulty)
        next_index = (current_index + 1) % len(difficulties)
        self.difficulty = difficulties[next_index]
        
        # Cập nhật độ sâu cho AI
        if self.difficulty == "Dễ":
            self.ai.depth = 2
        elif self.difficulty == "Trung bình":
            self.ai.depth = 3
        elif self.difficulty == "Khó":
            self.ai.depth = 4
        elif self.difficulty == "Rất khó":
            self.ai.depth = 5
        
        self.status_text = f"Đã đặt độ khó: {self.difficulty}"
    
    def run(self):
        """Vòng lặp chính của game"""
        while self.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:  # Nút chuột trái
                        self.handle_click(event.pos)
                elif event.type == USEREVENT + 1:
                    if self.ai_vs_stockfish_mode or self.need_ai_move:
                        self.make_ai_move()
                    pygame.time.set_timer(USEREVENT + 1, 0)  # Tắt timer sau khi xử lý
            
            self.draw_board()
            pygame.display.update()
            
            # Tự động kích hoạt nước đi nếu cần
            if not self.ai.board.is_game_over():
                if self.ai_vs_stockfish_mode and not self.need_ai_move:
                    self.need_ai_move = True
                    pygame.time.set_timer(USEREVENT + 1, 500)  # Delay giữa các nước đi
            
            self.clock.tick(30)
        
        pygame.quit()
        sys.exit()
