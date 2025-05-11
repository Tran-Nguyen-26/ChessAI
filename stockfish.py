import chess
import chess.engine
import os
import platform

class StockFish:
    def __init__(self, path=None, level=10):
        self.level = max(1, min(level, 20))
        self.board = chess.Board()
        self.engine = None
        self.path = path or self.get_default_path()
        self.load_engine()

    def get_default_path(self):
        """Tự động chọn đường dẫn phù hợp theo hệ điều hành"""
        system = platform.system()
        if system == "Windows":
            return "stockfish.exe"
        elif system == "Darwin":  # macOS
            return "./stockfish-mac"
        else:  # Linux
            return "./stockfish"

    def load_engine(self):
        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(self.path)
            self.set_level(self.level)
        except FileNotFoundError:
            print(f"Không tìm thấy Stockfish tại: {self.path}")
            print("Hãy chắc chắn rằng bạn đã tải Stockfish và đặt đúng tên/tệp/thư mục.")
            self.engine = None

    def set_level(self, level):
        self.level = max(1, min(level, 20))
        if self.engine:
            self.engine.configure({
                "Skill Level": self.level - 1  # Stockfish dùng thang 0–19
            })

    def reset_board(self):
        self.board.reset()

    def set_board_from_fen(self, fen):
        try:
            self.board.set_fen(fen)
        except ValueError:
            pass

    def get_move(self, thinking_time=1):
        """Trả về nước đi tốt nhất trong khoảng thời gian đã cho"""
        if self.engine:
            try:
                result = self.engine.play(self.board, chess.engine.Limit(time=thinking_time))
                return result.move
            except Exception as e:
                print("Lỗi khi lấy nước đi từ Stockfish:", e)
        return None

    def make_move(self, move):
        if isinstance(move, str):
            move = chess.Move.from_uci(move)
        if move in self.board.legal_moves:
            self.board.push(move)
            return True
        return False

    def quit(self):
        if self.engine:
            self.engine.quit()
