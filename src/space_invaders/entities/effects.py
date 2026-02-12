"""Visual effect entities (explosions, particles, electric whip)."""

from __future__ import annotations

import math
import random

import pygame

from space_invaders.constants import (
    Colors,
    ELECTRICAL_PARTICLE_LIFETIME,
    EXPLOSION_FRAME_RATE_MS,
    EXPLOSION_FRAMES,
    EXPLOSION_SIZE,
    PARTICLE_LIFETIME,
    PARTICLE_SIZE,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    WHIP_ANGULAR_SPEED,
    WHIP_GLOW_THICKNESS,
    WHIP_HIT_ANGLE_TOLERANCE,
    WHIP_LINE_THICKNESS,
    WHIP_OUTER_GLOW_THICKNESS,
    WHIP_PARTICLE_COUNT,
)


class Explosion(pygame.sprite.Sprite):
    """Multi-ring explosion with core flash and expanding shockwave ring."""

    def __init__(self, center: tuple[int, int]) -> None:
        super().__init__()
        self.size = EXPLOSION_SIZE
        self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=center)
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = EXPLOSION_FRAME_RATE_MS
        self.max_frames = EXPLOSION_FRAMES + 3  # extra frames for ring
        self._draw_frame()

    def _draw_frame(self) -> None:
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.image.get_width() // 2, self.image.get_height() // 2
        progress = self.frame / self.max_frames

        # Expanding shockwave ring
        ring_radius = int(self.size * 0.4 + self.size * 0.8 * progress)
        ring_alpha = int(120 * (1 - progress))
        ring_width = max(1, int(3 * (1 - progress)))
        if ring_alpha > 0:
            pygame.draw.circle(
                self.image, (*Colors.EXPLOSION_RING[:3], ring_alpha),
                (cx, cy), ring_radius, ring_width,
            )

        # Core glow (bright to dim)
        if progress < 0.7:
            core_progress = progress / 0.7
            core_r = int(self.size * 0.35 * (1 - core_progress * 0.6))
            core_alpha = int(200 * (1 - core_progress))
            if core_r > 1 and core_alpha > 0:
                # Outer glow
                pygame.draw.circle(
                    self.image, (*Colors.EXPLOSION_OUTER[:3], core_alpha // 3),
                    (cx, cy), core_r + 6,
                )
                # Mid layer
                pygame.draw.circle(
                    self.image, (*Colors.EXPLOSION_MID[:3], core_alpha // 2),
                    (cx, cy), core_r + 2,
                )
                # Hot core
                pygame.draw.circle(
                    self.image, (*Colors.EXPLOSION_CORE[:3], core_alpha),
                    (cx, cy), core_r,
                )

    def update(self, dt: float = 1 / 60) -> None:
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame >= self.max_frames:
                self.kill()
            else:
                self._draw_frame()


class Particle(pygame.sprite.Sprite):
    """Generic particle with color fade-out."""

    def __init__(
        self,
        pos: tuple[int, int],
        angle: float,
        speed: float,
        color: tuple[int, ...] | None = None,
    ) -> None:
        super().__init__()
        self._color = color or Colors.PRIMARY
        self.image = pygame.Surface((PARTICLE_SIZE, PARTICLE_SIZE), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=pos)
        self.x = float(pos[0])
        self.y = float(pos[1])
        self.velocity_x = math.cos(angle) * speed
        self.velocity_y = math.sin(angle) * speed
        self.lifetime = PARTICLE_LIFETIME
        self.max_lifetime = PARTICLE_LIFETIME
        self._redraw()

    def _redraw(self) -> None:
        fade = max(self.lifetime / self.max_lifetime, 0)
        alpha = int(255 * fade)
        self.image.fill((0, 0, 0, 0))
        c = self._color
        # Draw a soft circle instead of a solid square
        center = PARTICLE_SIZE // 2
        pygame.draw.circle(self.image, (*c[:3], alpha), (center, center), center)

    def update(self, dt: float = 1 / 60) -> None:
        self.x += self.velocity_x * dt * 60
        self.y += self.velocity_y * dt * 60
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
        else:
            self._redraw()


class ElectricalParticle(Particle):
    """Electric-blue particle with flickering effect."""

    def __init__(self, pos: tuple[int, int], angle: float, speed: float) -> None:
        super().__init__(pos, angle, speed, color=(100, 200, 255))
        self.lifetime = ELECTRICAL_PARTICLE_LIFETIME
        self.max_lifetime = ELECTRICAL_PARTICLE_LIFETIME

    def update(self, dt: float = 1 / 60) -> None:
        super().update(dt)
        if self.lifetime > 0:
            if random.random() < 0.5:
                self._color = (200, 230, 255)
            else:
                self._color = (80, 150, 255)
            self._redraw()


class ElectricWhip(pygame.sprite.Sprite):
    """Sweeping electric whip weapon animation with collision detection."""

    def __init__(self, player_pos: tuple[int, int], screen_width: int, screen_height: int) -> None:
        super().__init__()
        self.center_pos = player_pos
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.length = int(screen_width * 1.5)
        self.angle = 0.0
        self.angular_speed = WHIP_ANGULAR_SPEED
        self.done = False
        self.enemies_hit: set = set()

        self.image = pygame.Surface((self.length, self.length), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=player_pos)
        self._draw()

    def _draw(self) -> None:
        self.image.fill((0, 0, 0, 0))
        angle_rad = math.radians(self.angle)
        cx = self.length // 2
        cy = self.length // 2
        dx = math.cos(angle_rad) * self.length // 2
        dy = -math.sin(angle_rad) * self.length // 2

        end = (cx + dx, cy + dy)
        start = (cx, cy)

        pygame.draw.line(self.image, (0, 200, 255, 255), start, end, WHIP_LINE_THICKNESS)
        pygame.draw.line(self.image, (100, 220, 255, 180), start, end, WHIP_GLOW_THICKNESS)
        pygame.draw.line(self.image, (180, 230, 255, 100), start, end, WHIP_OUTER_GLOW_THICKNESS)

        for _ in range(WHIP_PARTICLE_COUNT):
            dist = random.random()
            px = cx + dx * dist
            py = cy + dy * dist

            perp = angle_rad + math.pi / 2
            offset = random.uniform(-10, 10)
            px += math.cos(perp) * offset
            py -= math.sin(perp) * offset

            size = random.randint(2, 6)
            alpha = random.randint(150, 255)
            pygame.draw.circle(self.image, (150, 220, 255, alpha), (int(px), int(py)), size)

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
            for enemy in list(enemy_group):
                if enemy in self.enemies_hit:
                    continue

                ex, ey = enemy.rect.center
                wx, wy = self.rect.center
                ddx = ex - wx
                ddy = ey - wy
                distance = math.sqrt(ddx * ddx + ddy * ddy)
                angle_to_enemy = math.degrees(math.atan2(-ddy, ddx))

                while angle_to_enemy < 0:
                    angle_to_enemy += 360
                while angle_to_enemy >= 360:
                    angle_to_enemy -= 360

                angle_diff = abs((self.angle - angle_to_enemy) % 360)
                if angle_diff > 180:
                    angle_diff = 360 - angle_diff

                if distance <= self.length and angle_diff < WHIP_HIT_ANGLE_TOLERANCE:
                    self.enemies_hit.add(enemy)

                    explosion = Explosion(enemy.rect.center)
                    all_sprites.add(explosion)

                    for _ in range(10):
                        a = random.uniform(0, 2 * math.pi)
                        s = random.uniform(2, 5)
                        p = ElectricalParticle(enemy.rect.center, a, s)
                        all_sprites.add(p)

                    if explosion_sound:
                        explosion_sound.play(maxtime=0, fade_ms=0)
