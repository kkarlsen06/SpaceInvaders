import pygame
import os
import random
import math

# Initialize pygame
pygame.init()

# Define dimensions for the background
WIDTH = 800
HEIGHT = 600

# Create the background surface
background = pygame.Surface((WIDTH, HEIGHT))

# Create a space-themed gradient background (dark blue to black)
for y in range(HEIGHT):
    # Calculate color - dark blue gradient to black
    color_value = max(0, 30 - int(y * 30 / HEIGHT))
    background.fill((0, 0, color_value), (0, y, WIDTH, 1))

# Add some stars
for _ in range(200):
    # Random position
    x = random.randint(0, WIDTH - 1)
    y = random.randint(0, HEIGHT - 1)
    
    # Random brightness (slightly yellowish white)
    brightness = random.randint(150, 255)
    color = (brightness, brightness, random.randint(brightness-50, brightness))
    
    # Random size (small stars)
    size = random.choice([1, 1, 1, 1, 2, 2, 3])
    
    # Draw the star
    pygame.draw.circle(background, color, (x, y), size)

# Add a few larger glows for bigger stars
for _ in range(20):
    x = random.randint(0, WIDTH - 1)
    y = random.randint(0, HEIGHT - 1)
    radius = random.randint(4, 8)
    
    # Create a subtle glow effect
    for r in range(radius, 0, -1):
        alpha = max(0, 150 - r * 30)
        color = (200, 200, 255, alpha)
        
        # Create a new surface for the glow
        glow = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
        pygame.draw.circle(glow, color, (r, r), r)
        
        # Blit the glow onto the background
        background.blit(glow, (x-r, y-r))

# Add a nebula-like effect in the corner
for _ in range(500):
    x = random.randint(0, WIDTH//3)
    y = random.randint(HEIGHT//2, HEIGHT)
    
    # Purple-ish nebula
    color = (
        random.randint(30, 80),
        0,
        random.randint(50, 120),
        random.randint(5, 30)
    )
    
    # Create a new surface for each nebula particle
    particle = pygame.Surface((10, 10), pygame.SRCALPHA)
    pygame.draw.circle(particle, color, (5, 5), random.randint(3, 8))
    
    # Apply the particle to the background
    background.blit(particle, (x, y))

# Make sure the assets directory exists
assets_folder = os.path.join(os.path.dirname(__file__), 'assets')
if not os.path.exists(assets_folder):
    os.makedirs(assets_folder)

# Save the background
pygame.image.save(background, os.path.join(assets_folder, 'background.jpg'))
print(f"Background saved to {os.path.join(assets_folder, 'background.jpg')}")
