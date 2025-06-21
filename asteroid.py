import pygame
import random
import math
from circleshape import CircleShape
from constants import *


class Asteroid(CircleShape):
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)
        self.shape_points = self._generate_irregular_shape()
        self.rotation = 0
        self.rotation_speed = random.uniform(-50, 50)  # degrees per second

    def _generate_irregular_shape(self):
        """Generate an irregular asteroid shape with random variations"""
        points = []
        num_points = random.randint(8, 12)  # Number of points around the circle
        
        for i in range(num_points):
            # Calculate angle for this point
            angle = (2 * math.pi * i) / num_points
            
            # Add some randomness to the radius (70% to 100% of full radius)
            radius_variation = random.uniform(0.7, 1.0)
            point_radius = self.radius * radius_variation
            
            # Calculate the point position relative to center
            x = point_radius * math.cos(angle)
            y = point_radius * math.sin(angle)
            
            points.append((x, y))
        
        return points

    def _get_rotated_points(self):
        """Get the asteroid points rotated by current rotation angle"""
        rotated_points = []
        cos_rot = math.cos(math.radians(self.rotation))
        sin_rot = math.sin(math.radians(self.rotation))
        
        for x, y in self.shape_points:
            # Rotate the point
            rotated_x = x * cos_rot - y * sin_rot
            rotated_y = x * sin_rot + y * cos_rot
            
            # Translate to world position
            world_x = rotated_x + self.position.x
            world_y = rotated_y + self.position.y
            
            rotated_points.append((world_x, world_y))
        
        return rotated_points

    def draw(self, screen):
        # Get the current rotated points
        points = self._get_rotated_points()
        
        # Draw the irregular asteroid shape
        if len(points) >= 3:
            pygame.draw.polygon(screen, "#39d353", points, 2)
        
        # Optional: Draw collision circle for debugging (comment out for final version)
        # pygame.draw.circle(screen, "#ff0000", self.position, self.radius, 1)

    def update(self, dt):
        self.position += self.velocity * dt
        self.rotation += self.rotation_speed * dt

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