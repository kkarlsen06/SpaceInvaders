"""Projectile entities (player shots and enemy projectiles)."""

from __future__ import annotations

import math
from typing import Callable

import pygame

from space_invaders.constants import (
    CYAN,
    ENEMY_PROJECTILE_HEIGHT,
    ENEMY_PROJECTILE_SPEED,
    ENEMY_PROJECTILE_WIDTH,
    ORANGE,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SHOT_HEIGHT,
    SHOT_SPEED_NORMAL,
    SHOT_WIDTH,
    SHOTGUN_HORIZONTAL_SPEED_FACTOR,
    SHOTGUN_PELLET_HEIGHT,
    SHOTGUN_PELLET_WIDTH,
    SHOTGUN_RANGE,
)


class Shot(pygame.sprite.Sprite):
    """Standard player laser shot."""

    def __init__(self, x: int, y: int) -> None:
        super().__init__()
        self.image = pygame.Surface((SHOT_WIDTH, SHOT_HEIGHT))
        self.image.fill(CYAN)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = SHOT_SPEED_NORMAL
        self.hit_enemy = False

    def update(self, dt: float = 1 / 60, reset_multiplier_func: Callable | None = None) -> None:
        self.rect.y += self.speed * dt * 60
        if self.rect.bottom < 0:
            if not self.hit_enemy and reset_multiplier_func and not isinstance(self, ShotgunShot):
                reset_multiplier_func()
            self.kill()


class ShotgunShot(Shot):
    """Shotgun pellet with angular spread."""

    def __init__(self, x: int, y: int, angle: float = 0) -> None:
        super().__init__(x, y)
        self.image = pygame.Surface((SHOTGUN_PELLET_WIDTH, SHOTGUN_PELLET_HEIGHT))
        self.image.fill(ORANGE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.angle = math.radians(angle)
        self.range = SHOTGUN_RANGE
        self.distance_traveled = 0
        self.horizontal_speed = math.sin(self.angle) * SHOTGUN_HORIZONTAL_SPEED_FACTOR

    def update(self, dt: float = 1 / 60, reset_multiplier_func: Callable | None = None) -> None:
        self.rect.y += self.speed * dt * 60
        self.rect.x += self.horizontal_speed * dt * 60
        self.distance_traveled += abs(self.speed * dt * 60)

        if (self.rect.bottom < 0 or self.rect.left > SCREEN_WIDTH
                or self.rect.right < 0 or self.distance_traveled > self.range):
            if not self.hit_enemy and reset_multiplier_func:
                reset_multiplier_func()
            self.kill()


class EnemyProjectile(pygame.sprite.Sprite):
    """Projectile fired by enemies in Impossible mode."""

    def __init__(self, x: int, y: int) -> None:
        super().__init__()
        self.image = pygame.Surface((ENEMY_PROJECTILE_WIDTH, ENEMY_PROJECTILE_HEIGHT))
        self.image.fill(ORANGE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.speed = ENEMY_PROJECTILE_SPEED

    def update(self, dt: float = 1 / 60) -> None:
        self.rect.y += self.speed * dt * 60
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
