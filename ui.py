import pygame
import config as cfg
from game import Game
from tree_ai import TreeAi
import time
import random

class UI:
    def __init__(self, screen):
        self.screen = screen
        self.grid_size = 6
        self.n_to_win = 4
        self.game = Game(self.grid_size, self.n_to_win)
        self.tree_ai = TreeAi(self.n_to_win)

        self.board_top_left_x = (cfg.WINDOW_WIDTH - (self.grid_size * cfg.SQUARE_LENGTH)) // 2
        self.board_top_left_y = (cfg.WINDOW_HEIGHT - (self.grid_size * cfg.SQUARE_LENGTH)) // 2
        
        self.winner = None
        self.winning_squares = None
        self.last_move = None
        self.last_move_time = None
        self.ai_bm = None

        self.game_mode = 0
        self.hard_depth = 3

        self.restart_game_font = pygame.font.SysFont(None, 24)
        self.game_over_font = pygame.font.SysFont(None, 50)
        self.background_color = (35, 35, 35)
        self.selected_button_color = (30, 30, 30)

        self._create_menu_buttons()
        self.buttons = self._create_board_buttons()
        
    def _create_menu_buttons(self):
        board_length = cfg.SQUARE_LENGTH * self.grid_size
        board_x_padding = 60
        menu_button_length = 90
        menu_button_height = 40
        menu_buttons_x = self.board_top_left_x + board_length + board_x_padding

        self.restart_button = pygame.Rect(menu_buttons_x, self.board_top_left_y, 
                                        menu_button_length, menu_button_height)
        
        self.friendly_button = pygame.Rect(menu_buttons_x, self.board_top_left_y + menu_button_height + 10, 
                                        menu_button_length, menu_button_height)
        self.easy_button = pygame.Rect(menu_buttons_x, self.board_top_left_y + 2 * menu_button_height + 10, 
                                        menu_button_length, menu_button_height)
        self.hard_button = pygame.Rect(menu_buttons_x, self.board_top_left_y + 3 * menu_button_height + 10, 
                                        menu_button_length, menu_button_height)
        
        self.three_by_three_button = pygame.Rect(menu_buttons_x, self.board_top_left_y + 4 * menu_button_height + 50, 
                                        menu_button_length / 2, menu_button_height)
        self.six_by_six_button = pygame.Rect(menu_buttons_x + menu_button_length / 2, self.board_top_left_y + 4 * menu_button_height + 50, 
                                        menu_button_length / 2, menu_button_height)
    
    def _create_board_buttons(self):
        buttons = []
        
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                buttons.append(pygame.Rect(self.board_top_left_x + (cfg.SQUARE_LENGTH * j), self.board_top_left_y + (cfg.SQUARE_LENGTH * i),
                                                 cfg.SQUARE_LENGTH, cfg.SQUARE_LENGTH))
        return buttons
    
    def _restart_board(self):
        self.winner = None
        self.winning_squares = None
        self.last_move = None
        self.last_move_time = None
        self.ai_bm = None

    def _change_grid_size(self, grid_size, n_to_win):
        self.grid_size = grid_size
        self.n_to_win = n_to_win
        self.board_top_left_x = (cfg.WINDOW_WIDTH - (self.grid_size * cfg.SQUARE_LENGTH)) // 2
        self.board_top_left_y = (cfg.WINDOW_HEIGHT - (self.grid_size * cfg.SQUARE_LENGTH)) // 2
        
        self.game = Game(self.grid_size, self.n_to_win)
        self.tree_ai = TreeAi(self.n_to_win)
        self._restart_board()
        self.buttons = self._create_board_buttons()

    def _apply_move(self, move):
        """
        Applies a move to the board and checks for winner
        Returns True if move was legal and False if not
        """
        if move is not None:
        
            if self.game.play_move(move):
                self.last_move = move
                self.last_move_time = time.perf_counter()
                self.winner = self.game.check_game_over(move)
                
                if self.winner == 1 or self.winner == -1:
                    self.winning_squares = self.game.get_winning_squares(self.last_move)
                return True
        
        return False
                
    
    def _handle_player_move(self, move):
        """
        Applies a move and checks calls _get_ai_move() to play AI move if the mode for playing against AI is selected
        """
        if self._apply_move(move):
            self.draw()
            pygame.display.flip()

            # Perform computer move after player move
            if not self.game.game_over:
                ai_move = self._get_ai_move()
                if ai_move is not None:
                    self._apply_move(ai_move)
            

    def _get_ai_move(self):
        """
        Returns an AI move if the game is not over and mode for AI moves is selected.
        Enables a message on screen if the move leads to a guaranteed victory
        """
        if not self.game.game_over:
            if self.game_mode == 1:
                return random.choice(self.game.valid_moves)
            
            elif self.game_mode == 2:
                ai_move, ai_score = self.tree_ai.get_move(self.game, self.hard_depth)

                if ai_score >= 10000 and self.grid_size > 3:
                    self.ai_bm = self.game.current_player

                return ai_move
        
            return None


    def draw(self):
        self.screen.fill(self.background_color)

        # Draw board squares on screen
        for index, button in enumerate(self.buttons):

            # Colors the squares in the winning sequence if there is one
            if self.winning_squares is not None and index in self.winning_squares:
                if self.winner == 1:
                    pygame.draw.rect(self.screen, (30, 0, 0), button)
                elif self.winner == -1:
                    pygame.draw.rect(self.screen, (0, 0, 30), button)

            # Colors the last move played for 2 seconds after the move was played
            elif self.last_move == index and time.perf_counter() - self.last_move_time < 2:
                if self.game.board[self.last_move] == 1:
                    pygame.draw.rect(self.screen, (30, 0, 0), button)
                else:
                    pygame.draw.rect(self.screen, (0, 0, 30), button)

            # Uses the same color as the background on the square
            else:
                pygame.draw.rect(self.screen, self.background_color, button)
            
            # Draw crosses in the squares for player 1
            if self.game.board[index] == 1:
                padding = cfg.SQUARE_LENGTH // 4
                pygame.draw.line(self.screen, (200, 30, 30), (button.left + padding, button.top + padding), (button.right - padding, button.bottom - padding), 6)
                pygame.draw.line(self.screen, (200, 30, 30), (button.left + padding, button.bottom - padding), (button.right - padding, button.top + padding), 6)
    
            # Draw circles in the squares for player -1
            elif self.game.board[index] == -1:
                pygame.draw.circle(self.screen, (30, 30, 200), button.center, cfg.SQUARE_LENGTH // 3, 5)
                
        # Draw vertical board lines on top of squares
        for i in range(1, self.grid_size):
          pygame.draw.line(self.screen, (0, 0, 0), (self.board_top_left_x + (cfg.SQUARE_LENGTH * i), self.board_top_left_y),
                           (self.board_top_left_x + (cfg.SQUARE_LENGTH * i), self.board_top_left_y + (cfg.SQUARE_LENGTH * self.grid_size)), 6)
        
        # Draw horizontal board lines on top of squares
        for i in range(1, self.grid_size):
            pygame.draw.line(self.screen, (0, 0, 0), (self.board_top_left_x, self.board_top_left_y + (cfg.SQUARE_LENGTH * i)),
                             (self.board_top_left_x + (cfg.SQUARE_LENGTH * self.grid_size), self.board_top_left_y + (cfg.SQUARE_LENGTH * i)), 6)
            
        
        # Draw restart button
        pygame.draw.rect(self.screen, (50, 50, 50), self.restart_button)
        text_surface = self.restart_game_font.render("Restart", True, (211, 211, 211))
        text_rect = text_surface.get_rect(center=self.restart_button.center)
        self.screen.blit(text_surface, text_rect)

        # Draw friendly button
        if self.game_mode == 0:
            pygame.draw.rect(self.screen, self.selected_button_color, self.friendly_button)
        else:
            pygame.draw.rect(self.screen, (50, 50, 50), self.friendly_button)

        text_surface = self.restart_game_font.render("Friendly", True, (211, 211, 211))
        text_rect = text_surface.get_rect(center=self.friendly_button.center)
        self.screen.blit(text_surface, text_rect)

        # Draw easy button
        # Darker color if the button is selected
        if self.game_mode == 1:
            pygame.draw.rect(self.screen, self.selected_button_color, self.easy_button)
        else:
            pygame.draw.rect(self.screen, (50, 50, 50), self.easy_button)

        text_surface = self.restart_game_font.render("Easy", True, (211, 211, 211))
        text_rect = text_surface.get_rect(center=self.easy_button.center)
        self.screen.blit(text_surface, text_rect)

        # Draw hard button
        # Darker color if the button is selected
        if self.game_mode == 2:
            pygame.draw.rect(self.screen, self.selected_button_color, self.hard_button)
        else:
            pygame.draw.rect(self.screen, (50, 50, 50), self.hard_button)

        text_surface = self.restart_game_font.render("Hard", True, (211, 211, 211))
        text_rect = text_surface.get_rect(center=self.hard_button.center)
        self.screen.blit(text_surface, text_rect)


        # Draw 3x3 button
        if self.grid_size == 3:
            pygame.draw.rect(self.screen, self.selected_button_color, self.three_by_three_button)
        else:
            pygame.draw.rect(self.screen, (50, 50, 50), self.three_by_three_button)

        text_surface = self.restart_game_font.render("3x3", True, (211, 211, 211))
        text_rect = text_surface.get_rect(center=self.three_by_three_button.center)
        self.screen.blit(text_surface, text_rect)

        # Draw 6x6 button
        if self.grid_size == 6:
            pygame.draw.rect(self.screen, self.selected_button_color, self.six_by_six_button)
        else:
            pygame.draw.rect(self.screen, (50, 50, 50), self.six_by_six_button)

        text_surface = self.restart_game_font.render("6x6", True, (211, 211, 211))
        text_rect = text_surface.get_rect(center=self.six_by_six_button.center)
        self.screen.blit(text_surface, text_rect)


        # Display "you will lose" message
        if self.ai_bm is not None and self.winner is None:
            if self.ai_bm == 1:
                color = (200, 30, 30)
            else:
                color = (30, 30, 200)
                
            msg = "You will lose.."
            text_surface = self.game_over_font.render(msg, True, color)
            text_rect = text_surface.get_rect(center=(cfg.WINDOW_WIDTH // 2, self.board_top_left_y // 2))
            self.screen.blit(text_surface, text_rect)

        # Display instruction on screen if first move
        if self.last_move is None:
            msg, color = f"Place {self.n_to_win} in a row to win", (211, 211, 211)
            text_surface = self.game_over_font.render(msg, True, color)
            text_rect = text_surface.get_rect(center=(cfg.WINDOW_WIDTH // 2, self.board_top_left_y // 2))
            self.screen.blit(text_surface, text_rect)


        # Display Winner or Draw messages on screen
        if self.winner is None:
            return
        
        if self.winner == 1:
            msg, color = "Player X has won!", (200, 30, 30)

        elif self.winner == -1:
            msg, color = "Player O has won!", (30, 30, 200)
        elif self.winner == 0:
            msg, color = "Draw!", (211, 211, 211)
            
        text_surface = self.game_over_font.render(msg, True, color)
        text_rect = text_surface.get_rect(center=(cfg.WINDOW_WIDTH // 2, self.board_top_left_y // 2))
        self.screen.blit(text_surface, text_rect)
            
    # Handles inputs from user    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            # Check if a square on board was clicked
            for index, button in enumerate(self.buttons):
                if button.collidepoint(event.pos):
                    self._handle_player_move(index)
                    break   

            if self.restart_button.collidepoint(event.pos):
                self.game.restart()
                self._restart_board()
                print("\n----------STARTING NEW GAME----------\n")

            elif self.friendly_button.collidepoint(event.pos):
                self.game_mode = 0
            
            elif self.easy_button.collidepoint(event.pos):
                # Changes mode
                self.game_mode = 1

                # Requests a move on the current position from easy mode
                ai_move = self._get_ai_move()
                self._apply_move(ai_move)

            elif self.hard_button.collidepoint(event.pos):
                # Changes mode
                self.game_mode = 2

                # Requests a move on the current position from hard mode
                ai_move = self._get_ai_move()
                self._apply_move(ai_move)
                    
            elif self.three_by_three_button.collidepoint(event.pos) and self.grid_size != 3:
                self._change_grid_size(3, 3)
            
            elif self.six_by_six_button.collidepoint(event.pos) and self.grid_size != 6:
                self._change_grid_size(6, 4)