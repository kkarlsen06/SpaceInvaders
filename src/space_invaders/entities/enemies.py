"""Enemy entities."""

from __future__ import annotations

import random

import pygame

from space_invaders.constants import (
    ENEMY_BASE_SIZE,
    ENEMY_MAX_SCALE,
    ENEMY_MIN_SCALE,
    ENEMY_SHOT_DELAY_MAX,
    ENEMY_SHOT_DELAY_MIN,
    ENEMY_SHOOT_PROBABILITY,
    NORMAL_ENEMY_POINTS,
    SCREEN_WIDTH,
    STRONG_ENEMY_BASE_SIZE,
    STRONG_ENEMY_MAX_SCALE,
    STRONG_ENEMY_MIN_SCALE,
    STRONG_ENEMY_POINTS,
    STRONG_ENEMY_SHOOT_PROBABILITY,
    DIFFICULTY_CONFIG,
)
from space_invaders.entities.projectiles import EnemyProjectile


class Enemy(pygame.sprite.Sprite):
    """Standard enemy that descends from the top of the screen."""

    def __init__(self, image: pygame.Surface, difficulty: int) -> None:
        super().__init__()
        self.scale_factor = random.uniform(ENEMY_MIN_SCALE, ENEMY_MAX_SCALE)
        size = int(ENEMY_BASE_SIZE * self.scale_factor)

        self.original_image = pygame.transform.scale(image, (size, size))
        self.angle = 0.0
        self.rotation_speed = random.uniform(-2, 2)
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)

        diff_cfg = DIFFICULTY_CONFIG[difficulty]
        lo, hi = diff_cfg["enemy_speed_range"]
        self.speed = random.randrange(lo, hi + 1)

        self.hits = 0
        self.max_hits = 1
        self.point_value = NORMAL_ENEMY_POINTS

        self.last_shot = pygame.time.get_ticks()
        self.shot_delay = random.randint(ENEMY_SHOT_DELAY_MIN, ENEMY_SHOT_DELAY_MAX)

    def update(self, dt: float = 1 / 60, difficulty: int | None = None,
               all_sprites: pygame.sprite.Group | None = None,
               enemy_projectile_group: pygame.sprite.Group | None = None) -> None:
        self.rect.y += self.speed * dt * 60

        # Rotate
        self.angle += self.rotation_speed
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        old_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = old_center

        if difficulty == 4 and all_sprites is not None and enemy_projectile_group is not None:
            now = pygame.time.get_ticks()
            if now - self.last_shot > self.shot_delay and random.random() < ENEMY_SHOOT_PROBABILITY:
                self.last_shot = now
                self._shoot(all_sprites, enemy_projectile_group)

    def _shoot(self, all_sprites: pygame.sprite.Group,
               enemy_projectile_group: pygame.sprite.Group) -> None:
        if self.rect.bottom > 0:
            proj = EnemyProjectile(self.rect.centerx, self.rect.bottom)
            all_sprites.add(proj)
            enemy_projectile_group.add(proj)


class StrongEnemy(Enemy):
    """Tougher enemy that takes two hits to destroy."""

    def __init__(self, image: pygame.Surface, difficulty: int) -> None:
        super().__init__(image, difficulty)
        self.scale_factor = random.uniform(STRONG_ENEMY_MIN_SCALE, STRONG_ENEMY_MAX_SCALE)
        size = int(STRONG_ENEMY_BASE_SIZE * self.scale_factor)

        self.original_image = pygame.transform.scale(image, (size, size))
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)

        diff_cfg = DIFFICULTY_CONFIG[difficulty]
        lo, hi = diff_cfg["strong_enemy_speed_range"]
        self.speed = random.randrange(lo, hi + 1)

        self.hits = 0
        self.max_hits = 2
        self.point_value = STRONG_ENEMY_POINTS
        self.rotation_speed = 0

    def update(self, dt: float = 1 / 60, difficulty: int | None = None,
               all_sprites: pygame.sprite.Group | None = None,
               enemy_projectile_group: pygame.sprite.Group | None = None) -> None:
        self.rect.y += self.speed * dt * 60

        if difficulty == 4 and all_sprites is not None and enemy_projectile_group is not None:
            now = pygame.time.get_ticks()
            if now - self.last_shot > self.shot_delay and random.random() < STRONG_ENEMY_SHOOT_PROBABILITY:
                self.last_shot = now
                self._shoot(all_sprites, enemy_projectile_group)
