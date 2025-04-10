import pygame

class GameController:
    def __init__(self):
        self.selected_piece = None
        self.valid_moves = []
        self.current_turn = "white"

    def handle_click(self, board, position):
        row, col = position
        
        if not (0 <= row < 8 and 0 <= col < 8):
            return False, None
            
        piece = board.get_piece(position)
        
        if self.selected_piece:
            if position in self.valid_moves:
                moved, captured_king = board.move_piece(self.selected_piece.position, position)
                self.reset_selection()
                
                if moved:
                    self.switch_turn()
                
                return moved, captured_king
            
            elif piece and piece.color == self.current_turn:
                self.selected_piece = piece
                self.valid_moves = piece.get_valid_moves(board)
                return False, None
                
            else:
                self.reset_selection()
                return False, None
        
        else:
            if piece and piece.color == self.current_turn:
                self.selected_piece = piece
                self.valid_moves = piece.get_valid_moves(board)
            return False, None

    def switch_turn(self):
        self.current_turn = "black" if self.current_turn == "white" else "white"

    def reset_selection(self):
        self.selected_piece = None
        self.valid_moves = []
    
    def get_current_turn(self):
        return self.current_turn