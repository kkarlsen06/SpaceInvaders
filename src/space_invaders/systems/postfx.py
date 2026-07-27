"""Full-screen post-processing: bloom, vignette, RGB split, shake, flash.

The game never draws to the display directly. It draws to :attr:`PostFX.world`,
and :meth:`present` composites that surface onto the real display with the
effects applied. Everything here is plain surface blits — no per-pixel Python
loops — so the whole chain costs a couple of milliseconds at 720p.
"""

from __future__ import annotations

import math

import pygame

from space_invaders.constants import (
    ABERRATION_MAX,
    BLOOM_DOWNSCALE,
    BLOOM_STRENGTH,
    BLOOM_THRESHOLD,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TRAUMA_DECAY,
    TRAUMA_MAX_OFFSET,
    TRAUMA_SHAKE_FREQ,
    VIGNETTE_STRENGTH,
)


def set_display_mode(fullscreen: bool) -> pygame.Surface:
    """Open the window. SCALED keeps the logical 720p size and letterboxes it,
    and also remaps mouse coordinates back into logical space for free."""
    flags = pygame.SCALED | (pygame.FULLSCREEN if fullscreen else 0)
    try:
        return pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags, vsync=1)
    except pygame.error:
        return pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)


def make_radial_alpha(
    size: int,
    color: tuple[int, int, int],
    inner: float = 0.0,
    max_alpha: int = 255,
    falloff: float = 1.0,
    premultiplied: bool = False,
) -> pygame.Surface:
    """Build a small radial-gradient surface, opaque in the middle.

    Cheap because it is built once at a low resolution from concentric circles
    and then scaled up wherever it is needed.

    Additive blends (``BLEND_RGB_ADD``/``BLEND_RGBA_ADD``) ignore the alpha
    channel entirely, so a plain alpha gradient blits as a flat disc. Pass
    ``premultiplied=True`` to fold the falloff into RGB as well, which is what
    every additive caller wants.
    """
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    r = size // 2
    for i in range(r, 0, -1):
        t = i / r
        if t <= inner:
            a = max_alpha
        else:
            a = int(max_alpha * (1 - (t - inner) / max(1 - inner, 1e-6)) ** falloff)
        a = max(0, min(a, 255))
        rgb = tuple(c * a // 255 for c in color) if premultiplied else color
        pygame.draw.circle(surf, (*rgb, a), (r, r), i)
    return surf


def _make_vignette(size: tuple[int, int], strength: int) -> pygame.Surface:
    """Dark, soft-edged frame. Built at 128px and scaled up to avoid banding."""
    n = 128
    small = pygame.Surface((n, n), pygame.SRCALPHA)
    small.fill((0, 0, 0, strength))
    r = n // 2
    for i in range(r, 0, -1):
        d = i / r
        a = int(strength * max(0.0, (d - 0.45) / 0.55) ** 1.7)
        pygame.draw.circle(small, (0, 0, 0, a), (r, r), i)
    return pygame.transform.smoothscale(small, size).convert_alpha()


class PostFX:
    """Owns the offscreen render target and the present-time effect chain."""

    def __init__(self, size: tuple[int, int]) -> None:
        self.size = size
        self.world = pygame.Surface(size).convert()

        w, h = size
        self._bloom_a = (max(w // BLOOM_DOWNSCALE, 2), max(h // BLOOM_DOWNSCALE, 2))
        self._bloom_b = (max(self._bloom_a[0] // 2, 2), max(self._bloom_a[1] // 2, 2))
        self._vignette = _make_vignette(size, VIGNETTE_STRENGTH)

        # Scratch surfaces, allocated once. Surface.fill() with a blend flag
        # takes an unaccelerated path in SDL (~3ms at 720p); blitting a solid
        # surface with the same flag is ~40x faster, so every full-screen blend
        # op below goes through one of these instead of fill().
        self._bright = pygame.Surface(size).convert()
        self._solid = pygame.Surface(size).convert()
        self._threshold = pygame.Surface(size).convert()
        self._threshold.fill(BLOOM_THRESHOLD)
        self._split_a = pygame.Surface(size).convert()
        self._split_b = pygame.Surface(size).convert()
        self._mask_red = pygame.Surface(size).convert()
        self._mask_red.fill((255, 0, 0))
        self._mask_cyan = pygame.Surface(size).convert()
        self._mask_cyan.fill((0, 255, 255))

        self.trauma = 0.0
        self._time = 0.0
        self._flash: tuple[float, float, tuple[int, int, int]] = (0.0, 1.0, (255, 255, 255))
        self.bloom_enabled = True

    # ------------------------------------------------------------------
    # Effect triggers
    # ------------------------------------------------------------------

    def shake(self, amount: float) -> None:
        """Add trauma (0..1). Decays automatically; offset scales with trauma²."""
        self.trauma = min(1.0, self.trauma + amount)

    def flash(self, duration: float = 0.09,
              color: tuple[int, int, int] = (255, 255, 255)) -> None:
        """Trigger a brief additive full-screen flash."""
        self._flash = (duration, duration, color)

    def update(self, dt: float) -> None:
        self._time += dt
        self.trauma = max(0.0, self.trauma - TRAUMA_DECAY * dt)
        remaining, total, color = self._flash
        if remaining > 0:
            self._flash = (max(0.0, remaining - dt), total, color)

    # ------------------------------------------------------------------
    # Present
    # ------------------------------------------------------------------

    def _shake_offset(self) -> tuple[int, int]:
        if self.trauma <= 0.001:
            return (0, 0)
        mag = TRAUMA_MAX_OFFSET * self.trauma * self.trauma
        t = self._time * TRAUMA_SHAKE_FREQ
        # Two incommensurable frequencies per axis reads as noise, not a wobble.
        ox = mag * (math.sin(t) * 0.6 + math.sin(t * 2.31 + 1.7) * 0.4)
        oy = mag * (math.sin(t * 1.13 + 0.9) * 0.6 + math.sin(t * 2.79) * 0.4)
        return (int(ox), int(oy))

    def _apply_bloom(self) -> None:
        # Threshold at full resolution. Doing it after the downscale averages a
        # 2px laser over a whole block and leaves nothing above the cut, which
        # is why thin bright things have to be isolated first.
        self._bright.blit(self.world, (0, 0))
        self._bright.blit(self._threshold, (0, 0), special_flags=pygame.BLEND_RGB_SUB)

        # Two-step downscale, then back up — a cheap wide gaussian-ish blur.
        small = pygame.transform.smoothscale(self._bright, self._bloom_a)
        small = pygame.transform.smoothscale(small, self._bloom_b)
        s = BLOOM_STRENGTH
        small.fill((s, s, s), special_flags=pygame.BLEND_RGB_MULT)
        bloom = pygame.transform.smoothscale(small, self.size)
        self.world.blit(bloom, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    def present(self, display: pygame.Surface) -> None:
        """Composite the world onto the display and flip."""
        if self.bloom_enabled:
            self._apply_bloom()

        self.world.blit(self._vignette, (0, 0))

        remaining, total, color = self._flash
        if remaining > 0:
            k = remaining / total
            # Plain fill (no blend flag) is memset-fast; the blend happens on
            # the blit.
            self._solid.fill(tuple(int(c * k * 0.85) for c in color))
            self.world.blit(self._solid, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

        ox, oy = self._shake_offset()
        split = int(ABERRATION_MAX * self.trauma)

        if ox or oy or split:
            display.fill((0, 0, 0))

        if split >= 1:
            # Split the red channel from green+blue and offset them apart.
            # Recombining them additively is lossless at split == 0.
            self._split_a.blit(self.world, (0, 0))
            self._split_a.blit(self._mask_red, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
            self._split_b.blit(self.world, (0, 0))
            self._split_b.blit(self._mask_cyan, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
            display.blit(self._split_a, (ox + split, oy))
            display.blit(self._split_b, (ox - split, oy), special_flags=pygame.BLEND_RGB_ADD)
        else:
            display.blit(self.world, (ox, oy))

        pygame.display.flip()
