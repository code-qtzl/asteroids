import sys
import pygame
from constants import *
from player import *
from asteroid import *
from asteroidfield import *

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

    AsteroidField()

    Player.containers = (updatable, drawable)
    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

    dt = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        screen.fill("#0d1117")
        
        for obj in updatable:
            obj.update(dt)

        for obj in drawable:
            obj.draw(screen)

        for asteroid in asteroids:
            if asteroid.collisions(player):
                print("Game over!")
                sys.exit('You crashed bro')

        pygame.display.flip()
        

        dt = clock.tick(60) / 1000


if __name__ == "__main__":
    main()