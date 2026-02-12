"""Input handling dispatched by game screen."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from space_invaders.config import save_config
from space_invaders.entities.effects import ElectricWhip
from space_invaders.constants import SCREEN_HEIGHT, SCREEN_WIDTH, WHIP_UNLOCK_LEVEL
from space_invaders.state import GameScreen
from space_invaders.systems.scoring import check_and_update_highscore

if TYPE_CHECKING:
    from space_invaders.game import Game


class InputHandler:
    """Processes events and dispatches to state-specific handlers."""

    def __init__(self, game: Game) -> None:
        self.game = game

    def process_events(self) -> None:
        g = self.game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                g.state.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mousedown(event)

            elif event.type == pygame.KEYDOWN:
                # Global: toggle fullscreen
                if event.key == pygame.K_f:
                    g.state.fullscreen = not g.state.fullscreen
                    if g.state.fullscreen:
                        g.screen = pygame.display.set_mode(
                            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
                    else:
                        g.screen = pygame.display.set_mode(
                            (SCREEN_WIDTH, SCREEN_HEIGHT))
                    g.game_config["fullscreen_enabled"] = g.state.fullscreen
                    save_config(g.game_config)
                    continue

                # Dispatch to current-screen handler
                handler = {
                    GameScreen.MENU: self._handle_menu,
                    GameScreen.LEVEL_SELECT: self._handle_level_select,
                    GameScreen.PLAYING: self._handle_playing,
                    GameScreen.QUIT_CONFIRM: self._handle_quit_confirm,
                    GameScreen.GAME_OVER: self._handle_game_over,
                    GameScreen.LEVEL_COMPLETE: self._handle_level_complete,
                    GameScreen.HELP: self._handle_help,
                    GameScreen.SETTINGS: self._handle_settings,
                }.get(g.state.screen)
                if handler:
                    handler(event)

    # ------------------------------------------------------------------
    # Mouse
    # ------------------------------------------------------------------

    def _handle_mousedown(self, event: pygame.event.Event) -> None:
        g = self.game

        # Menu button clicks
        if g.state.screen == GameScreen.MENU and event.button == 1:
            self._handle_menu_click(event.pos)
            return

        if not g.state.mouse_control or g.state.screen != GameScreen.PLAYING:
            return
        if event.button == 1:
            g.player.shoot(g.all_sprites, g.shot_group, g.active_shots,
                           g.assets.sounds["shoot"], g.state.difficulty, g.enemy_group, "normal")
        elif event.button == 3:
            if g.game_config["max_level_reached"] > 5:
                g.player.shoot(g.all_sprites, g.shot_group, g.active_shots,
                               g.assets.sounds["shoot"], g.state.difficulty, g.enemy_group, "shotgun")
        elif event.button == 2:
            if (g.game_config["max_level_reached"] >= WHIP_UNLOCK_LEVEL
                    and g.player.whip_charge >= g.player.whip_charge_threshold):
                g.player.shoot(g.all_sprites, g.shot_group, g.active_shots,
                               g.assets.sounds["shoot"], g.state.difficulty,
                               g.enemy_group, "electric whip")

    def _handle_menu_click(self, pos: tuple[int, int]) -> None:
        g = self.game
        btns = g.state.menu_buttons
        if not btns:
            return

        difficulty_map = {"easy": 1, "medium": 2, "hard": 3, "impossible": 4}
        for key, diff in difficulty_map.items():
            if key in btns and btns[key].collidepoint(pos):
                if key == "impossible" and not g.game_config["unlock_impossible"]:
                    return
                g.state.difficulty = diff
                g.state.level_mode = False
                g.state.screen = GameScreen.PLAYING
                g.state.show_menu = False
                g.start_round()
                return

        if "level_mode" in btns and btns["level_mode"].collidepoint(pos):
            g.state.level_mode = True
            g.state.current_level_page = 0
            g.state.screen = GameScreen.LEVEL_SELECT
            return

        if "help" in btns and btns["help"].collidepoint(pos):
            g.state.screen = GameScreen.HELP
            return

        if "settings" in btns and btns["settings"].collidepoint(pos):
            g.state.screen = GameScreen.SETTINGS
            return

        weapon_map = {
            "weapon_laser": "normal",
            "weapon_shotgun": "shotgun",
            "weapon_whip": "electric whip",
        }
        for btn_key, weapon_name in weapon_map.items():
            if btn_key in btns and btns[btn_key].collidepoint(pos):
                g.player.switch_weapon(weapon_name, g.game_config["max_level_reached"])
                return

    # ------------------------------------------------------------------
    # Menu
    # ------------------------------------------------------------------

    def _handle_menu(self, event: pygame.event.Event) -> None:
        g = self.game
        difficulty_keys = {
            pygame.K_1: 1,
            pygame.K_2: 2,
            pygame.K_3: 3,
        }
        if event.key in difficulty_keys:
            g.state.difficulty = difficulty_keys[event.key]
            g.state.level_mode = False
            g.state.screen = GameScreen.PLAYING
            g.state.show_menu = False
            g.start_round()
        elif event.key == pygame.K_4 and g.game_config["unlock_impossible"]:
            g.state.difficulty = 4
            g.state.level_mode = False
            g.state.screen = GameScreen.PLAYING
            g.state.show_menu = False
            g.start_round()
        elif event.key == pygame.K_l:
            g.state.level_mode = True
            g.state.current_level_page = 0
            g.state.screen = GameScreen.LEVEL_SELECT
        elif event.key == pygame.K_h:
            g.state.screen = GameScreen.HELP
        elif event.key == pygame.K_i:
            g.state.screen = GameScreen.SETTINGS

    # ------------------------------------------------------------------
    # Level selection
    # ------------------------------------------------------------------

    def _handle_level_select(self, event: pygame.event.Event) -> None:
        g = self.game
        from space_invaders.constants import LEVELS_PER_PAGE, MAX_LEVEL_PAGES
        if event.key in (pygame.K_RIGHT, pygame.K_n):
            g.state.current_level_page = min(g.state.current_level_page + 1, MAX_LEVEL_PAGES - 1)
        elif event.key in (pygame.K_LEFT, pygame.K_p):
            g.state.current_level_page = max(g.state.current_level_page - 1, 0)
        elif event.key == pygame.K_ESCAPE:
            g.state.screen = GameScreen.MENU
        elif pygame.K_1 <= event.key <= pygame.K_9:
            selected = g.state.current_level_page * LEVELS_PER_PAGE + (event.key - pygame.K_0)
            if selected <= g.game_config["max_level_reached"]:
                g.state.level = selected
                g.state.difficulty = 2
                g.state.screen = GameScreen.PLAYING
                g.state.show_menu = False
                g.start_round()

    # ------------------------------------------------------------------
    # Gameplay
    # ------------------------------------------------------------------

    def _handle_playing(self, event: pygame.event.Event) -> None:
        g = self.game
        if event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
            g.player.shoot(g.all_sprites, g.shot_group, g.active_shots,
                           g.assets.sounds["shoot"], g.state.difficulty, g.enemy_group)
        elif event.key == pygame.K_ESCAPE:
            g.state.screen = GameScreen.QUIT_CONFIRM
        elif event.key == pygame.K_1:
            g.player.switch_weapon("normal", g.game_config["max_level_reached"])
        elif event.key == pygame.K_2:
            g.player.switch_weapon("shotgun", g.game_config["max_level_reached"])
        elif event.key == pygame.K_3:
            if (g.game_config["max_level_reached"] >= WHIP_UNLOCK_LEVEL
                    and g.player.whip_charge >= g.player.whip_charge_threshold):
                previous = g.player.current_weapon
                whip = ElectricWhip(g.player.rect.midtop, SCREEN_WIDTH, SCREEN_HEIGHT)
                g.all_sprites.add(whip)
                g.assets.sounds["shoot"].play(maxtime=0, fade_ms=0)
                g.player.whip_charge = 0
                g.player.current_weapon = previous

    # ------------------------------------------------------------------
    # Dialogs
    # ------------------------------------------------------------------

    def _handle_quit_confirm(self, event: pygame.event.Event) -> None:
        g = self.game
        if event.key in (pygame.K_j, pygame.K_y):
            check_and_update_highscore(
                g.state.score, g.state.difficulty, g.high_scores,
                g.state.level, g.state.level_mode)
            g.state.screen = GameScreen.MENU
            g.state.show_menu = True
        elif event.key in (pygame.K_n, pygame.K_ESCAPE):
            g.state.screen = GameScreen.PLAYING

    def _handle_game_over(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_RETURN:
            self.game.state.screen = GameScreen.MENU
            self.game.state.show_menu = True

    def _handle_level_complete(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_RETURN:
            self.game.state.screen = GameScreen.PLAYING
            self.game.start_round()

    def _handle_help(self, event: pygame.event.Event) -> None:
        g = self.game
        from space_invaders.constants import HELP_SCROLL_SPEED
        if event.key in (pygame.K_ESCAPE, pygame.K_h):
            g.state.screen = GameScreen.MENU
            g.state.help_scroll_y = 0
        elif event.key == pygame.K_DOWN:
            g.state.help_scroll_y = min(
                g.state.help_scroll_y + HELP_SCROLL_SPEED,
                max(0, g.renderer.help_content_height - (int(SCREEN_HEIGHT * 0.8) - 100)))
        elif event.key == pygame.K_UP:
            g.state.help_scroll_y = max(0, g.state.help_scroll_y - HELP_SCROLL_SPEED)

    def _handle_settings(self, event: pygame.event.Event) -> None:
        g = self.game
        if event.key in (pygame.K_ESCAPE, pygame.K_i):
            g.state.screen = GameScreen.MENU
        elif event.key == pygame.K_1:
            g.state.sound_volume = max(0.0, g.state.sound_volume - 0.1)
            g.assets.apply_volumes(g.state.sound_volume, g.state.music_volume)
            g.game_config["sound_volume"] = g.state.sound_volume
            save_config(g.game_config)
        elif event.key == pygame.K_2:
            g.state.sound_volume = min(1.0, g.state.sound_volume + 0.1)
            g.assets.apply_volumes(g.state.sound_volume, g.state.music_volume)
            g.game_config["sound_volume"] = g.state.sound_volume
            save_config(g.game_config)
        elif event.key == pygame.K_3:
            g.state.music_volume = max(0.0, g.state.music_volume - 0.01)
            g.assets.apply_volumes(g.state.sound_volume, g.state.music_volume)
            g.game_config["music_volume"] = g.state.music_volume
            save_config(g.game_config)
        elif event.key == pygame.K_4:
            g.state.music_volume = min(0.2, g.state.music_volume + 0.01)
            g.assets.apply_volumes(g.state.sound_volume, g.state.music_volume)
            g.game_config["music_volume"] = g.state.music_volume
            save_config(g.game_config)
        elif event.key == pygame.K_5:
            g.state.mouse_control = not g.state.mouse_control
            g.game_config["mouse_control"] = g.state.mouse_control
            save_config(g.game_config)
