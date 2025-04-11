from abc import abstractmethod


class Piece:
    def __init__(self, color, position):
        self._color = color
        self._position = position
        self.has_moved = False
    
    @property
    def color(self):
        return self._color

    @property
    def position(self):
        return self._position
    
    #setter cho position
    @position.setter
    def position(self, new_position):
        self._position = new_position

    @abstractmethod
    def get_valid_moves(self, board):
        pass
