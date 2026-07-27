"""Main Game class — owns the game loop and all subsystems."""

from __future__ import annotations

import random
import sys
from pathlib import Path

import pygame

from space_invaders.config import load_config, load_high_scores, save_config
from space_invaders.constants import (
    BONUS_SPAWN_DELAY_MS,
    DIFFICULTY_CONFIG,
    FPS,
    HITSTOP_DEATH,
    HITSTOP_KILL,
    HITSTOP_MAX,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    Colors,
)
from space_invaders.entities.background import create_stars
from space_invaders.entities.effects import (
    ElectricWhip,
    Explosion,
    ScorePopup,
    spawn_burst,
)
from space_invaders.entities.enemies import Enemy, StrongEnemy
from space_invaders.entities.pickups import PowerBonus
from space_invaders.entities.player import Player
from space_invaders.entities.projectiles import hitbox_collide
from space_invaders.state import GameScreen, GameState
from space_invaders.systems.assets import AssetManager
from space_invaders.systems.input_handler import InputHandler
from space_invaders.systems.levels import check_level_complete, spawn_enemies
from space_invaders.systems.postfx import PostFX, set_display_mode
from space_invaders.systems.renderer import Renderer
from space_invaders.systems.scoring import check_and_update_highscore


class Game:
    """Top-level game object that owns the loop, state, and all subsystems."""

    def __init__(self) -> None:
        pygame.init()
        pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=1024)

        self.state = GameState()
        self.game_config = load_config()
        self.high_scores = load_high_scores()

        # Apply persisted settings
        self.state.sound_volume = self.game_config.get("sound_volume", 0.5)
        self.state.music_volume = self.game_config.get("music_volume", 0.07)
        self.state.fullscreen = self.game_config.get("fullscreen_enabled", False)
        self.state.mouse_control = self.game_config.get("mouse_control", False)

        # Display. Everything is drawn to the PostFX world surface; `display`
        # is only ever touched by PostFX.present().
        self.display = set_display_mode(self.state.fullscreen)
        pygame.display.set_caption("Space Invaders")
        self.fx = PostFX((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen = self.fx.world
        self.hitstop = 0.0

        # Assets
        assets_dir = Path(__file__).resolve().parent.parent.parent / "assets"
        self.assets = AssetManager(assets_dir)
        self.assets.load_all()
        self.assets.apply_volumes(self.state.sound_volume, self.state.music_volume)

        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()
        self.shot_group = pygame.sprite.Group()
        self.bonus_group = pygame.sprite.Group()
        self.enemy_projectile_group = pygame.sprite.Group()
        self.star_group = pygame.sprite.Group()

        create_stars(self.star_group)

        # Player
        self.player = Player(self.assets.images["player"])
        self.all_sprites.add(self.player)

        # Active shots list (for multiplier tracking)
        self.active_shots: list = []

        # Clock
        self.clock = pygame.time.Clock()

        # Bonus timer
        self.state.bonus_timer = pygame.time.get_ticks()

        # Systems
        self.input_handler = InputHandler(self)
        self.renderer = Renderer(self)

        # Start music
        try:
            self.assets.sounds["theme"].play(loops=-1)
        except Exception as e:
            print(f"Could not play background music: {e}")

    # ------------------------------------------------------------------
    # Round management
    # ------------------------------------------------------------------

    def start_round(self) -> None:
        """Reset player and spawn enemies for a new round."""
        spawn_enemies(
            self.state.level_mode,
            self.state.level,
            self.state.difficulty,
            self.assets.images["enemy"],
            self.assets.images["strong_enemy"],
            self.all_sprites,
            self.enemy_group,
        )
        self.player.lives = 3
        self.state.reset_for_new_game()

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def impact(self, trauma: float, hitstop: float = 0.0,
               flash: tuple[int, int, int] | None = None) -> None:
        """Punctuate a hit: shake the camera, freeze briefly, flash the screen."""
        self.fx.shake(trauma)
        if hitstop:
            self.hitstop = min(HITSTOP_MAX, self.hitstop + hitstop)
        if flash:
            self.fx.flash(0.1, flash)

    def run(self) -> None:
        """Execute the game loop until exit."""
        while self.state.running:
            # Clamp dt so a stall (window drag, first-frame asset work) can't
            # teleport sprites through each other.
            dt = min(self.clock.tick(FPS) / 1000.0, 0.05)
            self.input_handler.process_events()
            self.fx.update(dt)

            if self.hitstop > 0:
                self.hitstop = max(0.0, self.hitstop - dt)
                dt = 0.0

            self._update(dt)
            self.renderer.draw()

        pygame.mixer.stop()
        pygame.quit()
        sys.exit()

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def _update(self, dt: float) -> None:
        self.star_group.update(dt)

        if self.state.screen != GameScreen.PLAYING:
            return

        # Player
        self.player.update(
            dt, self.state.score, self.assets.skin_images, self.state.mouse_control)

        # Enemies
        for enemy in self.enemy_group:
            if self.state.difficulty == 4:
                enemy.update(dt, self.state.difficulty, self.all_sprites, self.enemy_projectile_group)
            else:
                enemy.update(dt)

        # Shots
        for shot in self.shot_group:
            shot.update(dt, self.state.reset_multiplier)

        # Other sprites (whip, explosions, particles, notifications)
        for sprite in list(self.all_sprites):
            if sprite in self.shot_group or sprite in self.enemy_group or sprite is self.player:
                continue
            if isinstance(sprite, ElectricWhip):
                sprite.update(dt, self.enemy_group, self.all_sprites,
                              self.assets.sounds["explosion"], self.state.score_multiplier)
                self._process_whip_hits(sprite)
            else:
                sprite.update(dt)

        # Collisions
        self._handle_shot_enemy_collisions()
        self._handle_enemy_projectile_collisions()
        self._handle_enemy_bottom()
        self._handle_bonus_spawn()
        self._handle_bonus_pickup()
        self._handle_level_completion()

    # ------------------------------------------------------------------
    # Collision helpers
    # ------------------------------------------------------------------

    def _destroy_enemy(self, enemy, *, keep_kind: bool = False,
                       charge_whip: bool = False) -> None:
        """Score, juice and replace a destroyed enemy.

        Single path for every kill so the whip and the guns feel identical.
        """
        self.state.increase_multiplier()
        point_gain = int(enemy.point_value * self.state.score_multiplier)
        self.state.score += point_gain
        if charge_whip:
            self.player.whip_charge = min(
                self.player.whip_charge + point_gain, self.player.whip_charge_threshold)

        strong = isinstance(enemy, StrongEnemy)
        center = enemy.rect.center

        self.all_sprites.add(Explosion(center, scale=1.35 if strong else 1.0))
        spawn_burst(self.all_sprites, center,
                    Colors.EXPLOSION_MID, count=16 if strong else 10)
        self.all_sprites.add(ScorePopup(
            center, f"+{point_gain}", self.assets.fonts["small"],
            Colors.SECONDARY if strong else Colors.TEXT_PRIMARY))
        self.assets.sounds["explosion"].play(maxtime=0, fade_ms=0)
        self.impact(0.30 if strong else 0.16, HITSTOP_KILL)

        enemy.kill()

        if keep_kind and strong:
            replacement = StrongEnemy(self.assets.images["strong_enemy"], self.state.difficulty)
        else:
            replacement = Enemy(self.assets.images["enemy"], self.state.difficulty)
        self.all_sprites.add(replacement)
        self.enemy_group.add(replacement)

    def _lose_life(self) -> None:
        """Take a hit: juice it, then end the run if that was the last life."""
        self.player.lives -= 1
        self.all_sprites.add(Explosion(self.player.hitbox.center, scale=1.2))
        spawn_burst(self.all_sprites, self.player.hitbox.center, Colors.DANGER, count=20)
        self.impact(0.85, HITSTOP_DEATH, flash=Colors.DANGER)

        if self.player.lives <= 0:
            self.state.screen = GameScreen.GAME_OVER
            check_and_update_highscore(
                self.state.score, self.state.difficulty, self.high_scores,
                self.state.level, self.state.level_mode)

    def _process_whip_hits(self, whip: ElectricWhip) -> None:
        for enemy in list(whip.enemies_hit):
            if enemy not in self.enemy_group:
                continue
            self._destroy_enemy(enemy, keep_kind=True)

    def _handle_shot_enemy_collisions(self) -> None:
        hits = pygame.sprite.groupcollide(
            self.shot_group, self.enemy_group, True, False, hitbox_collide)
        processed = set()
        for shot, enemies in hits.items():
            shot.hit_enemy = True
            for enemy in enemies:
                if enemy in processed:
                    continue
                processed.add(enemy)
                enemy.hit()
                if enemy.hits >= enemy.max_hits:
                    self._destroy_enemy(enemy, charge_whip=True)
                else:
                    # Survived: small shower of sparks so chip damage still reads.
                    spawn_burst(self.all_sprites, shot.rect.midtop,
                                Colors.SECONDARY, count=5, speed=(1.5, 4.0))
                    self.impact(0.05)

    def _handle_enemy_projectile_collisions(self) -> None:
        if self.state.difficulty != 4:
            return
        hits = pygame.sprite.spritecollide(
            self.player, self.enemy_projectile_group, True, hitbox_collide)
        for _ in hits:
            self._lose_life()
            if self.player.lives <= 0:
                return

    def _handle_enemy_bottom(self) -> None:
        diff_cfg = DIFFICULTY_CONFIG[self.state.difficulty]
        for enemy in self.enemy_group:
            if enemy.rect.top > SCREEN_HEIGHT:
                half = enemy.rect.width // 2
                enemy.place(random.randrange(half, SCREEN_WIDTH - half),
                            random.randrange(-100, -40))
                lo, hi = diff_cfg["enemy_speed_range"]
                enemy.speed = random.randrange(lo, hi + 1)
                self._lose_life()
                if self.player.lives <= 0:
                    return

    def _handle_bonus_spawn(self) -> None:
        now = pygame.time.get_ticks()
        if now - self.state.bonus_timer > BONUS_SPAWN_DELAY_MS:
            self.state.bonus_timer = now
            bonus = PowerBonus(self.assets.images["life"])
            self.all_sprites.add(bonus)
            self.bonus_group.add(bonus)

    def _handle_bonus_pickup(self) -> None:
        hits = pygame.sprite.spritecollide(
            self.player, self.bonus_group, True, hitbox_collide)
        for hit in hits:
            self.assets.sounds["life"].play(maxtime=0, fade_ms=0)
            self.player.lives += 1
            spawn_burst(self.all_sprites, hit.rect.center, Colors.SUCCESS, count=18)
            self.all_sprites.add(ScorePopup(
                hit.rect.center, "+1 LIV", self.assets.fonts["small"], Colors.SUCCESS))
            self.impact(0.12, flash=(30, 90, 55))

    def _handle_level_completion(self) -> None:
        completed, new_level, shotgun_unlocked = check_level_complete(
            self.state.level, self.state.score, self.state.level_mode,
            self.state.difficulty, self.high_scores, self.game_config)
        if completed:
            self.state.level = new_level
            self.state.screen = GameScreen.LEVEL_COMPLETE
            self.impact(0.35, flash=(40, 80, 70))
            if shotgun_unlocked:
                self.state.show_shotgun_unlock = True
