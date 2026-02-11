"""Main Game class — owns the game loop and all subsystems."""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import pygame

from space_invaders.config import load_config, load_high_scores, save_config
from space_invaders.constants import (
    BONUS_SPAWN_DELAY_MS,
    DIFFICULTY_CONFIG,
    FPS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from space_invaders.entities.background import create_stars
from space_invaders.entities.effects import ElectricWhip, Explosion, Particle
from space_invaders.entities.enemies import Enemy, StrongEnemy
from space_invaders.entities.pickups import PowerBonus
from space_invaders.entities.player import Player
from space_invaders.state import GameScreen, GameState
from space_invaders.systems.assets import AssetManager
from space_invaders.systems.input_handler import InputHandler
from space_invaders.systems.levels import check_level_complete, spawn_enemies
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

        # Screen
        flags = pygame.FULLSCREEN if self.state.fullscreen else 0
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
        pygame.display.set_caption("Space Invaders")

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

    def run(self) -> None:
        """Execute the game loop until exit."""
        while self.state.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.input_handler.process_events()
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

    def _process_whip_hits(self, whip: ElectricWhip) -> None:
        for enemy in list(whip.enemies_hit):
            if enemy not in self.enemy_group:
                continue
            self.state.increase_multiplier()
            point_gain = int(enemy.point_value * self.state.score_multiplier)
            self.state.score += point_gain

            exp = Explosion(enemy.rect.center)
            self.all_sprites.add(exp)

            is_strong = isinstance(enemy, StrongEnemy)
            enemy.kill()

            if is_strong:
                ne = StrongEnemy(self.assets.images["strong_enemy"], self.state.difficulty)
            else:
                ne = Enemy(self.assets.images["enemy"], self.state.difficulty)
            self.all_sprites.add(ne)
            self.enemy_group.add(ne)

    def _handle_shot_enemy_collisions(self) -> None:
        hits = pygame.sprite.groupcollide(self.shot_group, self.enemy_group, True, False)
        processed = set()
        for shot, enemies in hits.items():
            shot.hit_enemy = True
            for enemy in enemies:
                if enemy in processed:
                    continue
                processed.add(enemy)
                enemy.hits += 1
                if enemy.hits >= enemy.max_hits:
                    self.state.increase_multiplier()
                    point_gain = int(enemy.point_value * self.state.score_multiplier)
                    self.state.score += point_gain
                    self.player.whip_charge = min(
                        self.player.whip_charge + point_gain, self.player.whip_charge_threshold)

                    exp = Explosion(enemy.rect.center)
                    self.all_sprites.add(exp)
                    self.assets.sounds["explosion"].play(maxtime=0, fade_ms=0)
                    enemy.kill()

                    # Always spawn a normal enemy as replacement
                    ne = Enemy(self.assets.images["enemy"], self.state.difficulty)
                    self.all_sprites.add(ne)
                    self.enemy_group.add(ne)

    def _handle_enemy_projectile_collisions(self) -> None:
        if self.state.difficulty != 4:
            return
        hits = pygame.sprite.spritecollide(self.player, self.enemy_projectile_group, True)
        for _ in hits:
            self.player.lives -= 1
            if self.player.lives <= 0:
                self.state.screen = GameScreen.GAME_OVER
                check_and_update_highscore(
                    self.state.score, self.state.difficulty, self.high_scores,
                    self.state.level, self.state.level_mode)

    def _handle_enemy_bottom(self) -> None:
        diff_cfg = DIFFICULTY_CONFIG[self.state.difficulty]
        for enemy in self.enemy_group:
            if enemy.rect.top > SCREEN_HEIGHT:
                enemy.rect.x = random.randrange(SCREEN_WIDTH - enemy.rect.width)
                enemy.rect.y = random.randrange(-100, -40)
                lo, hi = diff_cfg["enemy_speed_range"]
                enemy.speed = random.randrange(lo, hi + 1)
                self.player.lives -= 1
                if self.player.lives <= 0:
                    self.state.screen = GameScreen.GAME_OVER
                    check_and_update_highscore(
                        self.state.score, self.state.difficulty, self.high_scores,
                        self.state.level, self.state.level_mode)

    def _handle_bonus_spawn(self) -> None:
        now = pygame.time.get_ticks()
        if now - self.state.bonus_timer > BONUS_SPAWN_DELAY_MS:
            self.state.bonus_timer = now
            bonus = PowerBonus(self.assets.images["life"])
            self.all_sprites.add(bonus)
            self.bonus_group.add(bonus)

    def _handle_bonus_pickup(self) -> None:
        hits = pygame.sprite.spritecollide(self.player, self.bonus_group, True)
        for hit in hits:
            self.assets.sounds["life"].play(maxtime=0, fade_ms=0)
            self.player.lives += 1
            for _ in range(10):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(1, 3)
                p = Particle(hit.rect.center, angle, speed)
                self.all_sprites.add(p)

    def _handle_level_completion(self) -> None:
        completed, new_level, shotgun_unlocked = check_level_complete(
            self.state.level, self.state.score, self.state.level_mode,
            self.state.difficulty, self.high_scores, self.game_config)
        if completed:
            self.state.level = new_level
            self.state.screen = GameScreen.LEVEL_COMPLETE
            if shotgun_unlocked:
                self.state.show_shotgun_unlock = True
