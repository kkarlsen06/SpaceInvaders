"""Enemy entities."""

from __future__ import annotations

import math
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
        self.place(random.randrange(size, SCREEN_WIDTH - size),
                   random.randrange(-100, -40))

        diff_cfg = DIFFICULTY_CONFIG[difficulty]
        lo, hi = diff_cfg["enemy_speed_range"]
        self.speed = random.randrange(lo, hi + 1)

        self.hits = 0
        self.max_hits = 1
        self.point_value = NORMAL_ENEMY_POINTS
        self.flash = 0.0

        self.last_shot = pygame.time.get_ticks()
        self.shot_delay = random.randint(ENEMY_SHOT_DELAY_MIN, ENEMY_SHOT_DELAY_MAX)

    FLASH_TIME = 0.14

    def place(self, x: int, y: int) -> None:
        """Move to a position, keeping the float tracker in sync."""
        self._fx = float(x)
        self._fy = float(y)
        self.rect.center = (x, y)

    def _advance(self, dt: float) -> None:
        """Step the true float position and re-anchor the rect on it.

        Rotation re-derives the rect from a bounding box that changes size every
        frame; rounding that box was swallowing sub-pixel movement and making
        slow enemies stutter. The float position is the source of truth.
        """
        self._fy += self.speed * dt * 60
        self.rect.center = (int(self._fx), int(self._fy))

    def hit(self) -> None:
        """Register an incoming hit and kick off the impact flash."""
        self.hits += 1
        self.flash = self.FLASH_TIME

    def _apply_flash(self, dt: float) -> None:
        """Blow the sprite out to white briefly after taking a hit."""
        if self.flash <= 0:
            return
        self.flash = max(0.0, self.flash - dt)
        v = int(235 * (self.flash / self.FLASH_TIME) ** 0.5)
        if v > 0:
            self.image = self.image.copy()
            self.image.fill((v, v, v), special_flags=pygame.BLEND_RGB_ADD)

    def update(self, dt: float = 1 / 60, difficulty: int | None = None,
               all_sprites: pygame.sprite.Group | None = None,
               enemy_projectile_group: pygame.sprite.Group | None = None) -> None:
        # Rotate. Scaled by dt like everything else, so spin rate does not ride
        # on the frame rate — and so hitstop actually stops it.
        self.angle += self.rotation_speed * dt * 60
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect()
        self._advance(dt)
        self._apply_flash(dt)

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
        self.place(random.randrange(size, SCREEN_WIDTH - size),
                   random.randrange(-100, -40))

        diff_cfg = DIFFICULTY_CONFIG[difficulty]
        lo, hi = diff_cfg["strong_enemy_speed_range"]
        self.speed = random.randrange(lo, hi + 1)

        self.hits = 0
        self.max_hits = 2
        self.point_value = STRONG_ENEMY_POINTS
        self.rotation_speed = 0
        self.flash = 0.0
        self._pulse_offset = random.uniform(0, math.tau)

    def update(self, dt: float = 1 / 60, difficulty: int | None = None,
               all_sprites: pygame.sprite.Group | None = None,
               enemy_projectile_group: pygame.sprite.Group | None = None) -> None:
        self._advance(dt)

        # Pulsing energy shield; it burns hotter once already damaged.
        t = pygame.time.get_ticks() * 0.004 + self._pulse_offset
        glow = 0.5 + 0.5 * math.sin(t)
        heat = 0.35 + 0.65 * (self.hits / self.max_hits)
        tint = int(70 * glow * heat)
        self.image = self.original_image.copy()
        if tint > 2:
            self.image.fill((tint, int(tint * 0.25), int(tint * 0.55)),
                            special_flags=pygame.BLEND_RGB_ADD)
        self._apply_flash(dt)

        if difficulty == 4 and all_sprites is not None and enemy_projectile_group is not None:
            now = pygame.time.get_ticks()
            if now - self.last_shot > self.shot_delay and random.random() < STRONG_ENEMY_SHOOT_PROBABILITY:
                self.last_shot = now
                self._shoot(all_sprites, enemy_projectile_group)
