"""Visual effect entities (explosions, sparks, popups, electric whip).

All effects are time-based rather than frame-counted, so they look identical
whatever the frame rate, and they lean on cached gradient surfaces instead of
per-pixel work.
"""

from __future__ import annotations

import math
import random

import pygame

from space_invaders.constants import (
    Colors,
    ELECTRICAL_PARTICLE_LIFETIME,
    EXPLOSION_SIZE,
    PARTICLE_SIZE,
    PARTICLE_LIFETIME,
    POPUP_LIFETIME,
    POPUP_RISE,
    WHIP_ANGULAR_SPEED,
    WHIP_HIT_ANGLE_TOLERANCE,
)
from space_invaders.systems.postfx import make_radial_alpha

_GLOW_RES = 64
_glow_cache: dict[tuple, pygame.Surface] = {}


def _glow(color: tuple[int, int, int], inner: float = 0.0,
          falloff: float = 1.8, premultiplied: bool = False) -> pygame.Surface:
    """Cached white-hot radial gradient, tinted to *color*."""
    key = (color, inner, falloff, premultiplied)
    surf = _glow_cache.get(key)
    if surf is None:
        surf = make_radial_alpha(_GLOW_RES, color, inner=inner, falloff=falloff,
                                 premultiplied=premultiplied)
        _glow_cache[key] = surf
    return surf


def _scaled_glow(color: tuple[int, int, int], diameter: int, alpha: int,
                 inner: float = 0.0, falloff: float = 1.8,
                 additive: bool = False) -> pygame.Surface:
    """Resize a cached glow and dim it to *alpha* (0-255).

    Blend modes ignore per-surface alpha, so an additive glow carries its
    falloff in RGB and is dimmed by scaling RGB instead.
    """
    g = pygame.transform.smoothscale(
        _glow(color, inner, falloff, premultiplied=additive), (diameter, diameter))
    a = max(0, min(alpha, 255))
    if additive:
        g.fill((a, a, a), special_flags=pygame.BLEND_RGB_MULT)
    else:
        g.set_alpha(a)
    return g


class Explosion(pygame.sprite.Sprite):
    """Layered blast: hot core, orange fireball, expanding shockwave ring."""

    duration = 0.42

    def __init__(self, center: tuple[int, int], scale: float = 1.0) -> None:
        super().__init__()
        self.size = int(EXPLOSION_SIZE * scale)
        span = self.size * 3
        self.image = pygame.Surface((span, span), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=center)
        self.elapsed = 0.0
        self._draw()

    def _draw(self) -> None:
        self.image.fill((0, 0, 0, 0))
        span = self.image.get_width()
        cx = cy = span // 2
        p = min(self.elapsed / self.duration, 1.0)

        # Fireball: outer smoke, mid orange, white core — each shrinking.
        if p < 0.85:
            k = p / 0.85
            for color, rad_f, alpha_f, falloff in (
                (Colors.EXPLOSION_OUTER[:3], 1.55, 0.50, 1.5),
                (Colors.EXPLOSION_MID[:3], 1.00, 0.80, 1.8),
                (Colors.EXPLOSION_CORE[:3], 0.52, 1.00, 2.4),
            ):
                d = int(self.size * rad_f * (1.0 + 0.55 * k) * (1 - k * 0.35))
                a = int(255 * alpha_f * (1 - k) ** 1.3)
                if d > 2 and a > 2:
                    g = _scaled_glow(color, d, a, falloff=falloff, additive=True)
                    self.image.blit(g, (cx - d // 2, cy - d // 2),
                                    special_flags=pygame.BLEND_RGBA_ADD)

        # Shockwave: a soft annulus, not an outline. Built by punching a hole
        # in a scaled glow so the ring keeps a gradient on both edges.
        ring_r = int(self.size * (0.4 + 1.5 * (1 - (1 - p) ** 2)))
        ring_a = int(210 * (1 - p) ** 1.7)
        if ring_a > 3 and ring_r > 4:
            d = ring_r * 2
            ring = _scaled_glow(Colors.EXPLOSION_RING[:3], d, ring_a,
                                inner=0.82, falloff=2.0, additive=True)
            hole = max(2, ring_r - max(3, int(self.size * 0.30 * (1 - p)) + 2))
            pygame.draw.circle(ring, (0, 0, 0, 0), (ring_r, ring_r), hole)
            self.image.blit(ring, (cx - ring_r, cy - ring_r),
                            special_flags=pygame.BLEND_RGBA_ADD)

    def update(self, dt: float = 1 / 60) -> None:
        self.elapsed += dt
        if self.elapsed >= self.duration:
            self.kill()
        else:
            self._draw()


class Particle(pygame.sprite.Sprite):
    """Spark with drag, shrink and colour fade."""

    def __init__(
        self,
        pos: tuple[int, int],
        angle: float,
        speed: float,
        color: tuple[int, ...] | None = None,
        size: int = PARTICLE_SIZE,
    ) -> None:
        super().__init__()
        self._color = tuple((color or Colors.PRIMARY)[:3])
        self.base_size = size
        self.image = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=pos)
        self.x = float(pos[0])
        self.y = float(pos[1])
        self.velocity_x = math.cos(angle) * speed
        self.velocity_y = math.sin(angle) * speed
        self.lifetime = PARTICLE_LIFETIME
        self.max_lifetime = PARTICLE_LIFETIME
        self._redraw()

    def _redraw(self) -> None:
        fade = max(self.lifetime / self.max_lifetime, 0.0)
        self.image.fill((0, 0, 0, 0))
        d = max(2, int(self.base_size * 2 * fade))
        a = int(255 * fade ** 0.6)
        g = _scaled_glow(self._color, d, a, inner=0.25, falloff=1.5)
        c = self.image.get_width() // 2
        self.image.blit(g, (c - d // 2, c - d // 2))

    def update(self, dt: float = 1 / 60) -> None:
        step = dt * 60
        self.x += self.velocity_x * step
        self.y += self.velocity_y * step
        # Drag, so sparks decelerate instead of flying off at constant speed.
        drag = 0.94 ** step
        self.velocity_x *= drag
        self.velocity_y *= drag
        self.rect.center = (int(self.x), int(self.y))
        self.lifetime -= step
        if self.lifetime <= 0:
            self.kill()
        else:
            self._redraw()


class ElectricalParticle(Particle):
    """Electric-blue particle with flickering effect."""

    def __init__(self, pos: tuple[int, int], angle: float, speed: float) -> None:
        super().__init__(pos, angle, speed, color=(120, 210, 255))
        self.lifetime = ELECTRICAL_PARTICLE_LIFETIME
        self.max_lifetime = ELECTRICAL_PARTICLE_LIFETIME

    def update(self, dt: float = 1 / 60) -> None:
        self._color = (215, 240, 255) if random.random() < 0.5 else (90, 165, 255)
        super().update(dt)


class ScorePopup(pygame.sprite.Sprite):
    """Floating "+N" that rises from a kill and fades out."""

    def __init__(self, pos: tuple[int, int], text: str, font: pygame.font.Font,
                 color: tuple[int, ...] = Colors.SECONDARY) -> None:
        super().__init__()
        self._base = font.render(text, True, color[:3])
        self.image = self._base.copy()
        self.rect = self.image.get_rect(center=pos)
        self._origin = pos
        self.elapsed = 0.0

    def update(self, dt: float = 1 / 60) -> None:
        self.elapsed += dt
        p = self.elapsed / POPUP_LIFETIME
        if p >= 1.0:
            self.kill()
            return
        # Ease-out rise, alpha holds then falls off in the last 40%.
        rise = POPUP_RISE * (1 - (1 - p) ** 3)
        self.rect.center = (self._origin[0], int(self._origin[1] - rise))
        self.image = self._base.copy()
        self.image.set_alpha(int(255 * min(1.0, (1 - p) / 0.4)))


class MuzzleFlash(pygame.sprite.Sprite):
    """Short-lived bloom at the gun barrel."""

    duration = 0.07

    def __init__(self, pos: tuple[int, int],
                 color: tuple[int, int, int] = (170, 245, 255),
                 size: int = 44) -> None:
        super().__init__()
        self.size = size
        self.color = color
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=pos)
        self.elapsed = 0.0
        self._draw()

    def _draw(self) -> None:
        p = min(self.elapsed / self.duration, 1.0)
        self.image.fill((0, 0, 0, 0))
        d = int(self.size * (0.55 + 0.45 * p))
        a = int(230 * (1 - p))
        if d > 2 and a > 2:
            g = _scaled_glow(self.color, d, a, inner=0.15, falloff=1.6)
            c = self.size // 2
            self.image.blit(g, (c - d // 2, c - d // 2))

    def update(self, dt: float = 1 / 60) -> None:
        self.elapsed += dt
        if self.elapsed >= self.duration:
            self.kill()
        else:
            self._draw()


def spawn_burst(group: pygame.sprite.Group, pos: tuple[int, int],
                color: tuple[int, ...], count: int = 12,
                speed: tuple[float, float] = (2.0, 7.0)) -> None:
    """Scatter *count* sparks outward from *pos*."""
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        group.add(Particle(pos, angle, random.uniform(*speed), color,
                           size=random.randint(3, 6)))


class ElectricWhip(pygame.sprite.Sprite):
    """Sweeping electric arc weapon with collision detection.

    The sprite surface is screen-sized rather than beam-sized: the beam is far
    longer than the display, and allocating a 1920² surface every frame was the
    single most expensive thing in the game.
    """

    def __init__(self, player_pos: tuple[int, int], screen_width: int,
                 screen_height: int) -> None:
        super().__init__()
        self.center_pos = player_pos
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.length = int(math.hypot(screen_width, screen_height))
        self.angle = 0.0
        self.angular_speed = WHIP_ANGULAR_SPEED
        self.done = False
        self.enemies_hit: set = set()

        self.image = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        self._draw()

    def _draw(self) -> None:
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.center_pos

        # Fading trail of the arc's recent sweep positions.
        for i in range(1, 7):
            trail_angle = math.radians(self.angle - i * 4)
            tx = cx + math.cos(trail_angle) * self.length
            ty = cy - math.sin(trail_angle) * self.length
            alpha = int(70 * (1 - i / 7))
            pygame.draw.line(self.image, (60, 170, 255, alpha), (cx, cy), (tx, ty), 10 - i)

        rad = math.radians(self.angle)
        ex = cx + math.cos(rad) * self.length
        ey = cy - math.sin(rad) * self.length

        pygame.draw.line(self.image, (40, 130, 255, 70), (cx, cy), (ex, ey), 18)
        pygame.draw.line(self.image, (110, 210, 255, 150), (cx, cy), (ex, ey), 9)
        pygame.draw.line(self.image, (240, 252, 255, 255), (cx, cy), (ex, ey), 3)

        # Jagged lightning branches jittering along the beam.
        perp = rad + math.pi / 2
        for _ in range(14):
            d = random.random()
            px = cx + (ex - cx) * d
            py = cy + (ey - cy) * d
            off = random.uniform(-16, 16)
            bx = px + math.cos(perp) * off
            by = py - math.sin(perp) * off
            pygame.draw.line(self.image, (190, 230, 255, random.randint(90, 200)),
                             (px, py), (bx, by), random.randint(1, 3))

        # Bright emitter at the player.
        core = _scaled_glow((180, 235, 255), 90, 220, inner=0.1, additive=True)
        self.image.blit(core, (cx - 45, cy - 45), special_flags=pygame.BLEND_RGBA_ADD)

    def update(self, dt: float = 1 / 60,
               enemy_group: pygame.sprite.Group | None = None,
               all_sprites: pygame.sprite.Group | None = None,
               explosion_sound: pygame.mixer.Sound | None = None,
               score_multiplier: float = 1.0) -> None:
        self.angle += self.angular_speed * dt * 60
        if self.angle >= 180:
            self.kill()
            self.done = True
            return

        self._draw()

        if enemy_group and all_sprites:
            wx, wy = self.center_pos
            for enemy in list(enemy_group):
                if enemy in self.enemies_hit:
                    continue

                ex, ey = enemy.rect.center
                ddx = ex - wx
                ddy = ey - wy
                distance = math.hypot(ddx, ddy)
                angle_to_enemy = math.degrees(math.atan2(-ddy, ddx)) % 360

                angle_diff = abs((self.angle - angle_to_enemy) % 360)
                if angle_diff > 180:
                    angle_diff = 360 - angle_diff

                if distance <= self.length and angle_diff < WHIP_HIT_ANGLE_TOLERANCE:
                    self.enemies_hit.add(enemy)

                    all_sprites.add(Explosion(enemy.rect.center))
                    for _ in range(10):
                        all_sprites.add(ElectricalParticle(
                            enemy.rect.center, random.uniform(0, 2 * math.pi),
                            random.uniform(2, 6)))

                    if explosion_sound:
                        explosion_sound.play(maxtime=0, fade_ms=0)
