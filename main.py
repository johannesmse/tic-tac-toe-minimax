import pygame
import config as cfg
from ui import UI
from game import Game
from tree_ai import TreeAi

pygame.init()
pygame.display.set_caption("Tic Tac Toe")
clock = pygame.time.Clock()
screen = pygame.display.set_mode((cfg.WINDOW_WIDTH, cfg.WINDOW_HEIGHT))
game_ui = UI(screen)
running = True


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        else:
            game_ui.handle_event(event)
    
    game_ui.draw()
    pygame.display.flip()

    clock.tick(60)


pygame.quit()