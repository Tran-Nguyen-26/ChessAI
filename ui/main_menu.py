import pygame
import sys
from ui.game_controls import GameController

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.width  = screen.get_width()
        self.height = screen.get_height()

        self.bg_color = (50, 50, 50)
        self.text_color = (255, 255, 255)
        self.highlight_color = (100, 100, 255)

        pygame.font.init()
        self.title_font = pygame.font.SysFont('Arial', 64, bold=True)
        self.menu_font = pygame.font.SysFont('Arial', 36)

        self.menu_options = ["Người vs Máy", "Máy vs Máy", "Thoát"]
        self.selected_option = 0

        self.running = True

    def draw(self):
        self.screen.fill(self.bg_color)

        title_text = self.title_font.render("CHESS AI", True, self.text_color)
        title_rect = title_text.get_rect(center=(self.width // 2, self.height // 4))
        self.screen.blit(title_text, title_rect)

        for i, option in enumerate(self.menu_options):
            color = self.highlight_color if i == self.selected_option else self.text_color
            option_text = self.menu_font.render(option, True, color)
            option_rect = option_text.get_rect(center=(self.width // 2, self.height // 2 + i * 60))
            self.screen.blit(option_text, option_rect)
        
        pygame.display.flip()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return "QUIT"
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.menu_options)
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.menu_options)
                elif event.key == pygame.K_RETURN:
                    return self.execute_option()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
                    return "QUIT"
        
        return None
    
    def execute_option(self):
        if self.selected_option == 0:  # Người vs Máy
            return "HUMAN_VS_AI"
        elif self.selected_option == 1:  # Máy vs Máy
            return "AI_VS_AI"
        elif self.selected_option == 2:  # Thoát
            self.running = False
            return "QUIT"
    
    def run(self):
        clock = pygame.time.Clock()
        
        while self.running:
            action = self.handle_events()
            self.draw()
            
            if action:
                return action
            
            clock.tick(30)
        
        return "QUIT"

    def run(self):
        clock = pygame.time.Clock()
        
        while self.running:
            action = self.handle_events()
            self.draw()
            
            if action:
                return action
            
            clock.tick(30)  # Giới hạn tốc độ khung hình
        
        return "QUIT"

def run(self):
        clock = pygame.time.Clock()
        
        while self.running:
            action = self.handle_events()
            self.draw()
            
            if action:
                return action
            
            clock.tick(30)  # Giới hạn tốc độ khung hình
        
        return "QUIT"

def run_main_menu(screen):
    menu = MainMenu(screen)
    return menu.run()
