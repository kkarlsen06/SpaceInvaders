"""Main renderer that dispatches to screen-specific drawing."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from space_invaders.constants import Colors, SCREEN_HEIGHT, SCREEN_WIDTH
from space_invaders.state import GameScreen
from space_invaders.ui.animation import UITransitionManager
from space_invaders.ui.draw_utils import draw_vignette
from space_invaders.ui.menu import draw_menu
from space_invaders.ui.hud import draw_hud
from space_invaders.ui.dialogs import (
    draw_game_over,
    draw_help,
    draw_level_complete,
    draw_level_select,
    draw_quit_confirm,
    draw_settings,
)

if TYPE_CHECKING:
    from space_invaders.game import Game

# Dialog screens that get slide-up animations
_DIALOG_SCREENS = {
    GameScreen.GAME_OVER: "game_over_slide",
    GameScreen.LEVEL_COMPLETE: "level_complete_slide",
    GameScreen.QUIT_CONFIRM: "quit_confirm_slide",
}


class Renderer:
    """Orchestrates all drawing based on current game screen."""

    def __init__(self, game: Game) -> None:
        self.game = game
        self.help_content_height = 800
        self.transitions = UITransitionManager()
        self._last_screen: GameScreen | None = None

    def draw(self) -> None:
        g = self.game
        screen = g.state.screen

        # Update mouse position for hover effects
        g.state.mouse_pos = pygame.mouse.get_pos()

        # Trigger transitions on screen change
        if screen != self._last_screen:
            self._on_screen_change(screen)
            self._last_screen = screen

        # Background
        if screen == GameScreen.MENU and "background" in g.assets.images:
            g.screen.blit(g.assets.images["background"], (0, 0))
        else:
            g.screen.fill(Colors.BG_DEEP)

        # Stars (skip on menu which uses the background image)
        if screen != GameScreen.MENU:
            g.star_group.draw(g.screen)

        # Screen-specific drawing
        if screen == GameScreen.MENU:
            draw_menu(g)
        elif screen == GameScreen.LEVEL_SELECT:
            draw_level_select(g)
        elif screen == GameScreen.HELP:
            self.help_content_height = draw_help(g)
        elif screen == GameScreen.SETTINGS:
            draw_settings(g)
        elif screen == GameScreen.LEVEL_COMPLETE:
            self._draw_gameplay(g)
            draw_level_complete(g)
        elif screen == GameScreen.GAME_OVER:
            self._draw_gameplay(g)
            draw_game_over(g)
        elif screen == GameScreen.QUIT_CONFIRM:
            self._draw_gameplay(g)
            draw_quit_confirm(g)
        elif screen == GameScreen.PLAYING:
            self._draw_gameplay(g)

        pygame.display.flip()

    def _on_screen_change(self, new_screen: GameScreen) -> None:
        """Trigger animations when transitioning to a new screen."""
        if new_screen in _DIALOG_SCREENS:
            key = _DIALOG_SCREENS[new_screen]
            self.transitions.start_slide_up(key, offset=40, duration_ms=300)

    def _draw_gameplay(self, g: Game) -> None:
        """Draw the playing field: aim line, sprites, vignette, HUD."""
        from space_invaders.constants import DIFFICULTY_CONFIG

        diff_cfg = DIFFICULTY_CONFIG[g.state.difficulty]

        # Gradient aim line (easy/medium modes)
        if diff_cfg["show_aim_line"] and g.state.screen != GameScreen.GAME_OVER:
            aim_x = g.player.rect.centerx
            aim_surf = pygame.Surface((4, SCREEN_HEIGHT), pygame.SRCALPHA)
            for y in range(SCREEN_HEIGHT):
                dist = (SCREEN_HEIGHT - y) / SCREEN_HEIGHT
                alpha = int(40 * (1 - dist))
                if (y // 8) % 2 == 0:
                    aim_surf.set_at((1, y), (0, 180, 255, alpha))
                    aim_surf.set_at((2, y), (0, 180, 255, alpha))
            g.screen.blit(aim_surf, (aim_x - 2, 0))

        g.all_sprites.draw(g.screen)

        # Vignette for cinematic feel
        draw_vignette(g.screen)

        draw_hud(g)
