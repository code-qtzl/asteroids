import sys
import pygame
from constants import *
from player import *
from asteroid import *
from asteroidfield import *
from alien import *
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
    alien_ships = pygame.sprite.Group()
    alien_shots = pygame.sprite.Group()

    Asteroid.containers = (asteroids, updatable, drawable)
    AsteroidField.containers = (updatable,)

    Shot.containers = (shots, updatable, drawable)
    AlienShip.containers = (alien_ships, updatable, drawable)
    AlienShot.containers = (alien_shots, updatable, drawable)

    reset_button = Button(
        SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50, 200, 50,
        "#39d353", "Reset", "white"
    )

    AsteroidField()

    Player.containers = (updatable, drawable)
    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

    dt = 0
    game_over = False
    game_paused = False  # Add pause state
    score = 0  # Initialize score counter
    high_score = high_score_manager.get_high_score() if high_score_enabled else 0
    alien_spawned = False  # Track if alien has been spawned for this score threshold

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p and not game_over:  # Press 'P' to pause (only when game is running)
                    game_paused = not game_paused  # Toggle pause, but we'll override this below
                    game_paused = True  # Force pause on (can only unpause with spacebar)
                    print("Game Paused! Press SPACEBAR to continue.")
                elif event.key == pygame.K_SPACE and game_paused:  # Press SPACEBAR to unpause
                    game_paused = False
                    print("Game Unpaused!")
            if event.type == pygame.MOUSEBUTTONDOWN:  # Mouse click event
                if game_over and reset_button.is_clicked(event.pos):
                    # Reset the game
                    # Clear all sprite groups
                    for sprite in updatable:
                        sprite.kill()
                    for sprite in drawable:
                        sprite.kill()
                    
                    asteroids.empty()
                    shots.empty()
                    alien_ships.empty()
                    alien_shots.empty()
                    updatable.empty()
                    drawable.empty()
                    
                    # Recreate player and asteroid field
                    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
                    AsteroidField()
                    game_over = False
                    game_paused = False  # Reset pause state
                    score = 0  # Reset score when game is reset
                    alien_spawned = False  # Reset alien spawn flag

        screen.fill("#0d1117")

        if not game_over and not game_paused:  # Only update if the game is running and not paused
            # Spawn alien ship when score reaches 25
            if score >= ALIEN_SPAWN_SCORE and not alien_spawned and len(alien_ships) == 0:
                alien = AlienShip()
                alien_spawned = True
                print("Alien ship spawned!")

            for obj in updatable:
                if isinstance(obj, AlienShip):
                    obj.update(dt, player.position, alien_shots, asteroids)
                else:
                    obj.update(dt)

            # Check collisions
            for asteroid in asteroids:
                if asteroid.collides_with(player):
                    print("Game over! Hit by asteroid!")
                    game_over = True
                    break  # Exit loop early if game over
                
                # Check player shots hitting asteroids
                for shot in shots:
                    if asteroid.collides_with(shot):
                        asteroid.split()
                        shot.kill()
                        score += 1  # Increment score when asteroid is hit
                        
                        # Update high score if needed
                        if high_score_enabled and score > high_score:
                            high_score = score
                            high_score_manager.update_high_score(score)
                        break  # Exit inner loop to avoid checking destroyed asteroid

            # Check alien ship collisions
            for alien in alien_ships:
                if alien.collides_with(player):
                    print("Game over! Hit by alien ship!")
                    game_over = True
                
                # Check if player shots hit alien
                for shot in shots:
                    if alien.collides_with(shot):
                        alien.kill()
                        shot.kill()
                        score += 5  # Bonus points for destroying alien
                        alien_spawned = False  # Allow new alien to spawn later
                        
                        # Update high score if needed
                        if high_score_enabled and score > high_score:
                            high_score = score
                            high_score_manager.update_high_score(score)

            # Check alien shot collisions with player
            for alien_shot in alien_shots:
                if alien_shot.collides_with(player):
                    print("Game over! Shot by alien!")
                    game_over = True
                
                # Check if alien shots hit asteroids (they destroy them too)
                for asteroid in asteroids:
                    if alien_shot.collides_with(asteroid):
                        asteroid.split()
                        alien_shot.kill()

        # Always draw everything (even when paused)
        for obj in drawable:
            obj.draw(screen)
        
        if not game_over:
            # Display score and high score
            draw_score(screen, score, high_score if high_score_enabled else None)
            
            # Display pause message if paused
            if game_paused:
                draw_pause_message(screen)
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
    
    # Show alien warning when approaching spawn score
    if score >= ALIEN_SPAWN_SCORE - 5 and score < ALIEN_SPAWN_SCORE:
        warning_font = pygame.font.Font(None, 48)
        warning_text = warning_font.render("ALIEN INCOMING!", True, "#ff6b6b")
        warning_rect = warning_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(warning_text, warning_rect)

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

def draw_pause_message(screen):
    # Draw semi-transparent overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(128)  # Semi-transparent
    overlay.fill((0, 0, 0))  # Black overlay
    screen.blit(overlay, (0, 0))
    
    # Draw pause text
    font = pygame.font.Font(None, 72)
    pause_text = font.render("PAUSED", True, "#39d353")
    pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
    screen.blit(pause_text, pause_rect)
    
    # Draw instruction text
    instruction_font = pygame.font.Font(None, 36)
    instruction_text = instruction_font.render("Press SPACEBAR to continue", True, "white")
    instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
    screen.blit(instruction_text, instruction_rect)

if __name__ == "__main__":
    main()