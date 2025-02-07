import sys
import pygame
from constants import *
from player import *
from asteroid import *
from asteroidfield import *
from button import Button

def main():
    pygame.init()
    print(f'Screen width: {SCREEN_WIDTH}\nScreen height: {SCREEN_HEIGHT}\nStarting asteroids!')

    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()

    Asteroid.containers = (asteroids, updatable, drawable)
    AsteroidField.containers = updatable

    Shot.containers = (shots, updatable, drawable)

    reset_button = Button(
        SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 50,
        "#39d353", "Reset", "white"
    )

    AsteroidField()

    Player.containers = (updatable, drawable)
    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

    dt = 0
    game_over = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:  # Mouse click event
                if game_over and reset_button.is_clicked(event.pos):
                    # Reset the game
                    asteroids.empty()
                    shots.empty()
                    updatable.empty()
                    drawable.empty()
                    player.kill()
                    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
                    AsteroidField()
                    game_over = False

        screen.fill("#0d1117")

        if not game_over:  # Only update if the game is running
            for obj in updatable:
                obj.update(dt)

            for obj in drawable:
                obj.draw(screen)

            for asteroid in asteroids:
                if asteroid.collides_with(player):
                    print("Game over!")
                    game_over = True
                for shot in shots:
                    if asteroid.collides_with(shot):
                        asteroid.split()
                        shot.kill()
        else:
            draw_game_over(screen)
            reset_button.draw(screen)


        pygame.display.flip()

        dt = clock.tick(60) / 1000

def draw_game_over(screen):
    font = pygame.font.Font(None, 72)
    text = font.render("You Lost!", True, "red")
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
    screen.blit(text, text_rect)

if __name__ == "__main__":
    main()