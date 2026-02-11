"""Visual effect entities (explosions, particles, electric whip)."""

from __future__ import annotations

import math
import random

import pygame

from space_invaders.constants import (
    BLACK,
    BLUE,
    EXPLOSION_FRAME_RATE_MS,
    EXPLOSION_FRAMES,
    EXPLOSION_SHRINK_PER_FRAME,
    EXPLOSION_SIZE,
    ORANGE,
    PARTICLE_LIFETIME,
    PARTICLE_SIZE,
    ELECTRICAL_PARTICLE_LIFETIME,
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
    """Orange circle explosion animation."""

    def __init__(self, center: tuple[int, int]) -> None:
        super().__init__()
        self.image = pygame.Surface((EXPLOSION_SIZE, EXPLOSION_SIZE))
        half = EXPLOSION_SIZE // 2
        pygame.draw.circle(self.image, ORANGE, (half, half), half)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect(center=center)
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = EXPLOSION_FRAME_RATE_MS

    def update(self, dt: float = 1 / 60) -> None:
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == EXPLOSION_FRAMES:
                self.kill()
            else:
                center = self.rect.center
                size = EXPLOSION_SIZE - self.frame * EXPLOSION_SHRINK_PER_FRAME
                if size < 2:
                    self.kill()
                    return
                self.image = pygame.Surface((size, size))
                half = size // 2
                pygame.draw.circle(self.image, ORANGE, (half, half), half)
                self.image.set_colorkey(BLACK)
                self.rect = self.image.get_rect(center=center)


class Particle(pygame.sprite.Sprite):
    """Generic particle for visual effects."""

    def __init__(self, pos: tuple[int, int], angle: float, speed: float) -> None:
        super().__init__()
        self.image = pygame.Surface((PARTICLE_SIZE, PARTICLE_SIZE))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(center=pos)
        self.x = float(pos[0])
        self.y = float(pos[1])
        self.velocity_x = math.cos(angle) * speed
        self.velocity_y = math.sin(angle) * speed
        self.lifetime = PARTICLE_LIFETIME

    def update(self, dt: float = 1 / 60) -> None:
        self.x += self.velocity_x * dt * 60
        self.y += self.velocity_y * dt * 60
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()


class ElectricalParticle(Particle):
    """Electric-blue particle with flickering effect."""

    def __init__(self, pos: tuple[int, int], angle: float, speed: float) -> None:
        super().__init__(pos, angle, speed)
        self.image.fill((100, 200, 255))
        self.lifetime = ELECTRICAL_PARTICLE_LIFETIME

    def update(self, dt: float = 1 / 60) -> None:
        super().update(dt)
        if random.random() < 0.5:
            self.image.fill((200, 230, 255))
        else:
            self.image.fill((80, 150, 255))


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
                dx = ex - wx
                dy = ey - wy
                distance = math.sqrt(dx * dx + dy * dy)
                angle_to_enemy = math.degrees(math.atan2(-dy, dx))

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
