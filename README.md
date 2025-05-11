# Dự Án Cờ Vua AI

Dự án này xây dựng một hệ thống chơi cờ vua sử dụng trí tuệ nhân tạo (AI), cho phép người dùng thi đấu với AI tự tạo hoặc với engine Stockfish – một trong những engine cờ vua mạnh nhất hiện nay.

## 🎮 Tính năng

- ♟️ **Người chơi vs AI tự tạo**: Người dùng có thể thi đấu với một AI được xây dựng bằng các thuật toán tự phát triển.
- 🤖 **Người chơi vs Stockfish**: Hỗ trợ thi đấu trực tiếp với engine Stockfish.
- ⚔️ **AI vs Stockfish**: So tài giữa AI tự tạo và Stockfish để đánh giá chất lượng thuật toán.
- 🔁 **Chuyển bên (Switch side)**: Cho phép người chơi đổi bên (trắng ↔ đen) trong quá trình chơi.
- 🎚️ **Điều chỉnh độ sâu tìm kiếm (Depth) của AI**: Tùy chỉnh độ sâu thuật toán minimax/alpha-beta pruning.
- 🎮 **Điều chỉnh cấp độ (Level) của Stockfish**: Thay đổi độ mạnh của Stockfish theo cấp độ người chơi.

## 🧠 Thuật toán sử dụng

- **Minimax và Alpha-Beta Pruning**: Dùng để tìm nước đi tối ưu cho AI với hiệu suất cao hơn bằng cách loại bỏ các nhánh không cần thiết.
- **Đánh giá trạng thái bàn cờ dựa trên các yếu tố sau**:
  - 🪙 **Giá trị quân cờ**: Tính điểm theo loại quân (tốt, mã, tượng, xe, hậu).
  - 🎯 **Kiểm soát trung tâm**: Ưu tiên các quân kiểm soát các ô trung tâm của bàn cờ.
  - 🛡️ **Khả năng phòng thủ và tấn công**: Xem xét số lượng quân đang bị đe dọa và khả năng gây áp lực lên quân đối phương.

## 🔧 Yêu cầu hệ thống

- Python 3.8+
- Thư viện hỗ trợ: `python-chess`, `pygame` (nếu có giao diện), `stockfish` (thông qua API hoặc CLI)

## 🚀 Cách sử dụng

1.  **Clone repository về máy của bạn:**
    ```bash
    git clone https://github.com/Tran-Nguyen-26/ChessAI.git
    cd ChessAI
    ```
    *(Lưu ý: Tên thư mục sau khi clone sẽ là `ChessAI` chứ không phải `ai-chess-project` nếu dựa theo link repo của bạn).*

2.  **Cài đặt các thư viện cần thiết:**
    Mở terminal hoặc command prompt trong thư mục dự án (`ChessAI`) và chạy lệnh sau:
    ```bash
    pip install pygame python-chess
    ```
    *(Gói `python-chess` là tên chính thức trên PyPI cho thư viện `chess` bạn đang dùng).*

    Hoặc, nếu bạn có file `requirements.txt` (khuyến khích nên có):
    ```bash
    pip install -r requirements.txt
    ```

3.  **Khởi chạy chương trình:**
    Vẫn trong thư mục dự án (`ChessAI`), chạy lệnh:
    ```bash
    python main.py
    ```
    
## 📁 Cấu trúc thư mục
<pre>
ChessAI/
│
├── __pycache__/               # File biên dịch tự động của Python
│   ├── ChessGUI.cpython-312.pyc
│   ├── ChessGUI.cpython-313.pyc
│   ├── ai.cpython-312.pyc
│   └── ai.cpython-313.pyc
│
├── assets/                    # Tài nguyên đa phương tiện
│   ├── images/               # Thư mục chứa hình ảnh
│   │   └── Chess_Pieces.png   # Hình ảnh quân cờ
│   └── sounds/               # Thư mục chứa âm thanh
│       └── move_piece.mp3     # Âm thanh khi đi quân
│
├── engines/                  # Engine cờ vua bên ngoài
│   └── stockfish/            # Thư mục chứa file thực thi Stockfish
│       └── stockfish          # File thực thi Stockfish
│
├── ChessGUI.py                # Giao diện người dùng (GUI) chính
├── ai.py                      # Thuật toán AI (minimax, alpha-beta, đánh giá cờ)
├── main.py                    # File khởi chạy chính của chương trình
└── README.md                  # Tài liệu mô tả dự án
</pre>

## 🎥 Link video demo
https://drive.google.com/file/d/18iVR4hBUICSh-szEcUKuqSkL-I6DMA5q/view?usp=sharing
