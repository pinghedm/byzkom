import time
import pygame
from fighter import Fighter
from characters import *

pygame.font.init()
font = pygame.font.Font(None, 14)


def end_screen(screen, message):
    screen.fill((255, 255, 255))
    text = font.render(message, True, (0, 0, 0))
    textpos = text.get_rect(
        centerx=screen.get_width() / 2,
        centery=screen.get_height() / 2,
    )
    screen.blit(text, textpos)
    pygame.display.flip()
    time.sleep(3)


def main():
    pygame.init()
    game_clock = pygame.time.Clock()

    game_running = True

    pygame.display.set_caption("minimal program")
    screen = pygame.display.set_mode((700, 500))
    screen.fill((255, 255, 255))

    left_player = Fighter(Heraclius, (50, 150))
    left_player.draw(screen)
    right_player = Fighter(Phocas, (400, 150))
    right_player.draw(screen)
    while game_running:
        for event in pygame.event.get(eventtype=pygame.QUIT):
            game_running = False
        screen.fill((255, 255, 255))  # TODO: dont do this, only redraw the dirty part
        right_player.ai_update_state(left_player)
        right_player.draw(screen)
        left_player.update_state(right_player)
        left_player.draw(screen)

        if right_player.health == 0:
            end_screen(screen, "You Win")
            game_running = False
        elif left_player.health == 0:
            end_screen(screen, "You Lose")
            game_running = False

        game_clock.tick(30)
        pygame.display.flip()


if __name__ == "__main__":
    main()
