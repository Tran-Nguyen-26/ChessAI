import chess
import time
import random
import os
import platform
import subprocess
import shutil

class SF:
    def _find_stockfish(self):
        """Tìm đường dẫn đến tệp thực thi Stockfish"""
        # Thử tìm trong thư mục hiện tại hoặc thư mục 'engines'
        common_paths = []

        # Thêm đường dẫn tương đối trong thư mục dự án
        current_dir = os.path.dirname(__file__)
        common_paths.append(os.path.join(current_dir, 'stockfish'))
        common_paths.append(os.path.join(current_dir, 'engines', 'stockfish'))

        # Thêm đường dẫn dựa trên hệ điều hành
        if platform.system() == 'Windows':
            common_paths.append(os.path.join(os.path.dirname(__file__), 'stockfish.exe'))
            common_paths.append(os.path.join(os.path.dirname(__file__), 'engines', 'stockfish.exe'))

            common_paths.append(os.path.join(os.path.dirname(__file__), 'stockfish-windows-x86-64-avx2.exe'))
            common_paths.append(
                os.path.join(os.path.dirname(__file__), 'engines', 'stockfish', 'stockfish-windows-x86-64-avx2.exe'))

            # Thêm đường dẫn cài đặt phổ biến của Windows
            program_files = os.environ.get('ProgramFiles', 'C:\\Program Files')
            common_paths.append(os.path.join(program_files, 'Stockfish', 'stockfish.exe'))

            common_paths.append(os.path.join(program_files, 'Stockfish', 'stockfish-windows-x86-64-avx2.exe'))
        elif platform.system() == 'Linux':
            # Kiểm tra nếu stockfish có trong PATH
            stockfish_in_path = shutil.which('stockfish')
            if stockfish_in_path:
                return stockfish_in_path
            common_paths.append('/usr/games/stockfish')
            common_paths.append('/usr/local/bin/stockfish')
        elif platform.system() == 'Darwin':  # macOS
            common_paths.append('/usr/local/bin/stockfish')
            common_paths.append('/opt/homebrew/bin/stockfish')

        # Kiểm tra từng đường dẫn
        for path in common_paths:
            if os.path.isfile(path) and os.access(path, os.X_OK):
                return path

        print("Không tìm thấy Stockfish. Sử dụng AI tích hợp.")
        return None


    def _init_stockfish(self):
        """Khởi tạo quá trình Stockfish"""
        if not self.stockfish_path:
            self.use_stockfish = False
            return False

        try:
            # Khởi tạo quá trình Stockfish
            self.stockfish_process = subprocess.Popen(
                self.stockfish_path,
                universal_newlines=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=1  # Line buffered
            )

            # Gửi các lệnh khởi tạo
            self._send_to_stockfish("uci")
            self._send_to_stockfish(f"setoption name Skill Level value {self.stockfish_strength}")
            self._send_to_stockfish("ucinewgame")
            self._send_to_stockfish("isready")

            # Đọc phản hồi cho đến khi gặp "readyok"
            while True:
                line = self.stockfish_process.stdout.readline().strip()
                if line == "readyok":
                    break

            return True
        except Exception as e:
            print(f"Lỗi khi khởi tạo Stockfish: {e}")
            self.use_stockfish = False
            return False


    def _send_to_stockfish(self, command):
        """Gửi lệnh đến Stockfish"""
        if self.stockfish_process and self.stockfish_process.stdin:
            self.stockfish_process.stdin.write(command + "\n")
            self.stockfish_process.stdin.flush()


    def _get_stockfish_move(self, time_ms=1000):
        """Lấy nước đi từ Stockfish với giới hạn thời gian (ms)"""
        if not self.stockfish_process:
            return None

        # Gửi trạng thái bàn cờ hiện tại
        self._send_to_stockfish(f"position fen {self.board.fen()}")

        # Yêu cầu Stockfish tìm nước đi tốt nhất
        depth_cmd = f"go depth {self.depth}"
        time_cmd = f"go movetime {time_ms}"

        # Chọn lệnh dựa vào độ khó
        if self.stockfish_strength < 10:  # Dễ
            self._send_to_stockfish(depth_cmd)
        else:  # Khó hơn, sử dụng giới hạn thời gian
            self._send_to_stockfish(time_cmd)

        best_move = None
        while True:
            line = self.stockfish_process.stdout.readline().strip()
            if line.startswith("bestmove"):
                best_move = line.split()[1]
                break

        # Chuyển đổi định dạng nước đi
        if best_move:
            try:
                return chess.Move.from_uci(best_move)
            except ValueError:
                print(f"Lỗi định dạng nước đi Stockfish: {best_move}")
                return None

        return None


    def set_stockfish_strength(self, level):
        """Đặt độ mạnh của Stockfish (1-20)"""
        self.stockfish_strength = max(1, min(20, level))
        if self.stockfish_process:
            self._send_to_stockfish(f"setoption name Skill Level value {self.stockfish_strength}")
            self._send_to_stockfish("ucinewgame")


    def toggle_stockfish(self, use_stockfish):
        """Bật/tắt sử dụng Stockfish"""
        self.use_stockfish = use_stockfish
        if use_stockfish and not self.stockfish_process and self.stockfish_path:
            self._init_stockfish()


    def set_stockfish_strength(self, level):
        """Đặt độ khó cho Stockfish (1-20)"""
        self.stockfish_strength = max(1, min(20, level))
        if self.stockfish_process:
            self._send_to_stockfish(f"setoption name Skill Level value {self.stockfish_strength}")


    def toggle_stockfish_opponent(self, enable):
        """Bật/tắt chế độ đấu với Stockfish"""
        self.use_stockfish_as_opponent = enable
        if enable and not self.stockfish_process and self.stockfish_path:
            self._init_stockfish()