import pygame

class GameController:
    def __init__(self):
        self.selected_piece = None
        self.valid_moves = []
        self.current_turn = "white"

    def handle_click(self, board, position):
        row, col = position
        piece = board.get_piece((row, col))

        if self.current_turn != "white":
            return False 

        if self.selected_piece:
            if (row, col) in self.valid_moves:
                board.move_piece(self.selected_piece.position, (row, col))
                self.switch_turn()
                self.reset_selection()
                return True
            self.reset_selection()
            return False
        else:
            if piece and piece.color == self.current_turn:
                self.selected_piece = piece
                self.valid_moves = piece.get_valid_moves(board)
        return False

    def switch_turn(self):
        self.current_turn = "black" if self.current_turn == "white" else "white"

    def reset_selection(self):
        self.selected_piece = None
        self.valid_moves = []
    
    def get_current_turn(self):
        return self.current_turn