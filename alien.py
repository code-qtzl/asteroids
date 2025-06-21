import pygame
import random
import math
from circleshape import CircleShape
from constants import *


class AlienShot(CircleShape):
    def __init__(self, x, y):
        super().__init__(x, y, SHOT_RADIUS)

    def draw(self, screen):
        pygame.draw.circle(screen, "red", self.position, self.radius, 2)

    def update(self, dt):
        self.position += self.velocity * dt
        # Remove shot if it goes off screen
        if (self.position.x < -50 or self.position.x > SCREEN_WIDTH + 50 or
            self.position.y < -50 or self.position.y > SCREEN_HEIGHT + 50):
            self.kill()


class AlienShip(CircleShape):
    def __init__(self):
        # Spawn from random side of screen, but ensure it flies ACROSS the screen
        side = random.randint(0, 1)  # 0=left, 1=right (only horizontal movement)
        
        if side == 0:  # Left side - fly to right
            x = -ALIEN_RADIUS
            y = random.randint(ALIEN_RADIUS + 50, SCREEN_HEIGHT - ALIEN_RADIUS - 50)
            # Fly towards right side with slight vertical component
            target_x = SCREEN_WIDTH + ALIEN_RADIUS
            target_y = random.randint(ALIEN_RADIUS + 50, SCREEN_HEIGHT - ALIEN_RADIUS - 50)
        else:  # Right side - fly to left
            x = SCREEN_WIDTH + ALIEN_RADIUS
            y = random.randint(ALIEN_RADIUS + 50, SCREEN_HEIGHT - ALIEN_RADIUS - 50)
            # Fly towards left side with slight vertical component
            target_x = -ALIEN_RADIUS
            target_y = random.randint(ALIEN_RADIUS + 50, SCREEN_HEIGHT - ALIEN_RADIUS - 50)
        
        super().__init__(x, y, ALIEN_RADIUS)
        
        # Calculate velocity to reach target
        direction = pygame.Vector2(target_x - x, target_y - y)
        if direction.length() > 0:
            self.velocity = direction.normalize() * ALIEN_SPEED
        else:
            self.velocity = pygame.Vector2(ALIEN_SPEED if side == 0 else -ALIEN_SPEED, 0)
        
        self.shoot_timer = 0
        self.direction_change_timer = 0
        self.direction_change_interval = random.uniform(3, 5)  # Less frequent direction changes
        self.base_velocity = self.velocity.copy()  # Store original direction

    def draw(self, screen):
        # Draw alien ship as a diamond/UFO shape
        points = [
            (self.position.x, self.position.y - self.radius),  # Top
            (self.position.x + self.radius, self.position.y),  # Right
            (self.position.x, self.position.y + self.radius),  # Bottom
            (self.position.x - self.radius, self.position.y)   # Left
        ]
        pygame.draw.polygon(screen, "#ff6b6b", points, 2)
        
        # Draw a small center dot
        pygame.draw.circle(screen, "#ff6b6b", self.position, 3)

    def update(self, dt, player_position, alien_shots_group, asteroids_group):
        # Store old position for collision checking
        old_position = self.position.copy()
        
        # Move the alien
        self.position += self.velocity * dt
        
        # Check collision with asteroids and bounce off them
        for asteroid in asteroids_group:
            if self.collides_with(asteroid):
                # Restore old position
                self.position = old_position
                
                # Calculate bounce direction (away from asteroid)
                bounce_direction = self.position - asteroid.position
                if bounce_direction.length() > 0:
                    bounce_direction = bounce_direction.normalize()
                    # Maintain speed but change direction
                    self.velocity = bounce_direction * ALIEN_SPEED
                    # Add some randomness to avoid getting stuck
                    angle_offset = random.uniform(-30, 30)
                    self.velocity = self.velocity.rotate(angle_offset)
                break
        
        # Update timers
        self.shoot_timer += dt
        self.direction_change_timer += dt
        
        # Occasionally make small direction adjustments (but keep general direction)
        if self.direction_change_timer >= self.direction_change_interval:
            self.direction_change_timer = 0
            self.direction_change_interval = random.uniform(3, 5)
            
            # Small course correction towards base direction
            angle_change = random.uniform(-20, 20)
            self.velocity = self.velocity.rotate(angle_change)
            
            # Ensure alien maintains proper speed
            if self.velocity.length() > 0:
                self.velocity = self.velocity.normalize() * ALIEN_SPEED
            else:
                # Fallback to base velocity if something goes wrong
                self.velocity = self.base_velocity.copy()
        
        # Shoot at player
        if self.shoot_timer >= ALIEN_SHOOT_COOLDOWN:
            self.shoot_at_player(player_position, alien_shots_group)
            self.shoot_timer = 0
        
        # Remove alien if it goes too far off screen
        if (self.position.x < -200 or self.position.x > SCREEN_WIDTH + 200 or
            self.position.y < -200 or self.position.y > SCREEN_HEIGHT + 200):
            self.kill()

    def shoot_at_player(self, player_position, alien_shots_group):
        # Calculate direction to player
        direction = player_position - self.position
        if direction.length() > 0:
            direction = direction.normalize()
            
            # Add some inaccuracy to make it challenging but not impossible
            angle_offset = random.uniform(-15, 15)  # degrees
            direction = direction.rotate(angle_offset)
            
            # Create alien shot
            shot = AlienShot(self.position.x, self.position.y)
            shot.velocity = direction * ALIEN_SHOOT_SPEED
            alien_shots_group.add(shot)
        else:
            # If player is exactly at alien position (very unlikely), shoot in random direction
            angle = random.uniform(0, 360)
            direction = pygame.Vector2(1, 0).rotate(angle)
            
            shot = AlienShot(self.position.x, self.position.y)
            shot.velocity = direction * ALIEN_SHOOT_SPEED
            alien_shots_group.add(shot)
