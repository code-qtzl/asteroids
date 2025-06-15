import sys
import pygame
from constants import *
from player import *
from asteroid import *
from asteroidfield import *
from button import Button
from highscore import HighScoreManager

def main():
    pygame.init()
    print(f'Screen width: {SCREEN_WIDTH}\nScreen height: {SCREEN_HEIGHT}\nStarting asteroids!')

    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # Initialize high score manager
    try:
        high_score_manager = HighScoreManager()
        high_score_enabled = True
        print("High score tracking enabled")
    except Exception as e:
        print(f"Error initializing high score manager: {e}")
        high_score_enabled = False
        print("High score tracking disabled")

    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()

    Asteroid.containers = (asteroids, updatable, drawable)
    AsteroidField.containers = updatable

    Shot.containers = (shots, updatable, drawable)

    reset_button = Button(
        SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50, 200, 50,
        "#39d353", "Reset", "white"
    )

    AsteroidField()

    Player.containers = (updatable, drawable)
    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

    dt = 0
    game_over = False
    score = 0  # Initialize score counter
    high_score = high_score_manager.get_high_score() if high_score_enabled else 0

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
                    score = 0  # Reset score when game is reset

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
                        score += 1  # Increment score when asteroid is hit
                        
                        # Update high score if needed
                        if high_score_enabled and score > high_score:
                            high_score = score
                            high_score_manager.update_high_score(score)
            
            # Display score and high score
            draw_score(screen, score, high_score if high_score_enabled else None)
        else:
            draw_game_over(screen)
            reset_button.draw(screen)
            # Display final score on game over screen
            draw_final_score(screen, score, high_score if high_score_enabled else None)


        pygame.display.flip()

        dt = clock.tick(60) / 1000

def draw_game_over(screen):
    font = pygame.font.Font(None, 72)
    text = font.render("You Lost!", True, "red")
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
    screen.blit(text, text_rect)

def draw_score(screen, score, high_score=None):
    font = pygame.font.Font(None, 36)
    text = font.render(f"Score: {score}", True, "#39d353")
    screen.blit(text, (20, 20))
    
    # Display high score if available
    if high_score is not None:
        high_score_text = font.render(f"High Score: {high_score}", True, "#39d353")
        screen.blit(high_score_text, (20, 60))

def draw_final_score(screen, score, high_score=None):
    font = pygame.font.Font(None, 48)
    text = font.render(f"Final Score: {score}", True, "#39d353")
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 80))
    screen.blit(text, text_rect)
    
    # Display high score if available
    if high_score is not None:
        if score >= high_score:
            high_score_text = font.render(f"NEW HIGH SCORE!", True, "#FFD700")
        else:
            high_score_text = font.render(f"High Score: {high_score}", True, "#39d353")
        # Position high score text above the reset button
        high_score_rect = high_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(high_score_text, high_score_rect)

if __name__ == "__main__":
    main()