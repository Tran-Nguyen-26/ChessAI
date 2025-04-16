import pygame
import os
from board.board import Board
from ui.game_controls import GameController
from game.ai import minimax_alpha_beta

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Đường dẫn tới các file cần thiết
SOUND_PATH = os.path.join(BASE_DIR, "assets", "sounds", "move_piece.mp3")
IMAGE_PATH = os.path.join(BASE_DIR, "assets", "images", "Chess_Pieces.png")

WIDTH, HEIGHT = 640, 640
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

WHITE = (240, 217, 181)
BROWN = (181, 136, 99)

PIECE_ORDER = ["king", "queen", "bishop", "knight", "rook", "pawn"]

AI_COLOR = "black"
PLAYER_COLOR = "white"
AI_MOVE_EVENT = pygame.USEREVENT + 1

def draw_board(win, controller):
    win.fill(WHITE)
    for row in range(ROWS):
        for col in range(COLS):
            if (row + col) % 2 != 0:
                pygame.draw.rect(win, BROWN, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    
    if controller.selected_piece:
        sel_row, sel_col = controller.selected_piece.position
        pygame.draw.rect(win, (173, 216, 230), (sel_col * SQUARE_SIZE, sel_row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))  # Xanh nhạt

        for move in controller.valid_moves:
            r, c = move
            pygame.draw.circle(win, (0, 255, 0), (c * SQUARE_SIZE + SQUARE_SIZE // 2, r * SQUARE_SIZE + SQUARE_SIZE // 2), 10)  # Chấm xanh

def load_piece_images(sprite_path):
    piece_images = {}
    sprite_sheet = pygame.image.load(sprite_path).convert_alpha()

    piece_width = 800 // 6
    piece_height = 267 // 2

    for i, name in enumerate(PIECE_ORDER):
        # Đen
        rect_black = pygame.Rect(i * piece_width, piece_height, piece_width, piece_height)
        image_black = sprite_sheet.subsurface(rect_black)
        piece_images[f"black_{name}"] = pygame.transform.scale(image_black, (SQUARE_SIZE, SQUARE_SIZE))

        # Trắng
        rect_white = pygame.Rect(i * piece_width, 0, piece_width, piece_height)
        image_white = sprite_sheet.subsurface(rect_white)
        piece_images[f"white_{name}"] = pygame.transform.scale(image_white, (SQUARE_SIZE, SQUARE_SIZE))

    return piece_images

def draw_pieces(win, board_obj, piece_images):
    for row in range(8):
        for col in range(8):
            piece = board_obj.get_piece((row, col))
            if piece:
                name = f"{piece.color}_{piece.__class__.__name__.lower()}"
                win.blit(piece_images[name], (col * SQUARE_SIZE, row * SQUARE_SIZE))

def draw_promotion_dialog(win, color, position, piece_images):
    _, col = position
    pieces = ["queen", "rook", "bishop", "knight"]
    
    if color == "white":
        start_row = 1
    else:
        start_row = 3

    dialog_width = SQUARE_SIZE
    dialog_height = 4 * SQUARE_SIZE
    pygame.draw.rect(win, (230, 230, 230), (col * SQUARE_SIZE, start_row * SQUARE_SIZE, dialog_width, dialog_height))
    pygame.draw.rect(win, (100, 100, 100), (col * SQUARE_SIZE, start_row * SQUARE_SIZE, dialog_width, dialog_height), 2)

    for i, piece_type in enumerate(pieces):
        piece_img = piece_images[f"{color}_{piece_type}"]
        win.blit(piece_img, (col * SQUARE_SIZE, (start_row + i) * SQUARE_SIZE))

        pygame.draw.rect(win, (150, 150, 150), (col * SQUARE_SIZE, (start_row + i) * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 1)


def start_game_ui():    
    pygame.init()
    pygame.mixer.init()
    move_sound = pygame.mixer.Sound(SOUND_PATH)
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("ChessAI")

    piece_images = load_piece_images(IMAGE_PATH)
    board = Board()
    controller = GameController()

    running = True
    clock = pygame.time.Clock()

    
    ai_thinking = False
    game_over = False
    winner = None

    promotion_active = False

    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                row = y // SQUARE_SIZE
                col = x // SQUARE_SIZE

                # Xử lý phong quân nếu đang hiển thị dialog
                if promotion_active and board.promote_piece:
                    promotion_col = board.promote_position[1]
                    
                    # Kiểm tra nếu click vào đúng cột của quân phong
                    if col == promotion_col:
                        color = board.promote_piece.color
                        promotion_row_start = 1 if color == "white" else 3
                        
                        # Kiểm tra click vào khu vực chọn quân
                        if promotion_row_start <= row < promotion_row_start + 4:
                            piece_index = row - promotion_row_start
                            promotion_pieces = ["queen", "rook", "bishop", "knight"]
                            
                            if piece_index < len(promotion_pieces):
                                # Thực hiện phong quân
                                if board.promote_pawn(promotion_pieces[piece_index]):
                                    move_sound.play()
                                    promotion_active = False
                                    
                                    # Chuyển lượt nếu là người chơi
                                    if controller.get_current_turn() == PLAYER_COLOR:
                                        controller.switch_turn()
                                        # Bắt đầu lượt AI
                                        if controller.get_current_turn() == AI_COLOR:
                                            ai_thinking = True
                                            pygame.time.set_timer(AI_MOVE_EVENT, 100)
                                    
                        continue  # Bỏ qua các xử lý click khác

                # Xử lý click thông thường nếu không đang phong quân
                if not promotion_active and not ai_thinking and not game_over:
                    if controller.get_current_turn() == PLAYER_COLOR:
                        result = controller.handle_click(board, (row, col))
                        
                        if result:
                            moved, captured_king = result
                            
                            if moved:
                                move_sound.play()
                                
                                # Kiểm tra nếu cần phong quân
                                if board.promote_piece:
                                    promotion_active = True
                                    continue  # Không chuyển lượt chơi cho đến khi phong quân xong
                                    
                                if captured_king == AI_COLOR:
                                    game_over = True
                                    winner = PLAYER_COLOR
                                    print("Player win")
                                else:
                                    ai_thinking = True
                                    pygame.time.set_timer(AI_MOVE_EVENT, 100)

            elif event.type == AI_MOVE_EVENT and controller.get_current_turn() == AI_COLOR:
                pygame.time.set_timer(AI_MOVE_EVENT, 0)
                depth = 3
                eval_score, ai_move = minimax_alpha_beta(board, depth, float('-inf'), float('inf'), True, AI_COLOR)

                if ai_move:
                    moved, captured_king = board.move_piece(ai_move[0], ai_move[1])

                    if moved:
                        move_sound.play()
                        controller.switch_turn()

                        # Kiểm tra nếu vua bị ăn
                        if captured_king == PLAYER_COLOR:
                            game_over = True
                            winner = "black"
                            print("AI win")
    
                ai_thinking = False
                controller.reset_selection()
            
        draw_board(win, controller)
        draw_pieces(win, board, piece_images)

        if promotion_active and board.promote_piece:
            draw_promotion_dialog(win, board.promote_piece.color, board.promote_position, piece_images)

        pygame.display.flip()
