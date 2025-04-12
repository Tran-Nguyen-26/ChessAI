import pygame
import sys
import os
from ui.game_board import start_game_ui

# Constants
WIDTH, HEIGHT = 800, 600
TITLE_SIZE = 72
MENU_FONT_SIZE = 36
BUTTON_WIDTH = 300
BUTTON_HEIGHT = 60
BUTTON_PADDING = 20

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)
GOLD = (218, 165, 32)
DARK_GOLD = (184, 134, 11)
BROWN = (139, 69, 19)
LIGHT_BROWN = (205, 133, 63)

class Button:
    def __init__(self, text, x, y, width, height, normal_color, hover_color, text_color, font_size=MENU_FONT_SIZE):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.normal_color = normal_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = pygame.font.SysFont('Arial', font_size, bold=True)
        self.is_hovered = False
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.normal_color
        # Draw button background
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=10)  # Border
        
        # Draw text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered
        
    def is_clicked(self, mouse_pos, mouse_clicked):
        return self.is_hovered and mouse_clicked

class MainMenu:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Chess Game - Main Menu")
        
        # Load background image if available, otherwise use a color
        self.background = self.load_background()
        
        # Setup fonts
        self.title_font = pygame.font.SysFont('Arial', TITLE_SIZE, bold=True)
        self.menu_font = pygame.font.SysFont('Arial', MENU_FONT_SIZE)
        
        # Create buttons
        button_x = WIDTH // 2 - BUTTON_WIDTH // 2
        button_y_start = HEIGHT // 2
        
        self.buttons = [
            Button("Play Game", button_x, button_y_start, 
                   BUTTON_WIDTH, BUTTON_HEIGHT, GOLD, DARK_GOLD, BLACK),
            Button("How to Play", button_x, button_y_start + BUTTON_HEIGHT + BUTTON_PADDING, 
                   BUTTON_WIDTH, BUTTON_HEIGHT, LIGHT_BROWN, BROWN, BLACK),
            Button("Quit", button_x, button_y_start + 2 * (BUTTON_HEIGHT + BUTTON_PADDING), 
                   BUTTON_WIDTH, BUTTON_HEIGHT, DARK_GRAY, GRAY, WHITE)
        ]
        
        # Current screen state
        self.current_screen = "main_menu"
        self.clock = pygame.time.Clock()
        
    def load_background(self):
        try:
            # Try to load a background image
            bg_path = os.path.join("assets", "images", "chess_background.jpg")
            background = pygame.image.load(bg_path)
            return pygame.transform.scale(background, (WIDTH, HEIGHT))
        except:
            # If image not found, create a gradient background
            background = pygame.Surface((WIDTH, HEIGHT))
            for y in range(HEIGHT):
                # Create gradient from light gray to dark gray
                color_value = 200 - int(y / HEIGHT * 100)
                pygame.draw.line(background, (color_value, color_value, color_value), (0, y), (WIDTH, y))
            return background
    
    def draw_main_menu(self):
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        # Draw title with shadow effect
        title_text = "CHESS MASTER"
        title_shadow = self.title_font.render(title_text, True, BLACK)
        title_surface = self.title_font.render(title_text, True, GOLD)
        
        # Calculate position for center alignment
        title_x = WIDTH // 2 - title_surface.get_width() // 2
        title_y = HEIGHT // 4 - title_surface.get_height() // 2
        
        # Draw shadow and then main text
        self.screen.blit(title_shadow, (title_x + 3, title_y + 3))
        self.screen.blit(title_surface, (title_x, title_y))
        
        # Draw buttons
        for button in self.buttons:
            button.draw(self.screen)
    
    def draw_how_to_play(self):
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        # Title
        title_text = "How to Play"
        title_surface = self.menu_font.render(title_text, True, GOLD)
        self.screen.blit(title_surface, (WIDTH // 2 - title_surface.get_width() // 2, 30))
        
        # Instructions
        instructions = [
            "1. Click on a piece to select it",
            "2. Green dots show possible moves",
            "3. Click on a green dot to move the piece",
            "4. Play alternates between you and the AI",
            "5. Capture opponent's king to win",
            "",
            "Good luck!"
        ]
        
        for i, line in enumerate(instructions):
            text_surface = self.menu_font.render(line, True, WHITE)
            self.screen.blit(text_surface, (50, 100 + i * 45))
        
        # Back button
        back_button = Button("Back to Menu", WIDTH // 2 - BUTTON_WIDTH // 2, 
                             HEIGHT - 100, BUTTON_WIDTH, BUTTON_HEIGHT, 
                             DARK_GRAY, GRAY, WHITE)
        back_button.draw(self.screen)
        
        return back_button
        
    def run(self):
        running = True
        
        while running:
            mouse_pos = pygame.mouse.get_pos()
            mouse_clicked = False
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        mouse_clicked = True
            
            if self.current_screen == "main_menu":
                self.draw_main_menu()
                
                # Handle button hover and clicks
                for i, button in enumerate(self.buttons):
                    button.check_hover(mouse_pos)
                    if button.is_clicked(mouse_pos, mouse_clicked):
                        if i == 0:  # Play Game
                            pygame.quit()
                            start_game_ui()  # Start the chess game
                            # Re-initialize pygame after the game ends
                            pygame.init()
                            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
                        elif i == 1:  # How to Play
                            self.current_screen = "how_to_play"
                        elif i == 2:  # Quit
                            running = False
            
            elif self.current_screen == "how_to_play":
                back_button = self.draw_how_to_play()
                back_button.check_hover(mouse_pos)
                if back_button.is_clicked(mouse_pos, mouse_clicked):
                    self.current_screen = "main_menu"
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    menu = MainMenu()
    menu.run()