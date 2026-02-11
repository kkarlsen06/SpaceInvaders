"""Background star entities."""

from __future__ import annotations

import random

import pygame

from space_invaders.constants import (
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    STAR_COUNT,
    STAR_MAX_SIZE,
    STAR_MAX_SPEED,
    STAR_MIN_SIZE,
    STAR_MIN_SPEED,
    WHITE,
)


class Star(pygame.sprite.Sprite):
    """A background star for parallax scrolling effect."""

    def __init__(self) -> None:
        super().__init__()
        size = random.randint(STAR_MIN_SIZE, STAR_MAX_SIZE)
        self.image = pygame.Surface((size, size))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(SCREEN_WIDTH)
        self.rect.y = random.randrange(SCREEN_HEIGHT)
        self.speed = random.uniform(STAR_MIN_SPEED, STAR_MAX_SPEED)

    def update(self, dt: float = 1 / 60) -> None:
        self.rect.y += self.speed * dt * 60
        if self.rect.top > SCREEN_HEIGHT:
            self.rect.y = -self.rect.height
            self.rect.x = random.randrange(SCREEN_WIDTH)


def create_stars(group: pygame.sprite.Group, count: int = STAR_COUNT) -> None:
    """Populate a sprite group with background stars."""
    for _ in range(count):
        group.add(Star())
