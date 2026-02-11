"""Player entity."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from space_invaders.constants import (
    PLAYER_HEIGHT,
    PLAYER_SPEED,
    PLAYER_WIDTH,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SHOT_COOLDOWN_MS,
    SHOTGUN_PELLET_ANGLES,
    SHOTGUN_UNLOCK_LEVEL,
    SKIN_THRESHOLD_2,
    SKIN_THRESHOLD_3,
    SKIN_THRESHOLD_4,
    WHIP_CHARGE_THRESHOLD,
    WHIP_UNLOCK_LEVEL,
    MOUSE_SPEED_FACTOR,
)
from space_invaders.entities.effects import ElectricWhip
from space_invaders.entities.projectiles import Shot, ShotgunShot

if TYPE_CHECKING:
    from space_invaders.state import GameState


class Player(pygame.sprite.Sprite):
    """The player-controlled ship."""

    def __init__(self, image: pygame.Surface) -> None:
        super().__init__()
        self.base_image = image
        self.image = pygame.transform.scale(self.base_image, (PLAYER_WIDTH, PLAYER_HEIGHT))
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed = PLAYER_SPEED
        self.lives = 3

        # Shot cooldown
        self.last_shot_time = 0
        self.shot_cooldown = SHOT_COOLDOWN_MS

        # Skin progression
        self._last_score_check = 0

        # Weapons
        self.current_weapon = "normal"
        self.whip_charge = 0
        self.whip_charge_threshold = WHIP_CHARGE_THRESHOLD

        # Mouse tracking
        self.target_x = self.rect.centerx
        self.mouse_speed_factor = MOUSE_SPEED_FACTOR

    def update(self, dt: float, score: int, skin_images: tuple[pygame.Surface, ...],
               mouse_control: bool = False) -> None:
        if not mouse_control:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.rect.x -= self.speed * dt * 60
                if self.rect.right < 0:
                    self.rect.left = SCREEN_WIDTH
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.rect.x += self.speed * dt * 60
                if self.rect.left > SCREEN_WIDTH:
                    self.rect.right = 0
        else:
            mouse_x, _ = pygame.mouse.get_pos()
            half_width = self.rect.width // 2
            self.target_x = max(half_width, min(mouse_x, SCREEN_WIDTH - half_width))

            dx = self.target_x - self.rect.centerx
            if abs(dx) > 2:
                max_move = self.speed * 2
                move_amount = min(max_move, abs(dx) * self.mouse_speed_factor)
                if move_amount < 1:
                    move_amount = 1
                if dx > 0:
                    self.rect.x += move_amount
                else:
                    self.rect.x -= move_amount

            if self.rect.left < 0:
                self.rect.left = 0
            elif self.rect.right > SCREEN_WIDTH:
                self.rect.right = SCREEN_WIDTH

        if score != self._last_score_check:
            self._last_score_check = score
            self._update_skin(score, skin_images)

    def _update_skin(self, score: int, skin_images: tuple[pygame.Surface, ...]) -> None:
        base, img2, img3, img4 = skin_images
        if score >= SKIN_THRESHOLD_4:
            self.base_image = img4
        elif score >= SKIN_THRESHOLD_3:
            self.base_image = img3
        elif score >= SKIN_THRESHOLD_2:
            self.base_image = img2
        else:
            self.base_image = base
        self.image = pygame.transform.scale(self.base_image, (PLAYER_WIDTH, PLAYER_HEIGHT))

    def shoot(
        self,
        all_sprites: pygame.sprite.Group,
        shot_group: pygame.sprite.Group,
        active_shots: list,
        shoot_sound: pygame.mixer.Sound,
        difficulty: int,
        enemy_group: pygame.sprite.Group | None = None,
        weapon_override: str | None = None,
    ) -> None:
        current_weapon = weapon_override if weapon_override is not None else self.current_weapon

        if current_weapon == "electric whip":
            if self.whip_charge >= self.whip_charge_threshold and enemy_group:
                whip = ElectricWhip(self.rect.midtop, SCREEN_WIDTH, SCREEN_HEIGHT)
                all_sprites.add(whip)
                shoot_sound.play(maxtime=0, fade_ms=0)
                self.whip_charge = 0
            return

        now = pygame.time.get_ticks()
        if now - self.last_shot_time > self.shot_cooldown:
            self.last_shot_time = now
            from space_invaders.constants import DIFFICULTY_CONFIG
            diff_cfg = DIFFICULTY_CONFIG[difficulty]
            if current_weapon == "shotgun":
                for angle in SHOTGUN_PELLET_ANGLES:
                    shot = ShotgunShot(self.rect.centerx, self.rect.top, angle)
                    shot.speed = diff_cfg["shotgun_speed"]
                    all_sprites.add(shot)
                    shot_group.add(shot)
                    if angle == 0:
                        active_shots.append(shot)
            else:
                shot = Shot(self.rect.centerx, self.rect.top)
                shot.speed = diff_cfg["shot_speed"]
                all_sprites.add(shot)
                shot_group.add(shot)
                active_shots.append(shot)
            shoot_sound.play(maxtime=0, fade_ms=0)

    def switch_weapon(self, weapon_name: str, max_level_reached: int) -> bool:
        """Switch weapon if available based on progression."""
        if weapon_name == "normal":
            self.current_weapon = weapon_name
            return True
        elif weapon_name == "shotgun" and max_level_reached > SHOTGUN_UNLOCK_LEVEL:
            self.current_weapon = weapon_name
            return True
        elif weapon_name == "electric whip" and max_level_reached >= WHIP_UNLOCK_LEVEL:
            self.current_weapon = weapon_name
            return True
        return False
