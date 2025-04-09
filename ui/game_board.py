import pygame
from board.board import Board
from ui.game_controls import GameController
from game.ai import evaluate_board, get_all_valid_moves, minimax_alpha_beta

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


def start_game_ui():    
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("ChessAI - Pygame UI")

    piece_images = load_piece_images("C:/ChessAI/assets/images/Chess_Pieces.png")
    board = Board()
    controller = GameController()

    running = True
    clock = pygame.time.Clock()

    current_turn = PLAYER_COLOR
    ai_thinking = False

    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and not ai_thinking:
                if controller.get_current_turn() == "white":
                    x, y = pygame.mouse.get_pos()
                    row = y // 80
                    col = x // 80
                    moved = controller.handle_click(board, (row, col))
                    if moved:
                        current_turn = AI_COLOR
                        ai_thinking = True
                        pygame.time.set_timer(AI_MOVE_EVENT, 100)

            elif event.type == AI_MOVE_EVENT and controller.get_current_turn() == "black":
                pygame.time.set_timer(AI_MOVE_EVENT, 0)
                depth = 3
                eval_score, ai_move = minimax_alpha_beta(board, depth, float('-inf'), float('-inf'), True, AI_COLOR)

                if ai_move:
                    board.move_piece(ai_move[0], ai_move[1])
                    controller.switch_turn()
                ai_thinking = False
                controller.reset_selection()
                print("Current turn after AI move:", controller.get_current_turn())
            
        draw_board(win, controller)
        draw_pieces(win, board, piece_images)
        pygame.display.flip()
    
    pygame.quit()
