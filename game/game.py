class Game:
    def __init__(self, board, white_player, black_player):
        self.board= board
        self.white_player = white_player
        self.black_player = black_player
        self.current_player = white_player
        self.game_over = False
        self.winner = None

    def switch_turn(self):
        self.current_player = self.white_player if self.current_player == self.black_player else self.black_player

    def make_move(self, from_pos, to_pos):
        if self.game_over:
            return False
        
        piece = self.board.get_piece(from_pos)
        if piece and piece.color == self.current_player.color:
            valid_moves = piece.get_valid_moves(self.board.board)
            if to_pos in valid_moves:
                self.board.move_piece(from_pos, to_pos)

            #kiểm tra nếu vua bị ăn
            if isinstance(self.board.get_piece(to_pos), type(self.board.king_pieces[self.opponent_color()])):
                self.game_over = True
                self.winner = self.current_player.color
            
            self.switch_turn()
            return True
        
        return False

    def opponent_color(self):
        return "black" if self.current_player.color == "white" else "white"
    
    def is_over_game(self):
        return self.game_over
    
    def get_winner(self):
        return self.winner