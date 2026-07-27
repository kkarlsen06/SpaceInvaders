"""Deep-space backdrop: nebula gradient plus a parallax starfield."""

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
from space_invaders.systems.postfx import make_radial_alpha

# Color palette for stars – subtle tints give depth
_STAR_COLORS = [
    Colors.STAR_WHITE,
    Colors.STAR_WARM,
    Colors.STAR_COOL,
    Colors.STAR_BLUE,
]

_backdrop_cache: dict[tuple[int, int], pygame.Surface] = {}
_star_sprite_cache: dict[tuple, pygame.Surface] = {}


# ---------------------------------------------------------------------------
# Backdrop
# ---------------------------------------------------------------------------

def make_backdrop(size: tuple[int, int] = (SCREEN_WIDTH, SCREEN_HEIGHT)) -> pygame.Surface:
    """Build (and cache) the static nebula backdrop drawn behind everything."""
    if size in _backdrop_cache:
        return _backdrop_cache[size]

    w, h = size
    surf = pygame.Surface(size).convert()

    # Vertical gradient: a 1x2 surface smoothscaled up is a free linear ramp.
    ramp = pygame.Surface((1, 2))
    ramp.set_at((0, 0), (9, 11, 24))
    ramp.set_at((0, 1), (4, 5, 12))
    surf.blit(pygame.transform.smoothscale(ramp, size), (0, 0))

    # Soft nebula clouds, blended additively so they only ever brighten.
    rng = random.Random(20260727)
    blob = make_radial_alpha(96, (255, 255, 255), max_alpha=255, falloff=2.6,
                             premultiplied=True)
    clouds = [
        ((26, 14, 60), 0.22, 0.30, 1.15),
        ((8, 38, 62), 0.78, 0.18, 0.95),
        ((48, 12, 44), 0.60, 0.74, 1.30),
        ((6, 32, 48), 0.14, 0.82, 1.05),
        ((24, 18, 54), 0.46, 0.50, 1.60),
    ]
    for color, fx, fy, scale in clouds:
        d = int(min(w, h) * scale)
        tinted = pygame.transform.smoothscale(blob, (d, int(d * 0.72)))
        tinted.fill(color, special_flags=pygame.BLEND_RGB_MULT)
        surf.blit(
            tinted,
            (int(w * fx) - tinted.get_width() // 2,
             int(h * fy) - tinted.get_height() // 2),
            special_flags=pygame.BLEND_RGB_ADD,
        )

    # A scatter of faint static pinpricks so the sky is never empty.
    for _ in range(220):
        x, y = rng.randrange(w), rng.randrange(h)
        v = rng.randint(30, 90)
        surf.fill((v, v, v + 10), (x, y, 1, 1), special_flags=pygame.BLEND_RGB_ADD)

    _backdrop_cache[size] = surf
    return surf


# ---------------------------------------------------------------------------
# Stars
# ---------------------------------------------------------------------------

def _star_sprite(size: int, color: tuple[int, ...], streak: int) -> pygame.Surface:
    """Cached star glyph: soft halo, hot core, optional motion streak."""
    key = (size, color[:3], streak)
    cached = _star_sprite_cache.get(key)
    if cached is not None:
        return cached

    glow_r = max(size * 3, 3)
    w = glow_r * 2
    h = glow_r * 2 + streak
    surf = pygame.Surface((w, h), pygame.SRCALPHA)

    halo = make_radial_alpha(glow_r * 2, color[:3], max_alpha=70, falloff=1.8)
    surf.blit(halo, (0, streak // 2))

    cx = w // 2
    if streak:
        # Elongate the core downwards: near stars smear as they fall.
        pygame.draw.line(surf, (*color[:3], 90), (cx, glow_r), (cx, glow_r + streak), 1)
    pygame.draw.circle(surf, (*color[:3], 255), (cx, glow_r + streak // 2),
                       max(size // 2, 1))

    _star_sprite_cache[key] = surf
    return surf


class Star(pygame.sprite.Sprite):
    """A parallax star. Depth drives size, speed, brightness and streaking."""

    def __init__(self) -> None:
        super().__init__()
        # depth 0 = far/slow/dim, 1 = near/fast/bright
        self.depth = random.random() ** 1.4
        self.size = STAR_MIN_SIZE + int(self.depth * (STAR_MAX_SIZE - STAR_MIN_SIZE) + 0.5)
        self.speed = STAR_MIN_SPEED + self.depth * (STAR_MAX_SPEED - STAR_MIN_SPEED)
        self.base_color = random.choice(_STAR_COLORS)

        self._twinkle_offset = random.uniform(0, 2 * math.pi)
        self._twinkle_speed = random.uniform(1.5, 4.0)
        self._base_alpha = int(70 + 185 * self.depth)

        # Only the very nearest stars smear; any more reads as visual noise.
        streak = int(max(0.0, self.depth - 0.72) * 22)
        # Each star owns a copy so per-star set_alpha twinkling stays independent.
        self.image = _star_sprite(self.size, self.base_color, streak).copy()

        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(SCREEN_WIDTH)
        self.rect.y = random.randrange(SCREEN_HEIGHT)
        self._y = float(self.rect.y)

    def update(self, dt: float = 1 / 60) -> None:
        self._y += self.speed * dt * 60
        if self._y > SCREEN_HEIGHT:
            self._y = -float(self.rect.height)
            self.rect.x = random.randrange(SCREEN_WIDTH)
        self.rect.y = int(self._y)

        t = pygame.time.get_ticks() / 1000.0
        flicker = math.sin(t * self._twinkle_speed + self._twinkle_offset)
        alpha = int(self._base_alpha * (0.65 + 0.35 * (flicker + 1) / 2))
        self.image.set_alpha(max(30, min(alpha, 255)))


def create_stars(group: pygame.sprite.Group, count: int = STAR_COUNT) -> None:
    """Populate a sprite group with background stars."""
    for _ in range(count):
        group.add(Star())
