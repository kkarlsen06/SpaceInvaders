"""Projectile entities (player shots and enemy projectiles).

Bolts are drawn as capsules with a baked-in motion tail. The tail lives inside
the sprite image, so ``rect`` is larger than the projectile really is — every
projectile therefore carries a tight ``hitbox`` that collision uses instead.
"""

from __future__ import annotations

import math
from typing import Callable

import pygame

from space_invaders.constants import (
    ENEMY_PROJECTILE_HEIGHT,
    ENEMY_PROJECTILE_SPEED,
    ENEMY_PROJECTILE_WIDTH,
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

LASER_COLOR = (110, 245, 255)
PELLET_COLOR = (255, 190, 80)
ENEMY_BOLT_COLOR = (255, 90, 120)

_bolt_cache: dict[tuple, pygame.Surface] = {}


def _make_bolt(w: int, h: int, color: tuple[int, int, int], tail: int,
               angle: float = 0.0) -> pygame.Surface:
    """Cached energy bolt: hot core, coloured capsule, fading tail below it.

    Built pointing up (head at top). The full-screen bloom pass supplies the
    outer glow, so nothing here needs a wide halo baked in.
    """
    key = (w, h, color, tail, angle)
    cached = _bolt_cache.get(key)
    if cached is not None:
        return cached

    pad = 2
    sw = w + pad * 2
    surf = pygame.Surface((sw, h + tail), pygame.SRCALPHA)
    cx = sw // 2

    if tail:
        tw = max(w - 2, 2)
        ramp = pygame.Surface((1, 2), pygame.SRCALPHA)
        ramp.set_at((0, 0), (*color, 150))
        ramp.set_at((0, 1), (*color, 0))
        surf.blit(pygame.transform.smoothscale(ramp, (tw, tail)), (cx - tw // 2, h))

    pygame.draw.rect(surf, (*color, 255), (cx - w // 2, 0, w, h),
                     border_radius=max(w // 2, 1))
    if w >= 5:
        pygame.draw.rect(surf, (255, 255, 255, 245),
                         (cx - w // 4, 2, max(w // 2, 1), h - 4),
                         border_radius=max(w // 4, 1))

    if angle:
        surf = pygame.transform.rotate(surf, -angle)

    _bolt_cache[key] = surf
    return surf


class Shot(pygame.sprite.Sprite):
    """Standard player laser bolt."""

    tail = 30
    color = LASER_COLOR
    bolt_size = (SHOT_WIDTH, SHOT_HEIGHT)

    def __init__(self, x: int, y: int) -> None:
        super().__init__()
        bw, bh = self.bolt_size
        self.image = _make_bolt(bw, bh, self.color, self.tail)
        self.rect = self.image.get_rect(midtop=(x, y - bh))
        self.hitbox = pygame.Rect(0, 0, bw, bh)
        self.hitbox.midtop = self.rect.midtop
        self.speed = SHOT_SPEED_NORMAL
        self.hit_enemy = False

    def _sync_hitbox(self) -> None:
        self.hitbox.center = (self.rect.centerx, self.rect.top + self.hitbox.height // 2)

    def update(self, dt: float = 1 / 60, reset_multiplier_func: Callable | None = None) -> None:
        self.rect.y += self.speed * dt * 60
        self._sync_hitbox()
        if self.rect.bottom < 0:
            if not self.hit_enemy and reset_multiplier_func and not isinstance(self, ShotgunShot):
                reset_multiplier_func()
            self.kill()


class ShotgunShot(Shot):
    """Shotgun pellet with angular spread."""

    tail = 14
    color = PELLET_COLOR
    bolt_size = (SHOTGUN_PELLET_WIDTH, SHOTGUN_PELLET_HEIGHT)

    def __init__(self, x: int, y: int, angle: float = 0) -> None:
        super().__init__(x, y)
        bw, bh = self.bolt_size
        self.image = _make_bolt(bw, bh, self.color, self.tail, angle=angle)
        self.rect = self.image.get_rect(center=(x, y - bh // 2))
        self.hitbox = pygame.Rect(0, 0, bw, bh)
        self.hitbox.center = self.rect.center

        self.angle = math.radians(angle)
        self.range = SHOTGUN_RANGE
        self.distance_traveled = 0
        self.horizontal_speed = math.sin(self.angle) * SHOTGUN_HORIZONTAL_SPEED_FACTOR

    def _sync_hitbox(self) -> None:
        self.hitbox.center = self.rect.center

    def update(self, dt: float = 1 / 60, reset_multiplier_func: Callable | None = None) -> None:
        self.rect.y += self.speed * dt * 60
        self.rect.x += self.horizontal_speed * dt * 60
        self.distance_traveled += abs(self.speed * dt * 60)
        self._sync_hitbox()

        if (self.rect.bottom < 0 or self.rect.left > SCREEN_WIDTH
                or self.rect.right < 0 or self.distance_traveled > self.range):
            if not self.hit_enemy and reset_multiplier_func:
                reset_multiplier_func()
            self.kill()


class EnemyProjectile(pygame.sprite.Sprite):
    """Projectile fired by enemies in Impossible mode."""

    def __init__(self, x: int, y: int) -> None:
        super().__init__()
        bw, bh = ENEMY_PROJECTILE_WIDTH, ENEMY_PROJECTILE_HEIGHT
        # Same bolt, flipped so the tail trails above a downward-moving shot.
        self.image = pygame.transform.flip(
            _make_bolt(bw, bh, ENEMY_BOLT_COLOR, 24), False, True)
        self.rect = self.image.get_rect(midbottom=(x, y + bh))
        self.hitbox = pygame.Rect(0, 0, bw, bh)
        self.hitbox.midbottom = self.rect.midbottom
        self.speed = ENEMY_PROJECTILE_SPEED

    def update(self, dt: float = 1 / 60) -> None:
        self.rect.y += self.speed * dt * 60
        self.hitbox.midbottom = self.rect.midbottom
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


def hitbox_collide(a: pygame.sprite.Sprite, b: pygame.sprite.Sprite) -> bool:
    """Collision callback that prefers a sprite's tight ``hitbox`` over ``rect``."""
    return getattr(a, "hitbox", a.rect).colliderect(getattr(b, "hitbox", b.rect))
