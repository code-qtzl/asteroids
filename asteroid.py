import pygame
import random
from circleshape import CircleShape
from constants import *


class Asteroid(CircleShape):
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)

    def draw(self, screen):
        pygame.draw.circle(screen, "#39d353", self.position, self.radius, 2)

    def update(self, dt):
        self.position += self.velocity * dt

    def split(self):
        self.kill()
        if self.radius <= ASTEROID_MIN_RADIUS:
            return
        else: 
            random_angle = random.uniform(20, 50)

            split_a = self.velocity.rotate(random_angle)
            split_b = self.velocity.rotate(-random_angle)

            new_radius = self.radius - ASTEROID_MIN_RADIUS

            new_astroid_a = Asteroid(self.position.x, self.position.y, new_radius)
            new_astroid_b = Asteroid(self.position.x, self.position.y, new_radius)

            new_astroid_a.velocity = split_a * 1.2
            new_astroid_b.velocity = split_b * 1.2