"""Pickup entities (power bonuses)."""

from __future__ import annotations

import random

import pygame

from space_invaders.constants import (
    BLACK,
    BLUE,
    BONUS_SIZE,
    BONUS_SPEED,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)


class PowerBonus(pygame.sprite.Sprite):
    """Falling life pickup that grants the player an extra life."""

    def __init__(self, life_image: pygame.Surface | None = None) -> None:
        super().__init__()
        if life_image:
            self.image = pygame.transform.scale(life_image, (BONUS_SIZE, BONUS_SIZE))
        else:
            self.image = pygame.Surface((BONUS_SIZE, BONUS_SIZE))
            pygame.draw.circle(self.image, BLUE, (BONUS_SIZE // 2, BONUS_SIZE // 2), BONUS_SIZE // 2)
            self.image.set_colorkey(BLACK)

        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speed = BONUS_SPEED

    def update(self, dt: float = 1 / 60) -> None:
        self.rect.y += self.speed * dt * 60
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
