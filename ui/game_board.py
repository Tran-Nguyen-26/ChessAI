import pygame
from board.board import Board

WIDTH, HEIGHT = 640, 640
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

WHITE = (240, 217, 181)
BROWN = (181, 136, 99)

PIECE_ORDER = ["king", "queen", "bishop", "knight", "rook", "pawn"]

def draw_board(win):
    win.fill(WHITE)
    for row in range(ROWS):
        for col in range(COLS):
            if (row + col) % 2 != 0:
                pygame.draw.rect(win, BROWN, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

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

    running = True
    clock = pygame.time.Clock()

    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
        draw_board(win)
        draw_pieces(win, board, piece_images)
        pygame.display.flip()
    
    pygame.quit()
