import random

class Game:
    def __init__(self, grid_size, n_to_win):
        self.grid_size = grid_size
        self.n_to_win = n_to_win
        self.board = [0] * (self.grid_size * self.grid_size)
        self.valid_moves = [i for i in range(0, self.grid_size * self.grid_size)]
        self.current_player = 1
        self.game_over = False
        self.all_winning_combinations = []
        self.winning_combinations_map = {}
        self.create_winning_map()

    def play_move(self, index):
        """
        Plays a move if square is empty and game is ongoing
        """
        if not self.game_over and self.board[index] == 0:
            self.valid_moves.remove(index)
            self.board[index] = self.current_player
            self.current_player = -self.current_player
            return True
        
        return False
        
    def undo_move(self, index):
        """
        Removes a move if square is not empty
        """
        if index not in self.valid_moves:
            self.board[index] = 0
            self.valid_moves.append(index)
            self.current_player = -self.current_player
            self.game_over = False
        else:
            print(f"Invalid undo move on index: {index}")
            return -1
    
    def create_winning_map(self):
        """
        Creates a dictionary with each move as key and a list with the possible 
        win combinations where the move is included as value.
        """
        winning_combinations = []

        # Generates rows
        for row in range(self.grid_size):
            r = []
            for i in range(self.grid_size):
                r.append(row * self.grid_size + i)
            winning_combinations.append(r)
        

        # Generates columns
        for col in range(self.grid_size):
            c = []
            i = col
            for _ in range(self.grid_size):
                c.append(i)
                i += self.grid_size
            winning_combinations.append(c)
        

        # Generates diagonals from left to right
        step = self.grid_size + 1
        
        for col in range(self.grid_size):
            d = []
            for i in range(self.grid_size - col):
                d.append(col + i * step)
            if len(d) >= self.n_to_win:
                winning_combinations.append(d)
        

        for row in range(1, self.grid_size):
            d = []
            for i in range(self.grid_size - row):
                d.append((row * self.grid_size) + (i * step))
            if len(d) >= self.n_to_win:
                winning_combinations.append(d)


        # Generates diagonals from right to left
        step = self.grid_size - 1

        for col in range(self.grid_size - 1, 0, -1):
            d = []
            for i in range(col + 1):
                d.append(col + i * step)
            if len(d) >= self.n_to_win:
                winning_combinations.append(d)
        

        for row in range(1, self.grid_size):
            d = []
            for i in range(self.grid_size - row):
                d.append((row * self.grid_size + self.grid_size - 1) + i * step)
            if len(d) >= self.n_to_win:
                winning_combinations.append(d)


        # Generates all possible winning combinations
        # Maps each move to corresponding winning combinations
        for combination in winning_combinations:
            start = 0
            end = start + self.n_to_win

            while end <= len(combination):
                winning_set = set()
                for i in range(start, end):
                    winning_set.add(combination[i])

                self.all_winning_combinations.append(winning_set)
                for i in winning_set:
                    if i in self.winning_combinations_map:
                        self.winning_combinations_map[i].append(winning_set)
                    else:
                        self.winning_combinations_map[i] = [winning_set]
                start += 1
                end += 1

    def check_game_over(self, last_move):
        """
        Returns player (1 or -1) if the player has n_to_win in a row
        Returns 0 if draw (board is full and no winner)
        """
        player = -self.current_player
        win_check = player * self.n_to_win

        for s in self.winning_combinations_map[last_move]:
            if sum(self.board[i] for i in s) == win_check:
                self.game_over = True
                return player
        

        # Check if any more legal moves exist
        if self.valid_moves:
            return None
        
        # Return 0 for draw
        self.game_over = True
        return 0
    
    def get_winning_squares(self, last_move):
        """
        Returns the squares that contributed to a win if a win has occured
        """
        player = -self.current_player
        win_check = player * self.n_to_win

        for s in self.winning_combinations_map[last_move]:
            if sum(self.board[i] for i in s) == win_check:
                return list(s)

        return None
    
    def restart(self):
        self.board = [0] * (self.grid_size * self.grid_size)
        self.valid_moves = [i for i in range(0, self.grid_size * self.grid_size)]
        self.current_player = 1
        self.game_over = False