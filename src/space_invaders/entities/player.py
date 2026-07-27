"""Player entity."""

from __future__ import annotations

import math

import pygame

from space_invaders.constants import (
    HUD_BOTTOM_H,
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
from space_invaders.entities.effects import ElectricWhip, MuzzleFlash, _scaled_glow
from space_invaders.entities.projectiles import Shot, ShotgunShot

# Extra room around the ship in its sprite surface for banking rotation and
# the engine plume. The tight ship body lives in `hitbox`.
_PAD_X = 26
_FLAME_H = 34
_MAX_BANK = 15.0


class Player(pygame.sprite.Sprite):
    """The player-controlled ship, with banking and a live engine plume."""

    def __init__(self, image: pygame.Surface) -> None:
        super().__init__()
        self.base_image = image
        self._ship = pygame.transform.smoothscale(
            self.base_image, (PLAYER_WIDTH, PLAYER_HEIGHT)).convert_alpha()

        self.image = pygame.Surface(
            (PLAYER_WIDTH + _PAD_X * 2, PLAYER_HEIGHT + _FLAME_H), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.hitbox = pygame.Rect(0, 0, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.bank = 0.0
        self.thrust = 0.0
        self._prev_x = float(SCREEN_WIDTH // 2)

        self.rect.centerx = SCREEN_WIDTH // 2
        # Hull sits clear of the bottom HUD bar, which draws over the sprites.
        self.rect.bottom = SCREEN_HEIGHT - HUD_BOTTOM_H - 14 + _FLAME_H
        self._sync_hitbox()
        self._render()

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

    # ------------------------------------------------------------------
    # Presentation
    # ------------------------------------------------------------------

    def _sync_hitbox(self) -> None:
        self.hitbox.midtop = (self.rect.centerx, self.rect.top)

    @property
    def muzzle(self) -> tuple[int, int]:
        """World position of the gun barrel."""
        return (self.rect.centerx, self.hitbox.top + 4)

    def _render(self) -> None:
        """Redraw the ship sprite: banked hull over a flickering engine plume."""
        self.image.fill((0, 0, 0, 0))
        cx = self.image.get_width() // 2
        body_cy = PLAYER_HEIGHT // 2

        # Engine plume — two stacked glows, length driven by thrust and flicker.
        t = pygame.time.get_ticks() * 0.02
        flicker = 0.75 + 0.25 * math.sin(t) * math.sin(t * 0.37)
        power = (0.55 + 0.45 * self.thrust) * flicker
        plume_h = int(_FLAME_H * power)
        if plume_h > 6:
            for color, wf, hf, alpha in (
                ((60, 150, 255), 1.5, 1.0, 120),
                ((150, 225, 255), 0.9, 0.72, 190),
                ((255, 255, 255), 0.45, 0.42, 235),
            ):
                pw = max(int(PLAYER_WIDTH * 0.42 * wf), 3)
                ph = max(int(plume_h * hf), 3)
                glow = _scaled_glow(color, max(pw, ph), alpha, inner=0.1,
                                    falloff=1.5, additive=True)
                glow = pygame.transform.smoothscale(glow, (pw, ph * 2))
                self.image.blit(glow, (cx - pw // 2, PLAYER_HEIGHT - ph // 2 - 4),
                                special_flags=pygame.BLEND_RGBA_ADD)

        ship = self._ship
        if abs(self.bank) > 0.4:
            ship = pygame.transform.rotozoom(self._ship, -self.bank, 1.0)
        r = ship.get_rect(center=(cx, body_cy))
        self.image.blit(ship, r)

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, dt: float, score: int, skin_images: tuple[pygame.Surface, ...],
               mouse_control: bool = False) -> None:
        # Movement is done on the tight hull rect so the sprite padding and
        # engine plume never affect where the ship can actually go.
        half = self.hitbox.width // 2
        if not mouse_control:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.rect.x -= self.speed * dt * 60
                if self.hitbox.right < 0:
                    self.rect.centerx = SCREEN_WIDTH + half
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.rect.x += self.speed * dt * 60
                if self.hitbox.left > SCREEN_WIDTH:
                    self.rect.centerx = -half
        else:
            mouse_x, _ = pygame.mouse.get_pos()
            self.target_x = max(half, min(mouse_x, SCREEN_WIDTH - half))

            dx = self.target_x - self.rect.centerx
            if abs(dx) > 2:
                move = max(1.0, min(self.speed * 2, abs(dx) * self.mouse_speed_factor))
                self.rect.x += move if dx > 0 else -move

            self.rect.centerx = max(half, min(self.rect.centerx, SCREEN_WIDTH - half))

        self._sync_hitbox()

        # Banking and thrust follow actual velocity, smoothed so they ease in
        # and out instead of snapping.
        vx = self.rect.centerx - self._prev_x
        self._prev_x = float(self.rect.centerx)
        target_bank = max(-_MAX_BANK, min(_MAX_BANK, vx * 1.6))
        blend = min(1.0, dt * 12)
        self.bank += (target_bank - self.bank) * blend
        self.thrust += (min(1.0, abs(vx) / max(self.speed, 1)) - self.thrust) * blend

        if score != self._last_score_check:
            self._last_score_check = score
            self._update_skin(score, skin_images)

        self._render()

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
        self._ship = pygame.transform.smoothscale(
            self.base_image, (PLAYER_WIDTH, PLAYER_HEIGHT)).convert_alpha()

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
                whip = ElectricWhip(self.muzzle, SCREEN_WIDTH, SCREEN_HEIGHT)
                all_sprites.add(whip)
                shoot_sound.play(maxtime=0, fade_ms=0)
                self.whip_charge = 0
            return

        now = pygame.time.get_ticks()
        if now - self.last_shot_time > self.shot_cooldown:
            self.last_shot_time = now
            from space_invaders.constants import DIFFICULTY_CONFIG
            diff_cfg = DIFFICULTY_CONFIG[difficulty]
            mx, my = self.muzzle
            if current_weapon == "shotgun":
                for angle in SHOTGUN_PELLET_ANGLES:
                    shot = ShotgunShot(mx, my, angle)
                    shot.speed = diff_cfg["shotgun_speed"]
                    all_sprites.add(shot)
                    shot_group.add(shot)
                    if angle == 0:
                        active_shots.append(shot)
                all_sprites.add(MuzzleFlash((mx, my), (255, 200, 110), 66))
            else:
                shot = Shot(mx, my)
                shot.speed = diff_cfg["shot_speed"]
                all_sprites.add(shot)
                shot_group.add(shot)
                active_shots.append(shot)
                all_sprites.add(MuzzleFlash((mx, my)))
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
