"""Background star entities with depth, color, and twinkling."""

from __future__ import annotations

import math
import random

import pygame

from space_invaders.constants import (
    Colors,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    STAR_COUNT,
    STAR_MAX_SIZE,
    STAR_MAX_SPEED,
    STAR_MIN_SIZE,
    STAR_MIN_SPEED,
)

# Color palette for stars – subtle tints give depth
_STAR_COLORS = [
    Colors.STAR_WHITE,
    Colors.STAR_WARM,
    Colors.STAR_COOL,
    Colors.STAR_BLUE,
]


class Star(pygame.sprite.Sprite):
    """A background star with parallax scrolling, color, and twinkling."""

    def __init__(self) -> None:
        super().__init__()
        self.size = random.randint(STAR_MIN_SIZE, STAR_MAX_SIZE)
        self.base_color = random.choice(_STAR_COLORS)
        self.speed = random.uniform(STAR_MIN_SPEED, STAR_MAX_SPEED)

        # Twinkle
        self._twinkle_offset = random.uniform(0, 2 * math.pi)
        self._twinkle_speed = random.uniform(1.5, 4.0)
        self._base_alpha = random.randint(140, 255)

        # Pre-render the star surface once
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        c = self.base_color
        if self.size <= 1:
            self.image.set_at((0, 0), (*c[:3], 255))
        else:
            center = self.size // 2
            for dy in range(self.size):
                for dx in range(self.size):
                    dist = math.sqrt((dx - center) ** 2 + (dy - center) ** 2)
                    if dist <= center:
                        a = int(255 * (1 - dist / max(center, 1)))
                        self.image.set_at((dx, dy), (*c[:3], min(a, 255)))

        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(SCREEN_WIDTH)
        self.rect.y = random.randrange(SCREEN_HEIGHT)
        self._y = float(self.rect.y)

    def update(self, dt: float = 1 / 60) -> None:
        self._y += self.speed * dt * 60
        if self._y > SCREEN_HEIGHT:
            self._y = -self.size
            self.rect.x = random.randrange(SCREEN_WIDTH)
        self.rect.y = int(self._y)

        # Twinkle via set_alpha (cheap)
        t = pygame.time.get_ticks() / 1000.0
        flicker = math.sin(t * self._twinkle_speed + self._twinkle_offset)
        alpha = int(self._base_alpha * (0.65 + 0.35 * (flicker + 1) / 2))
        self.image.set_alpha(max(40, min(alpha, 255)))


def create_stars(group: pygame.sprite.Group, count: int = STAR_COUNT) -> None:
    """Populate a sprite group with background stars."""
    for _ in range(count):
        group.add(Star())
