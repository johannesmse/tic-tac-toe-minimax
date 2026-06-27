import random
import math
import time
from game import Game

class TreeAi:
    def __init__(self, n_to_win):
        self.weights = [10**i for i in range(n_to_win + 1)]
        self.win_reward = self.weights[-1]
        self.evaluation_cache = {}
        self.player = None
        self.start_time = None
        self.nodes_visited = 0
        self.prune_triggers = 0

    def get_move(self, game, depth):
        """
        Returns the best move found at current board state using min-max search with depth=depth and alpha beta pruning
        """
        self.start_time = time.perf_counter()
        self.nodes_visited = 0
        self.prune_triggers = 0
        
        self.player = game.current_player
        move_scores = {}
        self.evaluation_cache = {}
        ordered_moves = self.quick_move_ordering(game, game.valid_moves.copy(), True)

        for move in ordered_moves:
            move_scores[move] = self.evaluate_move(move, game, -math.inf, math.inf, depth - 1)
        ordered_moves = [move for move, score in sorted(move_scores.items(), key=lambda x: x[1], reverse=True)]
     
        self._print_stats()
        return self.random_best_move(move_scores)
    
    def _print_stats(self):
        end_time = time.perf_counter()
        execution_time = end_time - self.start_time
        print(f"\nAI move took: {execution_time:.6f} seconds")
        print(f"Nodes visited: {self.nodes_visited}")
        print(f"Prune triggers: {self.prune_triggers}")

    def random_best_move(self, move_scores):
        """
        move_scores : a dictionary containing moves as keys and scores as values
        Returns the move in move_scores with the highest score along with its score. 
        If multiple moves have the same highest score, randomly choses between the highest scoring moves
        """

        max_score = max(move_scores.values())
        best_moves = [move for move, score in move_scores.items() if score == max_score]
        best_move = random.choice(best_moves)
        best_score = move_scores[best_move]
        return best_move, best_score
    
    def quick_move_ordering(self, game, moves, reverse):
        """
        Returns a list of moves sorted from highest to lowest,
        sorted using evaluate_position(game) method.
        """
        move_scores = {}
        for move in moves:
            game.play_move(move)
            move_scores[move] = self.evaluate_position(game)
            game.undo_move(move)
        
        ordered_moves = sorted(move_scores.items(), key=lambda x: x[1], reverse=reverse)
        return [move for move, score in ordered_moves]


    def evaluate_move(self, move, game, alpha, beta, depth):
        """
        Performs the minmax search with alpha beta pruning and recursively searches deeper in the tree
        until terminal node or max depth is reached.
        """
        self.nodes_visited += 1
        game.play_move(move)

        # Returns values at terminal board states
        # Player has won
        result = game.check_game_over(move)
        if result == self.player:
            game.undo_move(move)
            return self.win_reward * (depth + 1)
        
        # Opponent has won
        elif result == self.player * -1:
            game.undo_move(move)
            return -self.win_reward * (depth + 1)
        
        # Game is draw
        elif result == 0:
            game.undo_move(move)
            return 0
        
        # Max depth is reached, heuristic evaluation of position is returned
        if depth == 0:
            score = self.evaluate_position(game)
            game.undo_move(move)
            return score
        
        # Maximizing player
        if game.current_player == self.player:
            max_move = -math.inf
            ordered_moves = self.quick_move_ordering(game, game.valid_moves.copy(), True)

            for next_move in ordered_moves:
                move_score = self.evaluate_move(next_move, game, alpha, beta, depth - 1)
                max_move = max(move_score, max_move)

                alpha = max(move_score, alpha)
                if alpha >= beta:
                    self.prune_triggers += 1
                    break

            game.undo_move(move)
            return max_move
        
        # Minimizing player
        else:
            min_move = math.inf
            ordered_moves = self.quick_move_ordering(game, game.valid_moves.copy(), False)

            for next_move in ordered_moves:
                move_score = self.evaluate_move(next_move, game, alpha, beta, depth - 1)
                min_move = min(move_score, min_move)

                beta = min(move_score, beta)
                if beta <= alpha:
                    self.prune_triggers += 1
                    break
            
            game.undo_move(move)
            return min_move
        
    def evaluate_position(self, game):
        
        """
        Heuristic position evaluator that returns an estimated score of the current position.
        Looks at every winning line possible on the board and counts win possibilities for both players.

        score > 0 : advantage for current player.
        score < 0 : advantage for opponent.
        """

        # Returns score from cache if position has already been evaluated
        cache_key = tuple(game.board)
        if cache_key in self.evaluation_cache:
            return self.evaluation_cache[cache_key]

        score = 0
        board = game.board
        for combination in game.all_winning_combinations:
            player_count = 0
            opponent_count = 0
            for i in combination:
                if board[i] == self.player:
                    player_count += 1
                elif board[i] == self.player * -1:
                    opponent_count += 1
        
            if player_count > 0 and opponent_count == 0:
                if player_count == game.n_to_win - 1 and game.current_player == self.player:
                    score += self.win_reward
                else:
                    score += self.weights[player_count]
            elif opponent_count > 0 and player_count == 0:
                if opponent_count == game.n_to_win - 1 and game.current_player == -self.player:
                    score -= self.win_reward
                else:
                    score -= self.weights[opponent_count]
    
        self.evaluation_cache[cache_key] = score
        return score


        
        
        

        

        

    

