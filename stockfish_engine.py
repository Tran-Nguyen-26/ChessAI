import os
import platform
import subprocess
import shutil
import chess

class StockfishEngine:
    def __init__(self, skill_level=20):
        self.stockfish_path = self._find_stockfish()
        self.stockfish_process = None
        self.skill_level = skill_level

        if self.stockfish_path:
            self._init_stockfish()

    def _find_stockfish(self):
        """Tìm đường dẫn đến Stockfish với nhiều vị trí tiềm năng"""
        # Kiểm tra các vị trí phổ biến
        base_dir = os.path.dirname(__file__)
        possible_paths = [
            os.path.join(base_dir, 'stockfish'),
            os.path.join(base_dir, 'engines', 'stockfish'),
            os.path.join(base_dir, 'engine', 'stockfish'),
            os.path.join(base_dir, 'stockfish.exe'),
            '/usr/games/stockfish',           # Linux
            '/usr/local/bin/stockfish',       # macOS
            '/opt/homebrew/bin/stockfish',    # macOS (Homebrew)
        ]
        
        # Thêm đường dẫn mặc định cho Windows
        if platform.system() == 'Windows':
            possible_paths.extend([
                os.path.join(os.getenv('ProgramFiles'), 'Stockfish', 'stockfish.exe'),
                os.path.join(os.getenv('ProgramFiles(x86)'), 'Stockfish', 'stockfish.exe'),
                os.path.join(os.path.dirname(__file__), 'stockfish.exe'),
                os.path.join(os.path.dirname(__file__), 'engines', 'stockfish.exe'),
            ])
        
        # Kiểm tra từng đường dẫn
        for path in possible_paths:
            if os.path.isfile(path) and os.access(path, os.X_OK):
                return path
        
        # Thử tìm trong PATH hệ thống
        if platform.system() != 'Windows':
            path = shutil.which('stockfish')
            if path:
                return path
        
        print("Không tìm thấy Stockfish. Vui lòng cài đặt Stockfish và đặt file thực thi trong thư mục engines/")
        return None

    def _init_stockfish(self):
        try:
            self.stockfish_process = subprocess.Popen(
                self.stockfish_path,
                universal_newlines=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=1
            )
            self._send("uci")
            self._send(f"setoption name Skill Level value {self.skill_level}")
            self._send("ucinewgame")
            self._send("isready")
            while True:
                line = self.stockfish_process.stdout.readline().strip()
                if line == "readyok":
                    break
        except Exception as e:
            print(f"Stockfish init error: {e}")
            self.stockfish_process = None

    def _send(self, command):
        if self.stockfish_process and self.stockfish_process.stdin:
            self.stockfish_process.stdin.write(command + "\n")
            self.stockfish_process.stdin.flush()

    def get_move(self, board, time_ms=1000):
        if not self.stockfish_process:
            return None
        self._send(f"position fen {board.fen()}")
        self._send(f"go movetime {time_ms}")
        while True:
            line = self.stockfish_process.stdout.readline().strip()
            if line.startswith("bestmove"):
                best_move = line.split()[1]
                try:
                    return chess.Move.from_uci(best_move)
                except:
                    return None

    def close(self):
        if self.stockfish_process:
            self._send("quit")
            self.stockfish_process.terminate()
            self.stockfish_process = None
